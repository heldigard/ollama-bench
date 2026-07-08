"""Unit tests for smoke slice — uses mocked Ollama."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from ollama_bench.features.smoke.command import cmd_smoke, smoke_one


def _fake_response(response_text: str) -> MagicMock:
    body = json.dumps(
        {
            "model": "x",
            "response": response_text,
            "done": True,
            "done_reason": "stop",
            "eval_count": 10,
            "prompt_eval_count": 5,
            "eval_duration": 100_000_000,
        }
    ).encode()
    mock = MagicMock()
    mock.read.return_value = body  # non-`with` path (_post_json does r.read())
    mock.__enter__.return_value.read.return_value = body  # legacy `with` path
    return mock


def test_smoke_one_clean():
    with patch("urllib.request.urlopen", return_value=_fake_response("A list is mutable.")):
        r = smoke_one("m1")
    assert r["name"] == "m1"
    assert r["status"] == "ok"
    assert r["strippable"] == "0"
    assert r["etoks"] == 10


def test_smoke_one_leak_strippable():
    """A pure thinking-trace leak is flagged strippable (salvageable via --strip)."""
    leak = "<think>thinking</think>actual answer"
    with patch("urllib.request.urlopen", return_value=_fake_response(leak)):
        r = smoke_one("m2")
    assert r["status"].startswith("leak:")
    assert r["strippable"] == "1"


def test_smoke_one_refusal_not_strippable():
    """A refusal leak is NOT strippable (the answer itself is the refusal)."""
    refusal = "As an AI, I cannot answer that."
    with patch("urllib.request.urlopen", return_value=_fake_response(refusal)):
        r = smoke_one("m3")
    assert r["status"].startswith("leak:")
    assert r["strippable"] == "0"


def test_cmd_smoke_writes_tsv(tmp_path):
    fake = MagicMock()
    fake.__enter__.return_value.read.return_value = json.dumps(
        {
            "model": "x",
            "response": "clean",
            "done": True,
            "done_reason": "stop",
            "eval_count": 5,
            "eval_duration": 100_000_000,
        }
    ).encode()
    fake.read.return_value = fake.__enter__.return_value.read.return_value

    args = type("A", (), {"models": ["m1"], "output": str(tmp_path / "out.tsv")})()
    with patch("urllib.request.urlopen", return_value=fake):
        rc = cmd_smoke(args)
    assert rc == 0
    assert (tmp_path / "out.tsv").exists()
    content = (tmp_path / "out.tsv").read_text()
    assert "m1" in content
    assert "ok" in content


def test_is_embedding_model():
    from ollama_bench.features.smoke.command import _is_embedding_model

    assert _is_embedding_model("nomic-embed-text:latest")
    assert _is_embedding_model("embeddinggemma:latest")
    assert _is_embedding_model("qwen3-embedding:4b")
    assert _is_embedding_model("bge-m3:latest")
    assert not _is_embedding_model("qwen3.5:4b")
    assert not _is_embedding_model("MobiusDevelopment/gemma-4-12B")


def test_cmd_smoke_skips_embeddings(tmp_path):
    """Embedding models must NOT appear in smoke output (they can't /api/generate)."""
    fake = MagicMock()
    fake.__enter__.return_value.read.return_value = json.dumps(
        {
            "model": "x",
            "response": "clean",
            "done": True,
            "done_reason": "stop",
            "eval_count": 5,
            "eval_duration": 100_000_000,
        }
    ).encode()
    fake.read.return_value = fake.__enter__.return_value.read.return_value
    args = type(
        "A",
        (),
        {
            "models": ["qwen3.5:4b", "nomic-embed-text:latest", "embeddinggemma:latest"],
            "output": str(tmp_path / "out.tsv"),
        },
    )()
    with patch("urllib.request.urlopen", return_value=fake):
        rc = cmd_smoke(args)
    assert rc == 0
    content = (tmp_path / "out.tsv").read_text()
    assert "qwen3.5:4b" in content
    assert "nomic-embed-text" not in content
    assert "embeddinggemma" not in content
