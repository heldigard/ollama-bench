"""deep — canonical task bench across N models.

Canonical harness tasks: improve, codeq_sum, smart_trim, web_synth, code_gen.
Scoring is task-specific and emits per-case metric details to avoid the older
speed/leak/concision saturation problem.

Supports incremental runs (--resume) and GPU-friendly pacing (--cooldown).

# vs-soft-allow  — end-to-end pipeline (prompts → run → score → rank → write).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from statistics import mean

from ollama_bench.features.canonical_tasks import PROMPTS, iter_cases, score_task_response
from ollama_bench.shared.config import NUM_PREDICT_DEFAULT, TASKS
from ollama_bench.shared.gpu import gpu_temp, wait_gpu_cool
from ollama_bench.shared.ollama import CallOpts, call, get_model_names
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import strip_reasoning

# Execution is DELIBERATELY SEQUENTIAL — never re-introduce parallelism. A prior
# ThreadPoolExecutor design maxed the GPU (80°C+), ran for hours, and got killed
# mid-run, losing all progress. See memory: bench-gpu-safety.
DEFAULT_COOLDOWN = 60  # seconds between models
GPU_TEMP_LIMIT = 75  # °C — wait if GPU hotter


def _smoke_ok_candidates(strip: bool = True) -> list[str]:
    """Read smoke TSV and return benchable models.

    Default includes status=ok plus strippable=1 models, because reasoning
    traces can be cleaned and should be tracked as a handling requirement
    instead of hard-disqualifying the model. With strip=False, returns clean
    status=ok only for strict legacy comparisons.
    Falls back to all installed if no TSV.
    """
    smoke_tsv = result_path("smoke_all")
    if not smoke_tsv.exists():
        return get_model_names()
    candidates: list[str] = []
    with smoke_tsv.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r["status"] == "ok":
                candidates.append(r["name"])
            elif strip and r.get("strippable") == "1":
                candidates.append(r["name"])
    return candidates


def _load_completed_models(tsv_path: Path) -> set[str]:
    """Read existing results TSV and return set of models already benched."""
    if not tsv_path.exists():
        return set()
    models: set[str] = set()
    with tsv_path.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            models.add(r["model"])
    return models


def run_model(model: str, tasks: list[str], opts: CallOpts, strip: bool = False) -> dict:
    """Run model across all selected tasks. Returns {model: {task: [scores]}}.

    With strip=True, applies strip_reasoning to each response BEFORE scoring,
    so thinking-leak models are judged on their cleaned answer.
    """
    out: dict = {task: [] for task in tasks}
    for task in tasks:
        task_opts = replace(opts, api=TASKS[task]["protocol"])
        for case in iter_cases(task):
            res = call(model, case["prompt"], opts=task_opts)
            if strip and "out" in res:
                res = {**res, "out": strip_reasoning(res["out"])}
            scored = score_task_response(task, res, case, strip_strippable=strip)
            out[task].append(
                {
                    "pid": case["id"],
                    "sc": scored["score"],
                    "weight": float(case.get("weight", 1.0)),
                    "metrics": scored["metrics"],
                    "response": str(res.get("out", "")),
                }
            )
    return {model: out}


def _weighted_mean(items: list[dict]) -> float | None:
    scored = [item for item in items if "sc" in item]
    if not scored:
        return None
    total_weight = sum(float(item.get("weight", 1.0)) for item in scored)
    if total_weight <= 0:
        return mean(float(item["sc"]) for item in scored)
    return sum(float(item["sc"]) * float(item.get("weight", 1.0)) for item in scored) / total_weight


def _aggregate(results: dict, tasks: list[str]) -> dict[str, list]:
    """Compute risk-weighted mean per task; sort descending."""
    per_task: dict[str, list] = {t: [] for t in tasks}
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r:
            continue
        for t in tasks:
            items = r.get(t, [])
            task_mean = _weighted_mean(items)
            if task_mean is not None:
                per_task[t].append((m, round(task_mean, 2)))
    for t in per_task:
        per_task[t].sort(key=lambda x: -x[1])
    return per_task


def _details_path(base: Path) -> Path:
    """Path to the append-only per-case details JSONL (kill-safe source of truth)."""
    return base.with_name(f"{base.stem}_details").with_suffix(".jsonl")


def _append_model_details(model: str, results: dict, base: Path, tasks: list[str]) -> None:
    """Append one model's per-case metrics to the details JSONL immediately.

    This is the incremental, kill-safe save: each completed model is flushed to
    disk before the next one starts, so a kill/crash never loses scored work. The
    JSONL is append-only — it is NEVER truncated mid-run (the old design wrote it
    only at the very end, so any kill erased every score).
    """
    task_map = results.get(model)
    if not isinstance(task_map, dict) or "err" in task_map:
        return
    path = _details_path(base)
    with path.open("a") as f:
        for task in tasks:
            for item in task_map.get(task, []):
                f.write(
                    json.dumps(
                        {
                            "model": model,
                            "task": task,
                            "case": item.get("pid"),
                            "score": item.get("sc"),
                            "weight": item.get("weight", 1.0),
                            "metrics": item.get("metrics", {}),
                            "response": item.get("response", ""),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )


def _load_results_from_details(base: Path, tasks: list[str]) -> dict:
    """Rebuild a results dict from the append-only details JSONL.

    Resilient to a truncated trailing line (a kill mid-write leaves a partial
    JSON record) — bad lines are skipped, not fatal. This is what makes --resume
    reconstruct every previously-scored model so the final re-rank never drops
    completed work.
    """
    path = _details_path(base)
    results: dict = {}
    if not path.exists():
        return results
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # truncated tail from a killed run; skip
            model, task = entry.get("model"), entry.get("task")
            if not model or task not in tasks:
                continue
            results.setdefault(model, {}).setdefault(task, []).append(
                {
                    "pid": entry.get("case"),
                    "sc": entry.get("score"),
                    "weight": float(entry.get("weight", 1.0)),
                    "metrics": entry.get("metrics", {}),
                    "response": entry.get("response", ""),
                }
            )
    return results


def _load_results_from_tsv(tsv_path: Path, tasks: list[str]) -> dict:
    """Reconstruct task-level means from the ranked TSV.

    Defense-in-depth fallback for when the details JSONL is missing but the TSV
    survived (e.g. an older run written by the pre-incremental code). Produces
    one synthetic case per task carrying the model's recorded mean score, which
    is enough for _aggregate to rank it alongside freshly-benched models.
    """
    results: dict = {}
    if not tsv_path.exists():
        return results
    with tsv_path.open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            model, task = r.get("model"), r.get("task")
            if not model or task not in tasks:
                continue
            raw_score = r.get("score")
            if raw_score is None:
                continue
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                continue
            results.setdefault(model, {}).setdefault(task, []).append(
                {"pid": "tsv_mean", "sc": score, "metrics": {}}
            )
    return results


def _append_model_to_tsv(model: str, task_scores: dict[str, float], tsv_path: Path) -> None:
    """Append one model's results to the TSV (incremental save)."""
    write_header = not tsv_path.exists()
    with tsv_path.open("a", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        if write_header:
            w.writerow(["task", "rank", "score", "model"])
        for task, score in task_scores.items():
            w.writerow([task, 0, score, model])  # rank=0 placeholder, re-ranked later


def _rewrite_tsv_with_ranks(per_task: dict[str, list], tsv_path: Path) -> None:
    """Overwrite TSV with correct rankings from aggregated results."""
    with tsv_path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["task", "rank", "score", "model"])
        for t, ranked in per_task.items():
            for i, (m, s) in enumerate(ranked, 1):
                w.writerow([t, i, s, m])


