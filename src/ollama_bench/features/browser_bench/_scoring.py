"""Scoring + Ollama client for browser-model-bench.

T1-T4 scoring functions + ``call_ollama`` HTTP client. Imports ground truth
(``GT``, ``CLASS_GT``, ``ALL_CLASSES``, ``T3_CHANGE_WORDS``) from ``_bench_data``;
imports nothing from ``_bench_fixtures`` (Pillow stays lazy).
"""

from __future__ import annotations

import base64
import json
import re
import time
import urllib.request
from dataclasses import dataclass

from ollama_bench.features.browser_bench._data import ALL_CLASSES, CLASS_GT, GT, T3_CHANGE_WORDS

__all__ = [
    "OLLAMA_URL",
    "OllamaOptions",
    "call_ollama",
    "score_t1",
    "score_t2",
    "score_t3",
    "score_t4",
]

OLLAMA_URL = "http://localhost:11434"


@dataclass(frozen=True)
class OllamaOptions:
    """Per-call Ollama tuning; defaults match the prior call_ollama signature."""

    temperature: float = 0.2
    num_predict: int = 512
    timeout: float = 60.0


# =============================================================================
# Scoring — rigorous
# =============================================================================
def score_t1(content: str, gt_key: str) -> dict:
    blob = content.lower()
    gt = GT[gt_key]
    must = gt["must_contain"]
    must_not = gt["must_not"]
    if not must:
        # chart_pie: score by absence of hallucination only
        hallucinated = [w for w in must_not if w in blob]
        return {
            "recall": "n/a",
            "precision": "n/a",
            "hallucination_rate": round(len(hallucinated) / max(len(must_not), 1), 2),
            "hallucinated_words": hallucinated,
            "perfect": not hallucinated,
        }
    hits = sum(1 for w in must if w in blob)
    recall = hits / len(must)
    hallucinated = [w for w in must_not if w in blob]
    hall_rate = len(hallucinated) / max(len(must_not), 1) if must_not else 0
    return {
        "recall": round(recall, 2),
        "hallucinated_words": hallucinated,
        "hallucination_rate": round(hall_rate, 2),
        "perfect": recall == 1.0 and not hallucinated,
        "score": round((recall + (1 - hall_rate)) / 2, 2),
    }


def score_t2(content: str, gt_key: str) -> dict:
    expected = CLASS_GT[gt_key]
    blob = content.lower().strip()
    picked = next((c for c in ALL_CLASSES if c in blob), None)
    return {"expected": expected, "picked": picked, "ok": picked == expected}


def score_t3(content: str, scenario: str) -> dict:
    expected_words = T3_CHANGE_WORDS[scenario]
    blob = content.lower()
    hits = sum(1 for w in expected_words if w in blob)
    return {"hits": hits, "of": len(expected_words), "score": round(hits / len(expected_words), 2)}


_T4_EXPECT: dict[str, tuple[str, set[str | None]]] = {
    "click": ("click", {"e8", "e11"}),
    "fill": ("fill", {"e3"}),
    "scroll": ("scroll", {"e9"}),  # scroll paragraph into view
    "wait": ("wait", {"e3", "e4"}),  # wait progressbar / status gone
    "eval": ("eval", {None}),  # any eval is fine (no ref)
    "recovery": ("click", {"e7"}),
}


def score_t4(content: str, scenario: str) -> dict:
    """Expected action + expected ref range per scenario."""
    try:
        m = re.search(r"\{[^{}]+\}", content)
        call = json.loads(m.group(0)) if m else {}
    except (json.JSONDecodeError, AttributeError):
        call = {}
    expected_action, accepted_refs = _T4_EXPECT[scenario]
    action_ok = call.get("action") == expected_action
    ref_ok = (None in accepted_refs) or (call.get("ref") in accepted_refs)
    return {"call": call, "action_ok": action_ok, "ref_ok": ref_ok, "ok": action_ok and ref_ok}


# =============================================================================
# Ollama call
# =============================================================================
def _post_chat(payload: dict, timeout: float) -> dict:
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _decode_response(raw: dict, dt: float) -> dict:
    msg = raw.get("message", {}) or {}
    content = (msg.get("content") or "").strip()
    ed = raw.get("eval_duration", 0) / 1e9
    return {
        "content": content,
        "seconds": round(dt, 2),
        "eval_tokens": raw.get("eval_count", 0),
        "prompt_tokens": raw.get("prompt_eval_count", 0),
        "tokens_per_sec": round(raw.get("eval_count", 0) / ed, 2) if ed > 0 else 0,
    }


def call_ollama(
    model: str,
    prompt: str,
    image_bytes: bytes | None,
    options: OllamaOptions | None = None,
) -> dict:
    opts = options or OllamaOptions()
    messages: list[dict[str, object]] = [{"role": "user", "content": prompt}]
    if image_bytes is not None:
        messages[0]["images"] = [base64.b64encode(image_bytes).decode("ascii")]
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {"temperature": opts.temperature, "num_predict": opts.num_predict},
    }
    t0 = time.monotonic()
    try:
        raw = _post_chat(payload, opts.timeout)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}", "seconds": round(time.monotonic() - t0, 2)}
    return _decode_response(raw, time.monotonic() - t0)
