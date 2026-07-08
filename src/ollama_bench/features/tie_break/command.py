"""tie_break — re-bench tied candidates with harder canonical prompts.

Use when `deep` still has close models. Harder prompt bundles reuse the same
task-specific scoring as `deep`, with no single-score saturation cap.

# vs-soft-allow  — end-to-end pipeline (prompts → run → score → rank → MD).
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.features.canonical_tasks import HARD_PROMPTS as _HARD_PROMPTS
from ollama_bench.features.canonical_tasks import score_task_response
from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import strip_reasoning

PROMPTS: dict[str, dict] = {
    task: {
        **cfg,
        "scorer": (lambda out, _task=task, _cfg=cfg: sum(
            score_task_response(_task, {"out": out, "tps": 0, "done": "stop"}, case)["score"]
            for case in _cfg["cases"]
        ) / max(len(_cfg["cases"]), 1)),
    }
    for task, cfg in _HARD_PROMPTS.items()
}


def run_model(model: str, opts: CallOpts) -> dict:
    """Run a single model across all hard tasks. Returns {model: {task: score}}."""
    out: dict = {}
    for task, cfg in PROMPTS.items():
        task_items: list[dict] = []
        for case in cfg["cases"]:
            res = call(model, case["prompt"], opts=opts)
            if "out" in res:
                res = {**res, "out": strip_reasoning(res["out"])}
            scored = score_task_response(task, res, {**case, "budget_words": cfg["budget"]})
            task_items.append({
                "case": case["id"],
                "score": scored["score"],
                "metrics": scored["metrics"],
            })
        out[task] = {
            "score": round(sum(i["score"] for i in task_items) / max(len(task_items), 1), 2),
            "items": task_items,
        }
    return {model: out}


def _aggregate(results: dict, tasks: list[str]) -> dict[str, list]:
    """Aggregate per-task scores into ranked lists."""
    per_task: dict[str, list] = {t: [] for t in tasks}
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r:
            continue
        for t in tasks:
            sc = r.get(t)
            if isinstance(sc, dict) and isinstance(sc.get("score"), (int, float)):
                per_task[t].append((m, sc["score"]))
            elif isinstance(sc, (int, float)):
                per_task[t].append((m, sc))
    for t in per_task:
        per_task[t].sort(key=lambda x: -x[1])
    return per_task


def cmd_tie_break(args: argparse.Namespace) -> int:
    """`ollama-bench tie-break` entry point."""
    candidates = args.winners or []
    if not candidates:
        print("ERROR: --winners required (space-separated model names)", file=sys.stderr)
        return 2
    print(f"# Tie-break bench: {len(candidates)} winners × {len(PROMPTS)} hard tasks", file=sys.stderr)
    opts = CallOpts(num_predict=300, num_ctx=4096)

    results: dict = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m, opts): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(candidates)}] {m[:55]}  done", file=sys.stderr, flush=True)

    per_task = _aggregate(results, list(PROMPTS.keys()))
    out_path = Path(args.output) if args.output else result_path("tiebreak_ranking", ext="md")
    detail_path = out_path.with_name(f"{out_path.stem}_details").with_suffix(".jsonl")
    with out_path.open("w") as f:
        f.write("# Ollama Tie-Break — Hard Prompts + Structural Scoring\n\n")
        f.write("Each task uses harder canonical cases + task-specific scoring.\n")
        f.write("Higher = better. See companion JSONL for component metrics.\n\n")
        for task, ranked in per_task.items():
            score_counts: dict[float, int] = {}
            for _model, score in ranked:
                score_counts[score] = score_counts.get(score, 0) + 1
            max_tie = max(score_counts.values(), default=0)
            f.write(
                f"\n## {task}\n\n"
                f"Discrimination: {len(score_counts)} unique scores; max tie group {max_tie}.\n\n"
                "| # | Score | Model |\n|---|---|---|\n"
            )
            for i, (m, s) in enumerate(ranked, 1):
                f.write(f"| {i} | {s:.2f} | `{m}` |\n")
    with detail_path.open("w") as f:
        for model, task_map in sorted(results.items()):
            if not isinstance(task_map, dict) or "err" in task_map:
                continue
            for task, payload in task_map.items():
                if not isinstance(payload, dict):
                    continue
                for item in payload.get("items", []):
                    f.write(json.dumps({
                        "model": model,
                        "task": task,
                        "case": item.get("case"),
                        "score": item.get("score"),
                        "metrics": item.get("metrics", {}),
                    }, sort_keys=True) + "\n")
    print(f"\nWrote {out_path}\nWrote {detail_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    """Attach tie-break subcommand to root CLI."""
    p = sub.add_parser(
        "tie-break", parents=[parent], help="Re-bench tied candidates with harder prompts."
    )
    p.add_argument("-w", "--winners", nargs="+", required=True,
                   help="Model names to re-bench (space-separated).")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_tie_break)