def _write_outputs(per_task: dict[str, list], tasks: list[str], base: Path) -> None:
    """Write TSV + MD summary.

    The per-case details JSONL is maintained incrementally (_append_model_details)
    during the run, so it is NOT rewritten here — rewriting would truncate the
    kill-safe source of truth. TSV/MD are derived views, safe to rebuild from the
    fully-reconstructed results each time.
    """
    tsv_path = base.with_suffix(".tsv")
    _rewrite_tsv_with_ranks(per_task, tsv_path)
    md_path = base.with_suffix(".md")
    with md_path.open("w") as f:
        f.write("# Deep-bench — top-5 per task\n\n")
        for t, ranked in per_task.items():
            score_counts: dict[float, int] = {}
            for _model, score in ranked:
                score_counts[score] = score_counts.get(score, 0) + 1
            max_tie = max(score_counts.values(), default=0)
            f.write(
                f"\n## {t}\n\n"
                f"Discrimination: {len(score_counts)} unique scores; max tie group {max_tie}.\n\n"
                "| # | Score | Model |\n|---|---|---|\n"
            )
            for i, (m, s) in enumerate(ranked[:5], 1):
                f.write(f"| {i} | {s} | `{m}` |\n")
    print(f"Wrote {tsv_path}\nWrote {md_path}", file=sys.stderr)


