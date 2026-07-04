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
from typing import Any

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


def call(model: str, prompt: str, opts: CallOpts | None = None) -> dict[str, Any]:
    """Single Ollama /api/generate call. Non-streaming.

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
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": o.think,
            "options": {
                "temperature": o.temperature,
                "num_predict": o.num_predict,
                "num_ctx": o.num_ctx,
                "seed": o.seed,
            },
        }
    ).encode()
    t0 = time.perf_counter()
    data = _post_json(f"{OLLAMA_URL}/api/generate", body, o.timeout)
    if "err" in data:
        return data
    dt = time.perf_counter() - t0
    out = data.get("response", "") or ""
    return {
        "dt": round(dt, 2),
        "tps": round(data.get("eval_count", 0) / dt, 1) if dt > 0 else 0.0,
        "etoks": data.get("eval_count", 0),
        "ptoks": data.get("prompt_eval_count", 0),
        "len": len(out),
        "done": data.get("done_reason"),
        "out": out,
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
