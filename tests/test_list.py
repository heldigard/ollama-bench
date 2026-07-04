"""Unit tests for list slice — warnings for incompat/leaky models."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from ollama_bench.features.list.command import _warnings_for, cmd_list


def _fake_tags_response():
    return [
        {"name": "qwen3.5:4b", "size": 3.4 * 1024**3,
         "details": {"quantization_level": "Q4_K_M"}},
        {"name": "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
         "size": 7.2 * 1024**3, "details": {"quantization_level": "Q4_0"}},
    ]


def test_warnings_empty_for_clean_model():
    assert _warnings_for("qwen3.5:4b") == []


def test_warnings_for_lfm():
    w = _warnings_for("hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M")
    assert "LEAKS_THINK" in w


def test_cmd_list_writes_tsv(tmp_path):
    body = json.dumps({"models": _fake_tags_response()}).encode()
    mock = MagicMock()
    mock.__enter__.return_value.read.return_value = body
    out = tmp_path / "list.tsv"
    args = type("A", (), {"output": str(out)})()
    with patch("urllib.request.urlopen", return_value=mock):
        rc = cmd_list(args)
    assert rc == 0
    content = out.read_text()
    assert "qwen3.5:4b" in content
    assert "Mobius" in content


def test_cmd_list_to_stdout(capsys):
    body = json.dumps({"models": _fake_tags_response()}).encode()
    mock = MagicMock()
    mock.__enter__.return_value.read.return_value = body
    args = type("A", (), {"output": None})()
    with patch("urllib.request.urlopen", return_value=mock):
        rc = cmd_list(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "qwen3.5:4b" in captured.out
    assert "Installed Ollama models" in captured.out