def cmd_deep(args: argparse.Namespace) -> int:
    """`ollama-bench deep` entry point."""
    strict_clean = bool(getattr(args, "strict_clean", False))
    strip = bool(getattr(args, "strip", False)) or not strict_clean
    resume = bool(getattr(args, "resume", False))
    cooldown = int(getattr(args, "cooldown", DEFAULT_COOLDOWN))
    temp_limit = int(getattr(args, "temp_limit", GPU_TEMP_LIMIT))

    candidates = args.candidates if args.candidates else _smoke_ok_candidates(strip=strip)
    if not candidates or (not args.candidates and not result_path("smoke_all").exists()):
        candidates = get_model_names()
        print(
            f"# No smoke TSV; falling back to all {len(candidates)} installed models",
            file=sys.stderr,
        )
    tasks = args.tasks if args.tasks else list(PROMPTS.keys())

    # Determine output path
    suffix = "_strip" if strip else ""
    base = Path(args.output) if args.output else result_path(f"deep_bench{suffix}")
    tsv_path = base.with_suffix(".tsv")

    # A fresh (non-resume) run starts clean so incremental appends don't stack
    # onto stale TSV/JSONL from a previous run. --resume preserves + extends them.
    if not resume:
        for stale in (tsv_path, _details_path(base)):
            if stale.exists():
                stale.unlink()

    # Resume: skip models already in results
    if resume:
        completed = _load_completed_models(tsv_path)
        before = len(candidates)
        candidates = [m for m in candidates if m not in completed]
        skipped = before - len(candidates)
        if skipped:
            print(f"# Resume: skipping {skipped} already-benched models", file=sys.stderr)
        if not candidates:
            print("# Resume: all models already done", file=sys.stderr)
            return 0

    total_prompts = sum(len(iter_cases(t)) for t in tasks)
    mode = "strip" if strip else "clean"
    print(
        f"# Deep-bench ({mode}): {len(candidates)} candidates × {total_prompts} prompts "
        f"(cooldown={cooldown}s, temp_limit={temp_limit}°C)",
        file=sys.stderr,
    )
    # In strip mode, reasoning models spend tokens on <think>/<reasoning> BEFORE
    # the answer; give them headroom so the cleaned answer actually fits.
    num_predict = 600 if strip else NUM_PREDICT_DEFAULT
    # retries=0: the bench must score fast. A model failing consistently under
    # GPU contention (transient empty) registers -100 immediately rather than
    # stalling every prompt on backoff retries — that -100 is the diagnostic
    # signal, not a silent hang. Production callers keep the default retries=2.
    opts = CallOpts(num_predict=num_predict, num_ctx=4096, retries=0)

    # Reconstruct every previously-scored model so the final re-rank never drops
    # completed work. Source of truth = append-only details JSONL (kill-safe);
    # the ranked TSV is the fallback when JSONL is missing (older/other runs).
    results: dict = _load_results_from_details(base, tasks) if resume else {}
    if resume:
        for model, task_map in _load_results_from_tsv(tsv_path, tasks).items():
            results.setdefault(model, task_map)

    for i, model in enumerate(candidates, 1):
        short = model.split("/")[-1][:60]
        print(f"  [{i:2d}/{len(candidates)}] {short}", file=sys.stderr, flush=True)

        # GPU safety: always temp-gate before loading a model (a hot card must
        # never get a fresh workload), and sleep the cooldown BETWEEN models so
        # the GPU dissipates heat. No cooldown before the very first model.
        wait_gpu_cool(temp_limit)
        if i > 1:
            time.sleep(cooldown)

        try:
            r = run_model(model, tasks, opts, strip)
        except Exception as e:
            r = {model: {"err": str(e)}}
        results.update(r)

        # Incremental save: flush BOTH the ranked TSV and the per-case details
        # JSONL to disk now, so a kill/crash never loses this model's scores.
        if model in results and isinstance(results[model], dict) and "err" not in results[model]:
            task_scores = {}
            for t in tasks:
                items = results[model].get(t, [])
                task_mean = _weighted_mean(items)
                if task_mean is not None:
                    task_scores[t] = round(task_mean, 2)
            if task_scores:
                _append_model_to_tsv(model, task_scores, tsv_path)
                _append_model_details(model, results, base, tasks)
                print(
                    f"    saved ({', '.join(f'{t}={s:.2f}' for t, s in list(task_scores.items())[:3])}...)",
                    file=sys.stderr,
                )

        temp = gpu_temp()
        if temp > 0:
            print(f"    GPU: {temp}°C", file=sys.stderr)

    # Final: re-rank over the fully-reconstructed results and write derived views.
    per_task = _aggregate(results, tasks)
    _write_outputs(per_task, tasks, base)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    """Attach deep subcommand to root CLI."""
    p = sub.add_parser("deep", parents=[parent], help="5-task × N model bench.")
    p.add_argument(
        "-c", "--candidates", nargs="*", help="Models to bench (default: smoke-OK list)."
    )
    p.add_argument(
        "-t",
        "--tasks",
        nargs="*",
        choices=list(PROMPTS.keys()),
        help="Tasks to include (default: all).",
    )
    p.add_argument("-o", "--output", help="Output TSV base path (default: cache dir).")
    p.add_argument(
        "--strip",
        action="store_true",
        help="Compatibility flag: strip reasoning traces before scoring. This is now "
        "the default unless --strict-clean is used.",
    )
    p.add_argument(
        "--strict-clean",
        action="store_true",
        help="Legacy mode: exclude smoke-flagged strippable models and score raw output.",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Skip models already present in the output TSV (incremental run).",
    )
    p.add_argument(
        "--cooldown",
        type=int,
        default=DEFAULT_COOLDOWN,
        help=f"Seconds to wait between models (default: {DEFAULT_COOLDOWN}).",
    )
    p.add_argument(
        "--temp-limit",
        type=int,
        default=GPU_TEMP_LIMIT,
        help=f"Max GPU °C before forced wait (default: {GPU_TEMP_LIMIT}).",
    )
    p.set_defaults(cmd=cmd_deep)
