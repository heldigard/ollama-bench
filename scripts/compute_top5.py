#!/usr/bin/env python3
# vs-soft-allow  — script CLI helper (not a feature slice); flat control flow
# but the set-comprehensions over nested tuples read as deep indent to the guard.
"""Compute top-N per task from deep_bench TSV (combined-rank).

Prints top-N per task + models to KEEP (in any top-N) vs DELETE candidates.

Usage:
    python3 scripts/compute_top5.py [--tsv PATH] [--top N] [--delete]
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


def _read_ranked(tsv: Path) -> dict:
    """Read TSV -> {task: [(rank, score, model)]}."""
    ranked = defaultdict(list)
    with tsv.open() as f:
        for row in csv.DictReader(f, delimiter="\t"):
            ranked[row["task"]].append((int(row["rank"]), float(row["score"]), row["model"]))
    return dict(ranked)


def _nth_score(entries: list, top_n: int) -> float:
    """Score at the Nth position (for tie inclusion)."""
    if not entries:
        return -1.0
    entries_sorted = sorted(entries, key=lambda x: x[0])
    return entries_sorted[min(top_n - 1, len(entries_sorted) - 1)][1]


def _selected_entries(entries: list, top_n: int, nth: float) -> list:
    """Entries ranked <= top_n OR tying the Nth score."""
    return [e for e in entries if e[0] <= top_n or e[1] == nth]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default=str(Path.home() / ".cache/ollama-bench/results/deep_bench.tsv"))
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--delete", action="store_true",
                    help="Print `ollama rm` commands for models NOT in any top-N.")
    args = ap.parse_args()

    tsv = Path(args.tsv)
    if not tsv.exists():
        print(f"ERROR: {tsv} not found", file=sys.stderr)
        return 2

    per_task = _read_ranked(tsv)
    if not per_task:
        print("ERROR: no data in TSV", file=sys.stderr)
        return 2

    print(f"# Top-{args.top} per task\n")
    top_models: set[str] = set()
    for task, entries in per_task.items():
        nth = _nth_score(entries, args.top)
        selected = _selected_entries(entries, args.top, nth)
        if not selected:
            continue
        print(f"\n## {task}")
        for r, sc, m in selected:
            print(f"  {r}. {sc:.2f}  {m}")
            top_models.add(m)

    # Flatten all models via set comprehension (avoids deep nesting)
    all_models = {m for entries in per_task.values() for _, _, m in entries}
    not_top = all_models - top_models

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
