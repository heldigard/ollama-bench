#!/usr/bin/env python3
"""
Heuristic quality judge for bench outputs.
Scores 0-3 per test based on domain-specific criteria.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

RESULTS = Path("/home/eldi/bench/ollama/results_triage/all.json")


def judge_improve(out: str) -> tuple[int, str]:
    """improve_1: 'fix the auth bug' → spec with GOAL/FILES/STEPS/ACCEPTANCE."""
    if not out or len(out) < 20:
        return 0, "empty/too short"
    sections = ["GOAL", "FILE", "STEP", "ACCEPT"]
    found = sum(1 for s in sections if s.lower() in out.upper())
    has_action = bool(re.search(r"\b(check|verify|read|run|test|inspect|examine|debug|reproduce|locate|find|grep|look)\b", out, re.I))
    score = 0
    if found >= 3: score += 2
    elif found >= 2: score += 1
    if has_action: score += 1
    note = f"sections_found={found}/4 actions={'yes' if has_action else 'no'}"
    return min(score, 3), note


def judge_compact(out: str) -> tuple[int, str]:
    """compact_1: session → 5-bullet handoff covering task/decisions/current/blockers/next."""
    if not out or len(out) < 30:
        return 0, "empty/too short"
    bullets = len(re.findall(r"^\s*[-•*\d]+[\.)]?\s", out, re.M))
    keys = ["task", "decision", "current", "blocker", "next"]
    found_keys = sum(1 for k in keys if k.lower() in out.lower())
    has_uv = "uv" in out.lower()
    has_conftest = "conftest" in out.lower()
    score = 0
    if bullets >= 3: score += 1
    if found_keys >= 4: score += 1
    if has_uv and has_conftest: score += 1  # preserved key entities
    note = f"bullets={bullets} keys_found={found_keys}/5 entities_uv={has_uv} conftest={has_conftest}"
    return min(score, 3), note


def judge_code(out: str) -> tuple[int, str]:
    """code_1: validate_email stdlib only, handle None/empty/ws, 3 lines."""
    if not out:
        return 0, "empty"
    has_def = "def validate_email" in out
    has_re_or_email = bool(re.search(r"\bre\.|email\.", out))
    handles_none = bool(re.search(r"\bNone\b|not\s+\w|is\s+None", out))
    short_enough = out.count("\n") <= 10  # allow some leniency
    no_external = not bool(re.search(r"\bimport\s+(?!re|email|sys|os|string)\w", out))
    score = 0
    if has_def: score += 1
    if has_re_or_email: score += 1
    if handles_none: score += 1
    note = f"def={has_def} stdlib={has_re_or_email} none={handles_none} no_ext={no_external} lines~={out.count(chr(10))}"
    return min(score, 3), note


def judge_reason(out: str) -> tuple[int, str]:
    """reason_1: A>B, B>C, C=D-2, D=10 → ANSWER: <number>. A>8 so any number >8."""
    if not out:
        return 0, "empty"
    # Expected: C = 8, B > 8, A > B (could be 9 or "any > 8" or similar)
    has_answer_format = bool(re.search(r"ANSWER:\s*\S", out, re.I))
    steps = len(re.findall(r"step\s*\d|^\s*\d+[\.)]\s|^[-*]\s", out, re.M | re.I))
    mentions_8 = bool(re.search(r"\b8\b", out))
    score = 0
    if has_answer_format: score += 2
    if steps >= 1: score += 1
    if mentions_8: score += 0  # not strictly required for high score
    note = f"answer_fmt={has_answer_format} steps={steps} has_8={mentions_8}"
    return min(score, 3), note


JUDGES = {
    "improve": judge_improve,
    "compact": judge_compact,
    "code": judge_code,
    "reason": judge_reason,
}


def main():
    if not RESULTS.exists():
        print(f"ERR: {RESULTS} not found")
        sys.exit(1)
    data = json.loads(RESULTS.read_text())
    print(f"Loaded {len(data)} results\n")

    # Group by model
    by_model: dict[str, list[dict]] = {}
    for r in data:
        by_model.setdefault(r["model"], []).append(r)

    rows = []
    for model, rs in by_model.items():
        ok = [r for r in rs if r["status"] == "ok"]
        if not ok:
            rows.append({"model": model, "q_score": 0, "n_ok": 0, "speed": 0, "vram": 0, "details": "all failed"})
            continue
        scores = []
        details = []
        for r in ok:
            j = JUDGES.get(r["domain"])
            if j:
                s, note = j(r.get("output", ""))
                scores.append(s)
                details.append(f"{r['test_id']}={s}({note[:40]})")
        avg_quality = sum(scores) / len(scores) if scores else 0
        # Quality-normalized speed (tok/s * quality^2 to penalize bad quality heavily)
        speed = sum(r["tok_per_s"] for r in ok) / len(ok)
        vram = max(r["gpu_mem_peak_mib"] for r in ok)
        rows.append({
            "model": model,
            "q_score": round(avg_quality, 2),
            "n_ok": len(ok),
            "speed": round(speed, 1),
            "vram": vram,
            "composite": round(speed * avg_quality ** 2 / 10, 2),
            "details": " | ".join(details),
        })

    rows.sort(key=lambda r: r["composite"], reverse=True)
    print(f"{'model':<58} {'Q':>5} {'tok/s':>6} {'vram':>6} {'COMP':>6}")
    print("=" * 90)
    for r in rows:
        print(f"{r['model'][:57]:<58} {r['q_score']:>5} {r['speed']:>6} {r['vram']:>6} {r['composite']:>6}")

    print("\n\nDETAILED SCORES:")
    for r in rows:
        print(f"\n{r['model']}  (Q={r['q_score']}, {r['speed']} tok/s, {r['vram']} MiB)")
        print(f"  {r['details']}")

    # Save
    out = Path("/home/eldi/bench/ollama/judged.json")
    out.write_text(json.dumps(rows, indent=2))
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()