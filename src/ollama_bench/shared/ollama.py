"""HTTP call helper for Ollama.

Single path for ALL features. Critical invariants:

- `think` is TOP-LEVEL in the request body (not inside `options`). Putting it
  inside `options` is silently ignored — qwen3.x and gemma4 still emit the
  thinking trace in the response field. See shared/scorer.detect_leaks() for
  the matching consumer side.

- Default `num_ctx=4096` to keep responses cheap; large contexts OOM.
"""

# vs-soft-allow  — single-responsibility HTTP helper; the multi-line request-body
# dict literal in call() inflates lexical indentation without adding control-flow
# nesting (it's an expression, not a block). _post_json keeps real depth ≤3.

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Literal

from ollama_bench.shared.config import OLLAMA_URL, TIMEOUT_DEFAULT


@dataclass(frozen=True)
class CallOpts:
    """HTTP-call options for Ollama. Frozen so it's hashable / safe to share."""

    timeout: int = TIMEOUT_DEFAULT
    num_predict: int = 200
    num_ctx: int = 4096
    temperature: float = 0.2
    seed: int = 42  # pinned for reproducible bench runs (deterministic ranking)
    think: bool = False  # TOP-LEVEL; moving into options is silently ignored
    api: Literal["generate", "chat", "chat-fallback"] = "generate"
    system: str = ""
    retries: int = 2  # transient-load retries (timeout/5xx); 0 disables for bench runs


def get_models() -> list[dict[str, Any]]:
    """Return raw /api/tags response list. Each entry has name, size, etc."""
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=10) as r:
        data = json.load(r)
    return list(data.get("models", []))


def get_model_names() -> list[str]:
    return [m["name"] for m in get_models()]


def _post_json(url: str, body: bytes, timeout: int) -> dict[str, Any]:
    """POST `body` to `url`, return parsed JSON dict (or {"err": ...} on failure).

    Shared by call() + embed(). Non-`with` pattern (urlopen + close in finally)
    keeps nesting depth ≤2 so the vertical-slice guard passes; both call sites
    share one error-handling path (DRY). The success dict is the raw Ollama
    response; callers check `if "err" in data` before reading fields.
    """
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        return {"err": f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"err": f"{type(e).__name__}: {str(e)[:200]}"}
    try:
        return json.loads(r.read())
    finally:
        r.close()


def _request_body(model: str, prompt: str, o: CallOpts, api: str) -> dict[str, Any]:
    options = {
        "temperature": o.temperature,
        "num_predict": o.num_predict,
        "num_ctx": o.num_ctx,
        "seed": o.seed,
    }
    if api == "chat":
        messages = []
        if o.system:
            messages.append({"role": "system", "content": o.system})
        messages.append({"role": "user", "content": prompt})
        return {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": o.think,
            "options": options,
        }
    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": o.think,
        "options": options,
    }
    if o.system:
        body["system"] = o.system
    return body


def _template_parser_failure(data: dict[str, Any]) -> bool:
    error = str(data.get("err", "")).lower()
    return "http 400" in error and (
        "unable to generate parser for this template" in error
        or "automatic parser generation failed" in error
    )


# Transient-load retry. A model that fails with HTTP/timeout/load contention
# during a big bench run (empty `out`, no `etoks`) used to score -100 and could
# dethrone a healthy champion — see the 2026-07-13 Qwythos codeq_sum incident
# (worked when called in isolation, returned empty across all deep prompts
# under GPU contention). Retrying transient errors here, in the single HTTP
# path, protects every feature at once. Permanent client errors (HTTP 4xx:
# bad model tag, malformed request) are NOT retried — they cannot succeed.
_TRANSIENT_BACKOFF_SEC = (5.0, 15.0)


def _is_transient(err: str) -> bool:
    """Client errors (HTTP 4xx) are permanent; everything else (5xx, timeouts,
    connection resets, model-load races, OOM) is worth one more attempt."""
    return not err.startswith("HTTP 4")


def call(model: str, prompt: str, opts: CallOpts | None = None) -> dict[str, Any]:
    """Single protocol-aware Ollama completion with transient-load retry.

    Wraps :func:`_call_once`. On a transient error (HTTP 5xx / timeout /
    load-race) it retries up to ``opts.retries`` times (default 2) with backoff
    before returning the final ``{"err": ...}``. Permanent 4xx errors return
    immediately. Bench runs pass ``retries=0`` so a model failing consistently
    under GPU contention scores -100 fast instead of stalling every prompt.
    """
    o = opts or CallOpts()
    last: dict[str, Any] = {}
    for attempt in range(o.retries + 1):
        last = _call_once(model, prompt, o)
        if "err" not in last or not _is_transient(last["err"]):
            return last
        if attempt < o.retries:
            time.sleep(_TRANSIENT_BACKOFF_SEC[min(attempt, len(_TRANSIENT_BACKOFF_SEC) - 1)])
    return last


def _call_once(model: str, prompt: str, opts: CallOpts | None = None) -> dict[str, Any]:
    """Single protocol-aware Ollama completion. Non-streaming.

    Returns a dict with keys:
      - dt: wall time in seconds
      - tps: tokens/sec (eval_count / dt, 0 if dt==0)
      - etoks: eval_count
      - ptoks: prompt_eval_count
      - len: response length in chars
      - done: done_reason from Ollama
      - out: response text (possibly empty)
      - err: error string if HTTP/timeout failure (no other keys)

    The `think` flag is TOP-LEVEL. Don't move it into options.
    """
    o = opts or CallOpts()
    requested_api = "chat" if o.api in {"chat", "chat-fallback"} else "generate"
    t0 = time.perf_counter()
    body = json.dumps(_request_body(model, prompt, o, requested_api)).encode()
    data = _post_json(f"{OLLAMA_URL}/api/{requested_api}", body, o.timeout)
    protocol = requested_api
    if o.api == "chat-fallback" and _template_parser_failure(data):
        body = json.dumps(_request_body(model, prompt, o, "generate")).encode()
        data = _post_json(f"{OLLAMA_URL}/api/generate", body, o.timeout)
        protocol = "generate-fallback"
    if "err" in data:
        return data
    dt = time.perf_counter() - t0
    if protocol == "chat":
        message = data.get("message", {})
        out = message.get("content", "") if isinstance(message, dict) else ""
    else:
        out = data.get("response", "") or ""
    return {
        "dt": round(dt, 2),
        "tps": round(data.get("eval_count", 0) / dt, 1) if dt > 0 else 0.0,
        "etoks": data.get("eval_count", 0),
        "ptoks": data.get("prompt_eval_count", 0),
        "len": len(out),
        "done": data.get("done_reason"),
        "out": out,
        "protocol": protocol,
    }


def embed(model: str, text: str, timeout: int = TIMEOUT_DEFAULT) -> dict[str, Any]:
    """Single Ollama /api/embeddings call. Non-streaming.

    Returns:
      - vec: list[float] (the embedding)
      - dt: wall seconds
      - err: error string on failure (no other keys)

    Uses the legacy /api/embeddings endpoint (stable across Ollama versions,
    works for nomic-embed-text, embeddinggemma, bge-m3). num_ctx is not set —
    embedders use their own context window.
    """
    body = json.dumps({"model": model, "prompt": text}).encode()
    t0 = time.perf_counter()
    data = _post_json(f"{OLLAMA_URL}/api/embeddings", body, timeout)
    if "err" in data:
        return data
    return {"vec": data.get("embedding") or [], "dt": round(time.perf_counter() - t0, 2)}
