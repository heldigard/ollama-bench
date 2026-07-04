"""judge - LLM-as-judge helpers for benchmarking."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Quality rubric - keywords we want to see in a "good" output per task.
RUBRIC_KEYWORDS: dict[str, list[str]] = {
    "improve": ["GOAL", "STEP", "FILE", "ACCEPTANCE", "ASSUMPTION"],
    "codeq_sum": ["function", "method", "class", "return", "does"],
    "smart_trim": ["task", "decision", "next", "blocked", "current"],
    "web_synth": ["[1]", "[2]", "[3]", "summary", "according"],
    "code_gen": ["def ", "import", "return", "raise", "for "],
}

# Patterns that indicate a FAIL - model didn't do its job
FAIL_PATTERNS = [
    (r"i cannot", "refusal"),
    (r"i'm just an ai", "refusal"),
    (r"i don't have access", "refusal"),
    (r"as an ai language model", "refusal"),
    (r"placeholder", "stub"),
    (r"\$\{.*?\}", "unfilled_template"),
]


def judge_quality(task: str, output: str) -> dict:
    """Score 0-1 based on keyword presence + failure patterns."""
    score = 0.0
    matched: list[str] = []
    for kw in RUBRIC_KEYWORDS.get(task, []):
        if kw.lower() in output.lower():
            score += 0.15
            matched.append(kw)
    score = min(score, 1.0)
    failures: list[str] = []
    for pat, label in FAIL_PATTERNS:
        if re.search(pat, output, re.IGNORECASE):
            failures.append(label)
            score -= 0.2
    return {"score": max(score, 0.0), "matched": matched, "failures": failures}


def cmd_judge_score(args) -> int:
    """Score outputs in a JSONL file (each line has {task, output})."""
    in_path = Path(args.input)
    out_path = Path(args.output) if args.output else in_path.with_suffix(".scored.jsonl")
    n_total = n_pass = 0
    with in_path.open() as fi, out_path.open("w") as fo:
        for line in fi:
            if not line.strip():
                continue
            r = json.loads(line)
            task = r.get("task", "improve")
            output = r.get("output", "")
            verdict = judge_quality(task, output)
            verdict["model"] = r.get("model", "?")
            verdict["task"] = task
            fo.write(json.dumps(verdict) + "\n")
            n_total += 1
            if verdict["score"] >= 0.5 and not verdict["failures"]:
                n_pass += 1
    print(f"# scored {n_total}, pass-rate {n_pass}/{n_total}", file=sys.stderr)
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent):
    p = sub.add_parser("judge", parents=[parent], help="LLM-as-judge helpers.")
    sp = p.add_subparsers(dest="judge_cmd", required=True)
    sc = sp.add_parser("score", parents=[parent], help="Score outputs from JSONL.")
    sc.add_argument("-i", "--input", required=True, help="Input JSONL (task + output per line).")
    sc.add_argument("-o", "--output", help="Output JSONL.")
    sc.set_defaults(cmd=cmd_judge_score)
