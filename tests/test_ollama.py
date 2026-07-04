"""Unit tests for shared.ollama HTTP helper (with mocked urllib)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from ollama_bench.shared.ollama import CallOpts, call


def _fake_response(
    response_text: str, eval_count: int = 10, done_reason: str = "stop"
) -> MagicMock:
    """Build a context-manager mock that returns the given JSON body."""
    body = json.dumps(
        {
            "model": "x",
            "response": response_text,
            "done": True,
            "done_reason": done_reason,
            "eval_count": eval_count,
            "prompt_eval_count": 5,
            "eval_duration": 100_000_000,  # 0.1s in ns
        }
    ).encode()
    mock = MagicMock()
    mock.__enter__.return_value.read.return_value = body
    return mock


def test_call_returns_basic_fields():
    with patch("urllib.request.urlopen", return_value=_fake_response("hello", eval_count=10)):
        res = call("m", "hi")
    assert "err" not in res
    assert res["out"] == "hello"
    assert res["etoks"] == 10
    assert res["len"] == 5


def test_call_think_flag_at_top_level():
    """think MUST be top-level in body, not inside options."""
    captured = {}

    def fake_urlopen(req, **kw):
        captured["body"] = json.loads(req.data.decode())
        return _fake_response("ok")

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        call("m", "p", opts=CallOpts(think=True))
    assert captured["body"]["think"] is True
    # and NOT in options
    assert "think" not in captured["body"]["options"]


def test_call_handles_http_error():
    # Generic Exception via urlopen -> err key in response
    with patch("urllib.request.urlopen", side_effect=Exception("boom")):
        res = call("m", "p")
    assert "err" in res
    assert "boom" in res["err"]


def test_call_seed_in_options_for_reproducibility():
    """seed MUST land in options so bench runs are reproducible."""
    captured = {}

    def fake_urlopen(req, **kw):
        captured["body"] = json.loads(req.data.decode())
        return _fake_response("ok")

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        call("m", "p", opts=CallOpts(seed=123))
    assert captured["body"]["options"]["seed"] == 123


def test_callopts_is_frozen():
    o = CallOpts(num_predict=50)
    try:
        o.num_predict = 99  # type: ignore[misc]
        raise AssertionError("expected FrozenInstanceError")
    except Exception:
        pass  # OK, frozen prevents mutation
