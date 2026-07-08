#!/usr/bin/env python3
"""Detect tied models from a deep-bench details JSONL for tie-break.

Reads the append-only per-case JSONL, computes each model's mean score per task,
and prints (one per line) the models within MARGIN of the per-task TOP score in
ANY task. Union across tasks. A tie is only reported when >=2 models are within
margin (a lone leader is not a tie).

Usage:
    tie_winners.py <details.jsonl> [margin=0.5]

A small margin (0.5) captures genuine near-ties without dragging in the whole
field. Raise it to tie-break a broader cluster; lower it for only exact ties.
"""

# vs-soft-allow  — single-responsibility CLI script (read JSONL -> emit winners).
from __future__ import annotations

import json
import sys
from collections import defaultdict
from typing import Any


def _parse(line: str) -> dict[str, Any] | None:
    """Parse one JSONL line; None on blank or truncated (kill-mid-write) lines."""
    line = line.strip()
    if not line:
        return None
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        return None
    return e if isinstance(e, dict) else None


def load_means(path: str) -> dict[str, dict[str, float]]:
    """Return {model: {task: mean_score}} from the per-case details JSONL."""
    per: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        for line in f:
            e = _parse(line)
            if e is None:
                continue
            model, task, score = e.get("model"), e.get("task"), e.get("score")
            if model and task and score is not None:
                per[model][task].append(float(score))
    return {m: {t: sum(v) / len(v) for t, v in ts.items()} for m, ts in per.items()}


def tied_winners(means: dict[str, dict[str, float]], margin: float) -> set[str]:
    """Models within `margin` of the top in any task, where >=2 models are near."""
    tasks = {t for ts in means.values() for t in ts}
    winners: set[str] = set()
    for t in tasks:
        ranked = {m: ts[t] for m, ts in means.items() if t in ts}
        if len(ranked) < 2:
            continue
        top = max(ranked.values())
        near = [m for m, s in ranked.items() if top - s <= margin]
        if len(near) >= 2:
            winners.update(near)
    return winners


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: tie_winners.py <details.jsonl> [margin]", file=sys.stderr)
        return 2
    margin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    means = load_means(sys.argv[1])
    winners = tied_winners(means, margin)
    for m in sorted(winners):
        print(m)
    if not winners:
        print(f"# no ties within margin {margin} across {len(means)} models", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
