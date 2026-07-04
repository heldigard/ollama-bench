"""Unit tests for smoke slice — uses mocked Ollama."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from ollama_bench.features.smoke.command import cmd_smoke, smoke_one


def _fake_response(response_text: str) -> MagicMock:
    body = json.dumps({
        "model": "x", "response": response_text, "done": True,
        "done_reason": "stop", "eval_count": 10, "prompt_eval_count": 5,
        "eval_duration": 100_000_000,
    }).encode()
    mock = MagicMock()
    mock.__enter__.return_value.read.return_value = body
    return mock


def test_smoke_one_clean():
    with patch("urllib.request.urlopen", return_value=_fake_response("A list is mutable.")):
        r = smoke_one("m1")
    assert r["name"] == "m1"
    assert r["status"] == "ok"
    assert r["etoks"] == 10


def test_smoke_one_leak():
    leak = "<think>thinking</think>actual answer"
    with patch("urllib.request.urlopen", return_value=_fake_response(leak)):
        r = smoke_one("m2")
    assert r["status"].startswith("leak:")


def test_cmd_smoke_writes_tsv(tmp_path):
    fake = MagicMock()
    fake.__enter__.return_value.read.return_value = json.dumps(
        {"model": "x", "response": "clean", "done": True,
         "done_reason": "stop", "eval_count": 5, "eval_duration": 100_000_000}
    ).encode()

    args = type("A", (), {"models": ["m1"], "output": str(tmp_path / "out.tsv")})()
    with patch("urllib.request.urlopen", return_value=fake):
        rc = cmd_smoke(args)
    assert rc == 0
    assert (tmp_path / "out.tsv").exists()
    content = (tmp_path / "out.tsv").read_text()
    assert "m1" in content
    assert "ok" in content
