#!/usr/bin/env python3
"""
Improved judge for deep bench. Recognizes markdown headers, more lenient scoring.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

RESULTS = Path("/home/eldi/bench/ollama/results_deep/all.json")

# Strip markdown formatting before pattern matching
def strip_md(s: str) -> str:
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)  # bold
    s = re.sub(r"\*([^*]+)\*", r"\1", s)      # italic
    s = re.sub(r"`([^`]+)`", r"\1", s)        # inline code
    s = re.sub(r"^#+\s*", "", s, flags=re.M)   # headers
    return s


def judge_improve(out: str) -> tuple[int, str]:
    """improve: spec with GOAL/FILES/STEPS/ACCEPTANCE sections."""
    if not out or len(out) < 30:
        return 0, "empty/too short"
    o = strip_md(out).upper()
    sections = ["GOAL", "FILE", "STEP", "ACCEPT"]
    found = sum(1 for s in sections if s in o)
    has_action = bool(re.search(r"\b(check|verify|read|run|test|inspect|examine|debug|reproduce|locate|find|grep|look|analyze|review|implement|audit|validate|create|add|edit|update|write)\b", o, re.I))
    score = 0
    if found >= 3: score += 2
    elif found >= 2: score += 1
    if has_action: score += 1
    return min(score, 3), f"sections={found}/4 action={'y' if has_action else 'n'}"


def judge_compact(out: str) -> tuple[int, str]:
    """compact: 5-bullet handoff covering task/decisions/current/blockers/next."""
    if not out or len(out) < 30:
        return 0, "empty/too short"
    bullets = len(re.findall(r"^\s*[-•*\d]+[\.)]?\s", out, re.M))
    o = strip_md(out).lower()
    keys = ["task", "decision", "current", "blocker", "next"]
    found_keys = sum(1 for k in keys if k in o)
    # Domain-specific entity preservation
    entities = ["uv", "conftest"] if "uv" in out else []
    preserved = sum(1 for e in entities if e.lower() in o)
    score = 0
    if bullets >= 3: score += 1
    if found_keys >= 4: score += 1
    if (preserved == len(entities)) or (len(entities) == 0 and found_keys >= 4): score += 1
    return min(score, 3), f"bullets={bullets} keys={found_keys}/5 ents={preserved}/{len(entities)}"


def judge_code(out: str) -> tuple[int, str]:
    """code: function present, stdlib only, handles edge cases."""
    if not out:
        return 0, "empty"
    has_def = "def validate_email" in out or "def fetch_all" in out or "def chunk_text" in out
    has_re = bool(re.search(r"\bre\.|email\.|asyncio\.|aiohttp", out))
    no_external = not bool(re.search(r"\bimport\s+(?!re|email|sys|os|string|asyncio|aiohttp|typing|functools|collections|itertools|math|json|re\.|urllib|pathlib)\w+", out))
    has_handling = bool(re.search(r"\bNone|not\s+\w|is\s+None|try:|except", out))
    has_structure = bool(re.search(r"\b(?:def|async\s+def|return|if|for|while)\b", out))
    score = 0
    if has_def: score += 1
    if has_structure and has_re: score += 1
    if has_handling and no_external: score += 1
    return min(score, 3), f"def={has_def} structure={has_structure} stdlib={no_external} handling={has_handling}"


def judge_longctx(out: str) -> tuple[int, str]:
    """longctx: comprehensive summary that preserves all key items."""
    if not out or len(out) < 100:
        return 0, "too short for comprehensive summary"
    o = strip_md(out).lower()
    items = ["loguru", "pool", "fix/payment-flake", "race", "tracing", "test_payment"]
    preserved = sum(1 for i in items if i in o)
    has_structure = bool(re.search(r"\n\s*[-•*]|\n\s*\d+\.", out))
    score = 0
    if preserved >= 5: score += 2
    elif preserved >= 3: score += 1
    if has_structure and len(out) > 300: score += 1
    return min(score, 3), f"entities_preserved={preserved}/{len(items)} structured={has_structure} len={len(out)}"


def judge_reason(out: str) -> tuple[int, str]:
    """reason: shows steps + ANSWER format + correct logic."""
    if not out:
        return 0, "empty"
    has_answer = bool(re.search(r"ANSWER:\s*\S", out, re.I))
    steps = len(re.findall(r"step\s*\d|^\s*\d+[\.)]\s|^[-*]\s", out, re.M | re.I))
    has_8 = "8" in out
    # correct: 3/(3+2+5) * 5/(3+2+5-1) = 3/10 * 5/9 = 15/90 = 1/6
    has_15_90 = "15" in out and "90" in out
    has_1_6 = bool(re.search(r"\b1/6\b|0\.1[67]|\b15/90\b", out))
    score = 0
    if has_answer: score += 1
    if steps >= 2: score += 1
    if has_15_90 or has_1_6 or has_8: score += 1  # any correct math
    return min(score, 3), f"answer_fmt={has_answer} steps={steps} math={'y' if (has_15_90 or has_1_6 or has_8) else 'n'}"


JUDGES = {
    "improve": judge_improve,
    "compact": judge_compact,
    "code": judge_code,
    "longctx": judge_longctx,
    "reason": judge_reason,
}


def main():
    if not RESULTS.exists():
        print(f"ERR: {RESULTS} not found")
        sys.exit(1)
    data = json.loads(RESULTS.read_text())
    print(f"Loaded {len(data)} results\n")

    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in data:
        by_model[r["model"]].append(r)

    # Aggregate per domain
    domain_scores: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    speed_by_model: dict[str, list[float]] = defaultdict(list)
    quality_by_model: dict[str, list[int]] = defaultdict(list)

    for r in data:
        if r["status"] != "ok":
            continue
        j = JUDGES.get(r["domain"])
        if j:
            score, note = j(r.get("output", ""))
            domain_scores[r["domain"]][r["model"]].append(score)
            quality_by_model[r["model"]].append(score)
            speed_by_model[r["model"]].append(r.get("tps", 0))

    # Per-domain ranking
    print(f"{'='*90}\nPER-DOMAIN WINNERS (highest avg quality first)\n{'='*90}")
    winners = {}
    for d in sorted(domain_scores):
        print(f"\n[{d.upper()}]")
        ranked = sorted(
            domain_scores[d].items(),
            key=lambda kv: (sum(kv[1]) / len(kv[1]), sum(speed_by_model[kv[0]]) / len(speed_by_model[kv[0]])),
            reverse=True,
        )
        for i, (m, scores) in enumerate(ranked):
            avg_q = sum(scores) / len(scores)
            avg_s = sum(speed_by_model[m]) / len(speed_by_model[m])
            star = " ★" if i == 0 else ""
            print(f"  {i+1}. {m[:55]:<55} Q={avg_q:.2f}  speed={avg_s:.1f} tok/s  ({len(scores)} tests){star}")
            if i == 0:
                winners[d] = m

    print(f"\n{'='*90}\nDOMAIN WINNERS\n{'='*90}")
    for d, m in winners.items():
        print(f"  {d:<12} → {m}")

    # Overall composite
    print(f"\n{'='*90}\nOVERALL RANKING\n{'='*90}")
    rows = []
    for m in by_model:
        qs = quality_by_model.get(m, [])
        ss = speed_by_model.get(m, [])
        avg_q = sum(qs) / len(qs) if qs else 0
        avg_s = sum(ss) / len(ss) if ss else 0
        rows.append({
            "model": m,
            "avg_quality": round(avg_q, 2),
            "avg_speed": round(avg_s, 1),
            "vram": max(r.get("vram", 0) for r in by_model[m] if r.get("vram")),
            "composite": round(avg_s * (avg_q ** 2) / 10, 2),
        })
    rows.sort(key=lambda r: r["composite"], reverse=True)
    print(f"{'model':<58} {'Q':>5} {'tok/s':>7} {'vram':>6} {'COMP':>6}")
    for r in rows:
        print(f"{r['model'][:57]:<58} {r['avg_quality']:>5} {r['avg_speed']:>7} {r['vram']:>6} {r['composite']:>6}")

    # Save
    Path("/home/eldi/bench/ollama/judged_deep.json").write_text(
        json.dumps({"winners": winners, "rows": rows}, indent=2))
    print(f"\nSaved: /home/eldi/bench/ollama/judged_deep.json")


if __name__ == "__main__":
    main()