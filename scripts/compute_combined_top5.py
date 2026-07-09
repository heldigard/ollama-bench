#!/usr/bin/env python3
# vs-soft-allow  — script CLI helper; flat comprehensions read as deep indent to the guard.
"""Combined-rank top-N: avg of (deep rank + tie-break rank) per task.

Reads deep_bench.tsv + tiebreak_ranking.md, computes combined rank, prints
top-N per task + KEEP set (any top-N) vs DELETE candidates.

Usage: python3 scripts/compute_combined_top5.py --deep RUN.tsv --tiebreak RUN.md
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


def _deep_ranks(tsv: Path) -> dict:
    """{task: {model: rank}} from deep_bench.tsv."""
    out: dict = {}
    with tsv.open() as f:
        for row in csv.DictReader(f, delimiter="\t"):
            out.setdefault(row["task"], {})[row["model"]] = int(row["rank"])
    return out


def _tiebreak_ranks(md: Path) -> dict:
    """{task: {model: rank}} parsed from tiebreak_ranking.md tables."""
    out: dict = {}
    cur = None
    for line in md.read_text().splitlines():
        m = re.match(r"^## (\w+)$", line.strip())
        if m:
            cur = m.group(1)
            out[cur] = {}
            continue
        if cur:
            r = re.match(r"^\| (\d+) \| [\d.\-]+ \| `([^`]+)` \|", line.strip())
            if r:
                out[cur][r.group(2)] = int(r.group(1))
    return out


def _combined(deep: dict, tb: dict) -> dict:
    """{task: [(model, avg_rank, deep_rank, tb_rank)]} sorted ascending by avg."""
    out: dict = {}
    tasks = sorted(set(deep) | set(tb))
    for t in tasks:
        d = deep.get(t, {})
        t_ranks = tb.get(t, {})
        models = set(d) & set(t_ranks)  # only models in BOTH
        rows = []
        for m in models:
            avg = (d[m] + t_ranks[m]) / 2
            rows.append((m, avg, d[m], t_ranks[m]))
        rows.sort(key=lambda x: x[1])
        out[t] = rows
    return out


def _top_n(rows: list, n: int) -> list:
    """First n entries (ties at nth avg included)."""
    if not rows:
        return []
    nth = rows[min(n - 1, len(rows) - 1)][1]
    return [r for r in rows if r[1] <= nth or r[1] == nth]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--deep", required=True, help="deep TSV from the same benchmark cycle")
    ap.add_argument(
        "--tiebreak", required=True, help="tie-break Markdown from the same benchmark cycle"
    )
    args = ap.parse_args()

    deep_path = Path(args.deep)
    tb_path = Path(args.tiebreak)
    if not deep_path.is_file() or not tb_path.is_file():
        print("ERROR: deep/tie-break input does not exist", file=sys.stderr)
        return 2
    print(f"# Inputs: deep={deep_path.name} tiebreak={tb_path.name}\n")
    deep = _deep_ranks(deep_path)
    tb = _tiebreak_ranks(tb_path)
    if not deep or not tb:
        print("ERROR: missing inputs", file=sys.stderr)
        return 2

    combined = _combined(deep, tb)
    top_models: set[str] = set()
    print(f"# Combined-rank Top-{args.top} per task\n")
    for task, rows in combined.items():
        selected = _top_n(rows, args.top)
        print(f"\n## {task}")
        for m, avg, dr, tr in selected:
            print(f"  avg={avg:.1f} (deep #{dr}, tb #{tr})  {m}")
            top_models.add(m)

    tb_models = {m for ranks in tb.values() for m in ranks}
    not_top = tb_models - top_models
    print("\n\n# Summary")
    print(f"  Top-{args.top} unique models (KEEP): {len(top_models)}")
    print(f"  Not in any top-{args.top} (DELETE candidates): {len(not_top)}")

    if args.delete and not_top:
        print("\n# ollama rm commands for DELETE candidates:")
        for m in sorted(not_top):
            print(f"ollama rm '{m}'")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
