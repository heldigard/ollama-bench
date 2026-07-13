"""Unit tests for shared.ollama HTTP helper (with mocked urllib)."""

from __future__ import annotations

import io
import json
import urllib.error
from email.message import Message
from unittest.mock import MagicMock, patch

from ollama_bench.shared.config import OLLAMA_URL
from ollama_bench.shared.ollama import CallOpts, call, unload


def _fake_response(
    response_text: str, eval_count: int = 10, done_reason: str = "stop", chat: bool = False
) -> MagicMock:
    """Build a context-manager mock that returns the given JSON body."""
    body = json.dumps(
        {
            "model": "x",
            "response": response_text,
            "message": {"role": "assistant", "content": response_text} if chat else None,
            "done": True,
            "done_reason": done_reason,
            "eval_count": eval_count,
            "prompt_eval_count": 5,
            "eval_duration": 100_000_000,  # 0.1s in ns
        }
    ).encode()
    mock = MagicMock()
    mock.read.return_value = body  # non-`with` path (_post_json does r.read())
    mock.__enter__.return_value.read.return_value = body  # legacy `with` path
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
    # Generic Exception via urlopen -> transient err -> retried, then returned.
    # Backoff patched to 0 so the test does not wait on real sleeps.
    with (
        patch("urllib.request.urlopen", side_effect=Exception("boom")),
        patch("ollama_bench.shared.ollama._TRANSIENT_BACKOFF_SEC", (0.0, 0.0)),
    ):
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


def test_call_chat_protocol_uses_messages_and_records_protocol():
    captured = {}

    def fake_urlopen(req, **kw):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode())
        return _fake_response("ok", chat=True)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        res = call("m", "p", opts=CallOpts(api="chat", system="ground it"))
    assert captured["url"].endswith("/api/chat")
    assert captured["body"]["messages"] == [
        {"role": "system", "content": "ground it"},
        {"role": "user", "content": "p"},
    ]
    assert res["out"] == "ok"
    assert res["protocol"] == "chat"


def test_call_chat_fallback_only_for_template_parser_error():
    calls = []

    def fake_post(url, body, timeout):
        calls.append(url)
        if url.endswith("/api/chat"):
            return {"err": "HTTP 400: Unable to generate parser for this template"}
        return {
            "response": "ok",
            "eval_count": 1,
            "prompt_eval_count": 1,
            "done_reason": "stop",
        }

    with patch("ollama_bench.shared.ollama._post_json", side_effect=fake_post):
        res = call("m", "p", opts=CallOpts(api="chat-fallback"))
    assert calls == [
        f"{OLLAMA_URL}/api/chat",
        f"{OLLAMA_URL}/api/generate",
    ]
    assert res["out"] == "ok"
    assert res["protocol"] == "generate-fallback"


def test_callopts_is_frozen():
    o = CallOpts(num_predict=50)
    try:
        o.num_predict = 99  # type: ignore[misc]
        raise AssertionError("expected FrozenInstanceError")
    except Exception:
        pass  # OK, frozen prevents mutation


# --- transient-load retry (2026-07-13: stop false -100 hard-DQs) ------------


def test_call_retries_transient_then_succeeds():
    """A transient error (timeout / load race) MUST be retried; the 3rd attempt
    succeeds. Regression for the Qwythos codeq_sum incident: a model that empties
    under GPU contention must not be hard-DQd when a retry would have worked."""
    responses = [
        urllib.error.URLError("timeout"),  # attempt 1: transient
        urllib.error.URLError("conn reset"),  # attempt 2: transient
        _fake_response("ok", eval_count=3),  # attempt 3: success
    ]
    with (
        patch("urllib.request.urlopen", side_effect=responses),
        patch("ollama_bench.shared.ollama._TRANSIENT_BACKOFF_SEC", (0.0, 0.0)),
    ):
        res = call("m", "p")
    assert res["out"] == "ok"
    assert res["etoks"] == 3


def test_call_no_retry_on_permanent_4xx():
    """Permanent 4xx (bad model tag / malformed request) MUST NOT be retried —
    it cannot succeed. No backoff sleep is taken."""
    http_err = urllib.error.HTTPError("u", 404, "Not Found", Message(), io.BytesIO(b"nope"))
    with (
        patch("urllib.request.urlopen", side_effect=http_err),
        patch("ollama_bench.shared.ollama.time.sleep") as mock_sleep,
    ):
        res = call("m", "p")
    assert "err" in res
    assert "HTTP 404" in res["err"]
    mock_sleep.assert_not_called()


def test_call_returns_err_after_all_retries_fail():
    """All-transient-failure returns the err after exhausting retries
    (1 initial + 2 retries = 3 attempts)."""
    with (
        patch("urllib.request.urlopen", side_effect=urllib.error.URLError("down")),
        patch("ollama_bench.shared.ollama._TRANSIENT_BACKOFF_SEC", (0.0, 0.0)),
    ):
        res = call("m", "p")
    assert "err" in res
    assert "down" in res["err"]


def test_call_retries_zero_makes_single_attempt():
    """Bench runs pass retries=0 so a model failing consistently under GPU
    contention scores fast (one attempt, no backoff) instead of stalling every
    prompt — the -100 is the diagnostic signal, not a silent hang."""
    with (
        patch("urllib.request.urlopen", side_effect=urllib.error.URLError("down")),
        patch("ollama_bench.shared.ollama.time.sleep") as mock_sleep,
    ):
        res = call("m", "p", opts=CallOpts(retries=0))
    assert "err" in res
    mock_sleep.assert_not_called()


def test_unload_posts_keep_alive_zero_best_effort():
    """unload() POSTs keep_alive=0 to /api/generate so the bench releases VRAM
    between models (2026-07-13 Qwythos contention fix). Errors are ignored."""
    captured = {}

    def fake_post(url, body, timeout):
        captured["url"] = url
        captured["body"] = json.loads(body)
        return {"err": "anything — must be ignored, not raised"}

    with patch("ollama_bench.shared.ollama._post_json", side_effect=fake_post):
        unload("mymodel")  # must not raise even though _post_json returned err
    assert captured["body"] == {"model": "mymodel", "keep_alive": 0}
    assert captured["url"].endswith("/api/generate")
