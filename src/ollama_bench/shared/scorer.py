"""Scoring rubrics: leak detection, tps bonus, structural scoring.

Single registry for all features. Per-task scoring is in the feature's
PROMPTS['scorer'] callback; this module provides the building blocks.
"""
from __future__ import annotations

import re
from collections.abc import Callable

# Leak patterns. Match case-insensitively.
LEAK_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"<think>", "think_tag"),
    (r"</think>", "think_tag_close"),
    (r"thinking process[: ]", "thinking_process"),
    (r"as an ai", "refusal_pattern"),
    (r"i cannot", "refusal_pattern"),
    (r"i'm having an issue", "stuck_response"),
)

# Think-strip regex: matched-pair OR orphan <think>...
THINK_RE = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)


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


def structural_score(out: str, expected_sections: tuple[str, ...] = (), must_have: tuple[str, ...] = ()) -> float:
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
