"""Scoring rubrics: leak detection, tps bonus, structural scoring.

Single registry for all features. Per-task scoring is in the feature's
PROMPTS['scorer'] callback; this module provides the building blocks.
"""

from __future__ import annotations

import re
from collections.abc import Callable

# Leak patterns. Match case-insensitively. These cover thinking-trace leaks
# (the hard-disqualify case) AND overt refusal/stuck patterns. Conservative:
# avoids bare "i can't" (too broad — false-positives legit code summaries).
LEAK_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"<think>", "think_tag"),
    (r"</think>", "think_tag_close"),
    # Structured-reasoning trace tags (some Qwen/DeepSeek/GPT-OSS variants).
    (r"<reasoning>", "reasoning_tag"),
    (r"<reflection>", "reflection_tag"),
    (r"<output>", "output_tag"),
    # Llama-4 / Gemma-4 abliterated turn-token leak (e.g. Huihui merges emit
    # `<|channel|>thought<|channel|>` in the answer field). Documented gap in
    # ~/prompt-improve/.memory-bank/REFERENCE.md — deep_bench missed it.
    (r"<\|channel\|>", "channel_token"),
    # Visible thinking prefixes (model narrating its chain-of-thought).
    (r"thinking process[: ]", "thinking_process"),
    (r"let me think[: ]", "thinking_prefix"),
    # Refusal / stuck patterns.
    (r"as an ai", "refusal_pattern"),
    (r"as a language model", "refusal_pattern"),
    (r"i cannot", "refusal_pattern"),
    (r"i'm just an ai", "refusal_pattern"),
    (r"i'm unable to", "refusal_pattern"),
    (r"i am unable to", "refusal_pattern"),
    (r"i'm having an issue", "stuck_response"),
)

# Think-strip regex: matched-pair OR orphan <think>...
THINK_RE = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)
# Reasoning-trace tags from structured-reasoning models (Qwen3/DeepSeek-R1
# distills/GPT-OSS/LFM). Stripped as matched-pair OR orphan, DOTALL.
REASONING_RE = re.compile(r"<reasoning>.*?(</reasoning>|$)", re.DOTALL)
REFLECTION_RE = re.compile(r"<reflection>.*?(</reflection>|$)", re.DOTALL)
# `<output>...</output>` wrappers: UNWRAP (keep inner content), don't drop.
OUTPUT_WRAP_RE = re.compile(r"<output>(.*?)</output>", re.DOTALL | re.IGNORECASE)

# Leak tags that can be SALVAGED by stripping (thinking traces). A model whose
# ONLY leaks are strippable is still benchable on the cleaned answer. Refusal
# leaks (as an ai, i cannot, ...) are NOT strippable — the answer itself is the
# refusal, so stripping cannot recover a useful response.
STRIPPABLE_TAGS: frozenset[str] = frozenset(
    {
        "think_tag",
        "think_tag_close",
        "reasoning_tag",
        "reflection_tag",
        "thinking_process",
        "thinking_prefix",
        "output_tag",
        "channel_token",
    }
)


def detect_leaks(text: str) -> list[str]:
    """Return list of leak tags found in text. Empty list = clean."""
    if not text:
        return []
    leaks: list[str] = []
    L = text.lower()
    for pat, tag in LEAK_PATTERNS:
        if re.search(pat, L):
            leaks.append(tag)
    return leaks


def strip_think(text: str) -> str:
    """Strip <think>...</think> blocks (matched OR orphan)."""
    return THINK_RE.sub("", text).strip()


def strip_reasoning(text: str) -> str:
    """Strip ALL reasoning-trace blocks and unwrap <output> wrappers.

    Removes <think>, <reasoning>, <reflection> (matched-pair or orphan), then
    unwraps <output>...</output> (keeps inner content). Use this to salvage
    thinking-leak models: score the CLEANED answer, not the raw trace.

    Idempotent on clean text (no-op if no tags present).
    """
    if not text:
        return ""
    out = THINK_RE.sub("", text)
    out = REASONING_RE.sub("", out)
    out = REFLECTION_RE.sub("", out)
    # Unwrap <output>...</output> (may be multiple). Keep inner text.
    out = OUTPUT_WRAP_RE.sub(r"\1", out)
    return out.strip()


def leaks_are_strippable(leaks: list[str]) -> bool:
    """True if EVERY leak tag is a thinking-trace tag (no refusals).

    A model whose leaks are all strippable can be salvaged via strip_reasoning.
    A refusal leak means the answer itself is useless — not salvageable.
    """
    return bool(leaks) and all(tag in STRIPPABLE_TAGS for tag in leaks)


def structural_score(
    out: str, expected_sections: tuple[str, ...] = (), must_have: tuple[str, ...] = ()
) -> float:
    """Award points per section / keyword present. Range 0-10."""
    s = 0.0
    L = out.lower()
    for sec in expected_sections:
        if sec.lower() in L:
            s += 2.0
    for kw in must_have:
        if kw.lower() in L:
            s += 1.5
    return min(s, 10.0)


def quality_score(out: str, keywords: tuple[str, ...] = ()) -> float:
    """Award 2 points per keyword present. Range 0-10."""
    s = 0.0
    L = out.lower()
    for kw in keywords:
        if kw.lower() in L:
            s += 2.0
    return min(s, 10.0)


def tps_bonus(tps: float, cap: float = 3.0) -> float:
    """Bonus for throughput, capped. Adds cap at tps=cap*15."""
    return min(tps / 15.0, cap)


def first_pass_score(task: str, res: dict, budget: int) -> float:
    """First-pass scoring used by smoke + deep + multi_domain.

    Range roughly -10 to +10. Saturates at 7.0 for fast+clean responses —
    use tie_break for discrimination when many models saturate.
    """
    if "err" in res:
        return -100.0
    out = res["out"]
    L = out.lower()
    s = 0.0
    if "think>" in L or "thinking process" in L:
        s -= 5
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if res.get("done") == "length" and res.get("etoks", 0) >= 190:
        s -= 2
    if not out.strip():
        s -= 10
    wc = len(out.split())
    if wc <= budget:
        s += 2
    elif wc <= budget * 1.5:
        s += 1
    s += min(res.get("tps", 0) / 10.0, 5.0)
    if wc > budget * 2:
        s -= 3
    return round(s, 2)


def tie_break_score(res: dict, scorer: Callable[[str], float], budget: int) -> float:
    """Tie-break scoring: structural + leak penalties + tps bonus, no cap.

    Range roughly -10 to +15. Used when first_pass saturates.
    """
    if "err" in res:
        return -100.0
    out = res["out"]
    L = out.lower()
    s = 0.0
    if "think>" in L or "thinking process" in L:
        s -= 8
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if res.get("done") == "length" and res.get("len", 0) > budget * 2:
        s -= 5
    if not out.strip():
        s -= 10
    s += scorer(out)
    s += tps_bonus(res.get("tps", 0), cap=3.0)
    return round(s, 2)
