#!/usr/bin/env python3
"""browser-model-bench — rigorous benchmark for the 2 winner Ollama models on
browser-automation subtasks. Determines PRIMARY vs FALLBACK per role based on
accuracy, latency, hallucination rate, and variance.

Tasks (rigorous mode):
- T1 vision_ocr: extract all text from screenshot (precision, recall, halluc_rate)
- T2 vision_classify: 8-class UI state classifier (top-1 accuracy, confusion)
- T3 snapshot_diff: 3 scenarios minor/medium/major (change-recall, FP rate)
- T4 tool_call: 6 scenarios click/fill/scroll/wait/eval (success rate)
- T5 speed: 5 reps per model cold+warm (mean, p50, p95, tokens/sec)

Models (2 winners + 1 specialist):
- qwen3.5:4b (vision + tools winner)
- MobiusDevelopment/gemma-4-12B-it-qat-q4 (text-reasoning winner)
- fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b (tool-call tie)

Usage:
  python3 ~/.claude/scripts/browser-model-bench.py             # quick
  python3 ~/.claude/scripts/browser-model-bench.py --rigorous  # deep (default = quick)

Architecture: this module is the CLI facade + run orchestration. Fixture
builders, ground-truth/snapshot data, and scoring live in the sibling
``_bench_fixtures``, ``_bench_data``, and ``_bench_scoring`` modules.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.request
from itertools import product
from pathlib import Path

from ollama_bench.features.browser_bench._data import (
    P_T1,
    P_T2,
    P_T3_PROMPTS,
    P_T4_PROMPTS,
    SNAPSHOT_1,
    SNAPSHOT_2,
    SNAPSHOT_BASE,
    SNAPSHOT_BASE_SEARCH,
    SNAPSHOT_LIST_VIEW,
    SNAPSHOT_LOADING,
    SNAPSHOT_TOP_OF_TABLE,
)
from ollama_bench.features.browser_bench._fixtures import (
    QUICK_FIXTURES,
    RIGOROUS_FIXTURES,
    build_fixtures,
)
from ollama_bench.features.browser_bench._scoring import (
    OLLAMA_URL,
    OllamaOptions,
    call_ollama,
    score_t1,
    score_t2,
    score_t3,
    score_t4,
)

__all__ = [
    "OLLAMA_URL",
    "OUT_DIR",
    "PRIMARY_MODELS",
    "P_T1",
    "P_T2",
    "P_T3_PROMPTS",
    "P_T4_PROMPTS",
    "QUICK_FIXTURES",
    "RIGOROUS_FIXTURES",
    "SNAPSHOT_1",
    "SNAPSHOT_2",
    "SNAPSHOT_BASE",
    "SNAPSHOT_BASE_SEARCH",
    "SNAPSHOT_LIST_VIEW",
    "SNAPSHOT_LOADING",
    "SNAPSHOT_TOP_OF_TABLE",
    "TOOL_MODELS",
    "OllamaOptions",
    "build_fixtures",
    "call_ollama",
    "main",
    "render_markdown",
    "score_t1",
    "score_t2",
    "score_t3",
    "score_t4",
]

OUT_DIR = Path.home() / ".claude" / "state" / "browser-model-bench"

# 2026-07-08 PM: aligned with ~/ollama-bench/.memory-bank/topics/local-ollama-lineup.md
# - qwen3.5:4b: vision + tools winner (kept; lightweight infra)
# - HauhauCS-Balanced: smart_trim #1 (replaces Grug-12B, DROPPED 2026-07-08 PM trim)
# - huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K: tool-call winner (kept)
PRIMARY_MODELS = [
    "cryptidbleh/gemma4-claude-opus-4.6:latest",
    "hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M",
]
TOOL_MODELS = PRIMARY_MODELS + [
    "huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K",
]

_HAUAHAUCS = "huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K"


def _vision_models(text_models: list[str]) -> list[str]:
    return [m for m in text_models if m in PRIMARY_MODELS or "gemma" in m or "qwen" in m.lower()]


def _t1_attempt(model, fname, img, rep, results):
    out = call_ollama(model, P_T1, img, OllamaOptions(num_predict=400))
    if "error" not in out:
        out["score"] = score_t1(out["content"], fname)
        sc = out["score"]
        print(
            f"  T1 OCR [{model[:36]:38}] {fname} rep{rep + 1} {out['seconds']}s recall={sc.get('recall')} halluc={sc.get('hallucination_rate')}"
        )
    results.append({"task": "T1_ocr", "model": model, "fixture": fname, "rep": rep + 1, **out})


def _t2_attempt(model, fname, img, rep, results):
    out = call_ollama(model, P_T2, img, OllamaOptions(num_predict=20))
    if "error" not in out:
        out["score"] = score_t2(out["content"], fname)
        sc = out["score"]
        print(
            f"  T2 CLS [{model[:36]:38}] {fname} rep{rep + 1} {out['seconds']}s picked={sc['picked']} ok={sc['ok']}"
        )
    results.append({"task": "T2_classify", "model": model, "fixture": fname, "rep": rep + 1, **out})


def _t3_attempt(model, scenario, prompt, rep, results):
    out = call_ollama(model, prompt, None, OllamaOptions(num_predict=300))
    if "error" not in out:
        out["score"] = score_t3(out["content"], scenario)
        sc = out["score"]
        print(
            f"  T3 DIFF[{scenario:6}] [{model[:36]:38}] rep{rep + 1} {out['seconds']}s hits={sc['hits']}/{sc['of']}"
        )
    results.append({"task": "T3_diff", "model": model, "scenario": scenario, "rep": rep + 1, **out})


def _t4_attempt(model, scenario, prompt, rep, results):
    out = call_ollama(model, prompt, None, OllamaOptions(num_predict=100))
    if "error" not in out:
        out["score"] = score_t4(out["content"], scenario)
        sc = out["score"]
        print(
            f"  T4 TLP[{scenario:8}] [{model[:36]:38}] rep{rep + 1} {out['seconds']}s ok={sc['ok']}"
        )
    results.append({"task": "T4_tool", "model": model, "scenario": scenario, "rep": rep + 1, **out})


def _run_t1(fixtures: dict, models: list[str], reps: int, results: list[dict]) -> None:
    """T1 — OCR over fixture images."""
    for (fname, (img, _)), model, rep in product(fixtures.items(), models, range(reps)):
        _t1_attempt(model, fname, img, rep, results)


def _run_t2(fixtures: dict, models: list[str], reps: int, results: list[dict]) -> None:
    """T2 — 8-class UI state classification."""
    for (fname, (img, _)), model, rep in product(fixtures.items(), models, range(reps)):
        _t2_attempt(model, fname, img, rep, results)


def _run_t3(models: list[str], reps: int, results: list[dict]) -> None:
    """T3 — accessibility-tree snapshot diff (3 scenarios)."""
    for model, (scenario, prompt), rep in product(models, P_T3_PROMPTS.items(), range(reps)):
        _t3_attempt(model, scenario, prompt, rep, results)


def _run_t4(models: list[str], reps: int, results: list[dict]) -> None:
    """T4 — tool-call proposals (6 scenarios)."""
    for model, (scenario, prompt), rep in product(models, P_T4_PROMPTS.items(), range(reps)):
        _t4_attempt(model, scenario, prompt, rep, results)


def _run_t5(models: list[str], results: list[dict]) -> None:
    """T5 — speed (5 reps, fresh prompt each to defeat cache)."""
    speed_prompts = [f"Reply with word {i}" for i in range(5)]
    for model, (i, prompt) in product(models, enumerate(speed_prompts)):
        out = call_ollama(model, prompt, None, OllamaOptions(num_predict=5))
        results.append({"task": "T5_speed", "model": model, "rep": i + 1, **out})
    _report_t5_speeds(models, results)


def _t5_speeds_for(model: str, results: list[dict]) -> list[float]:
    out = []
    for r in results:
        same_task = r.get("task") == "T5_speed"
        same_model = r.get("model") == model
        positive = r.get("tokens_per_sec", 0) > 0
        if same_task and same_model and positive:
            out.append(r["tokens_per_sec"])
    return out


def _t5_summary_line(model: str, speeds: list[float]) -> str:
    stdev = statistics.stdev(speeds) if len(speeds) > 1 else 0
    return f"  T5 SPD [{model[:36]:38}] mean={statistics.mean(speeds):.1f} stdev={stdev:.1f} tok/s"


def _report_t5_speeds(models: list[str], results: list[dict]) -> None:
    for model in models:
        speeds = _t5_speeds_for(model, results)
        if speeds:
            print(_t5_summary_line(model, speeds))


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--quick", action="store_true", help="2 fixtures per task (legacy)")
    ap.add_argument(
        "--rigorous", action="store_true", help="8 fixtures + 2 reps per call + per-model variance"
    )
    ap.add_argument(
        "--models", nargs="+", default=None, help="override models (default: 2 winners + HauhauCS)"
    )
    args = ap.parse_args(argv)
    if not args.quick and not args.rigorous:
        args.quick = True  # default
    return args


def _select_fixture_set(args: argparse.Namespace) -> tuple[dict, int, list[str]]:
    if args.quick:
        fixtures = build_fixtures(QUICK_FIXTURES)
        reps = 1
    else:  # rigorous
        fixtures = build_fixtures(RIGOROUS_FIXTURES)
        reps = 2
    text_models = list(args.models) if args.models else PRIMARY_MODELS + [_HAUAHAUCS]
    return fixtures, reps, text_models


# =============================================================================
# Main
# =============================================================================
def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2).read()
    except Exception as exc:
        print(f"Ollama down: {exc}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d-%H%M%S")
    results: list[dict] = []

    fixtures, reps, text_models = _select_fixture_set(args)
    vision_models = _vision_models(text_models)

    print(
        f"[browser-model-bench] mode={'rigorous' if args.rigorous else 'quick'} "
        f"fixtures={len(fixtures)} reps={reps} models={len(text_models)}"
    )

    _run_t1(fixtures, vision_models, reps, results)
    _run_t2(fixtures, vision_models, reps, results)
    _run_t3(text_models, reps, results)
    _run_t4(text_models, reps, results)
    _run_t5(list(set(vision_models + text_models)), results)

    mode = "rigorous" if args.rigorous else "quick"
    json_path = OUT_DIR / f"results-{run_id}.json"
    json_path.write_text(
        json.dumps(
            {"run_id": run_id, "mode": mode, "results": results}, indent=2, ensure_ascii=False
        )
    )
    md_path = OUT_DIR / f"results-{run_id}.md"
    md_path.write_text(render_markdown(results, mode))
    print(f"\n[OK] results -> {json_path}")
    print(f"[OK] report  -> {md_path}")
    return 0


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0


def _summary_row(model: str, tasks: dict[str, list[dict]]) -> str:
    """One per-model markdown summary row across T1-T5."""
    t1 = [r for r in tasks.get("T1_ocr", []) if "error" not in r]
    t1_recalls = [
        r["score"]["recall"] for r in t1 if isinstance(r["score"].get("recall"), (int, float))
    ]
    t1_hall = [
        r["score"]["hallucination_rate"]
        for r in t1
        if isinstance(r["score"].get("hallucination_rate"), (int, float))
    ]
    t1_recall_mean = _mean(t1_recalls)
    t1_hall_mean = _mean(t1_hall)
    t2 = [r for r in tasks.get("T2_classify", []) if "error" not in r]
    t2_acc = sum(1 for r in t2 if r["score"]["ok"]) / max(len(t2), 1)
    t3 = [r for r in tasks.get("T3_diff", []) if "error" not in r]
    t3_avg = _mean([r["score"]["hits"] / r["score"]["of"] for r in t3])
    t4 = [r for r in tasks.get("T4_tool", []) if "error" not in r]
    t4_ok = sum(1 for r in t4 if r["score"]["ok"]) / max(len(t4), 1)
    t5 = [r["tokens_per_sec"] for r in tasks.get("T5_speed", []) if r.get("tokens_per_sec", 0) > 0]
    t5_stdev = statistics.stdev(t5) if len(t5) > 1 else 0
    return (
        f"| `{model}` | {t1_recall_mean:.2f} | {t1_hall_mean:.2f} | "
        f"{t2_acc:.0%} | {t3_avg:.2f} | {t4_ok:.0%} | {_mean(t5):.1f} ± {t5_stdev:.1f} |"
    )


def _group_by_model(results: list[dict]) -> dict[str, dict[str, list[dict]]]:
    by_model: dict[str, dict[str, list[dict]]] = {}
    for r in results:
        by_model.setdefault(r.get("model", "?"), {}).setdefault(r.get("task", "?"), []).append(r)
    return by_model


def _render_summary(by_model: dict[str, dict[str, list[dict]]]) -> list[str]:
    lines = [
        "## Summary by model",
        "",
        "| model | T1 recall | T1 halluc | T2 acc | T3 avg hits | T4 ok | T5 tok/s (mean ± stdev) |",
        "|---|---|---|---|---|---|---|",
    ]
    lines.extend(_summary_row(m, tasks) for m, tasks in sorted(by_model.items()))
    lines.append("")
    return lines


def _t1_row(model: str, r: dict) -> str:
    if "error" in r:
        return f"| `{model}` | {r['fixture']} | {r['rep']} | ERR | — | — | — |"
    sc = r["score"]
    return (
        f"| `{model}` | {r['fixture']} | {r['rep']} | {r['seconds']} | "
        f"{sc.get('recall', 'n/a')} | {sc.get('hallucination_rate', 0)} | {sc.get('score', 'n/a')} |"
    )


def _t2_row(model: str, r: dict) -> str:
    if "error" in r:
        return f"| `{model}` | {r['fixture']} | {r['rep']} | ERR | — | — | — |"
    sc = r["score"]
    mark = "✅" if sc["ok"] else "❌"
    return f"| `{model}` | {r['fixture']} | {r['rep']} | {r['seconds']} | {sc['expected']} | **{sc['picked']}** | {mark} |"


def _t3_row(model: str, r: dict) -> str:
    if "error" in r:
        return f"| `{model}` | {r['scenario']} | {r['rep']} | ERR | — | — |"
    sc = r["score"]
    return f"| `{model}` | {r['scenario']} | {r['rep']} | {r['seconds']} | {sc['hits']}/{sc['of']} | {sc['score']} |"


def _t4_row(model: str, r: dict) -> str:
    if "error" in r:
        return f"| `{model}` | {r['scenario']} | {r['rep']} | ERR | — | — |"
    sc = r["score"]
    mark = "✅" if sc["ok"] else "❌"
    return f"| `{model}` | {r['scenario']} | {r['rep']} | {r['seconds']} | {mark} | `{json.dumps(sc['call'])}` |"


def _t5_row(model: str, r: dict) -> str:
    if "error" in r:
        return f"| `{model}` | {r['rep']} | ERR | — | — |"
    return (
        f"| `{model}` | {r['rep']} | {r['seconds']} | {r['eval_tokens']} | {r['tokens_per_sec']} |"
    )


_RENDERERS = {
    "T1_ocr": ("| model | fixture | rep | seconds | recall | halluc | score |", "T1_ocr", _t1_row),
    "T2_classify": (
        "| model | fixture | rep | seconds | expected | picked | ok |",
        "T2_classify",
        _t2_row,
    ),
    "T3_diff": ("| model | scenario | rep | seconds | hits/of | score |", "T3_diff", _t3_row),
    "T4_tool": ("| model | scenario | rep | seconds | ok | call |", "T4_tool", _t4_row),
    "T5_speed": ("| model | rep | seconds | eval_tok | tok/s |", "T5_speed", _t5_row),
}


def _render_detail_section(task: str, by_model: dict[str, dict[str, list[dict]]]) -> list[str]:
    """Render one per-task detail table; empty if no rows."""
    headers, task_key, row_fn = _RENDERERS[task]
    pairs = [(m, r) for m, tasks in sorted(by_model.items()) for r in tasks.get(task_key, [])]
    if not pairs:
        return []
    out = [f"## {task}", "", headers, "|---|---|---|---|---|---|---|"]
    out.extend(row_fn(m, r) for m, r in pairs)
    out.append("")
    return out


def render_markdown(results: list[dict], mode: str) -> str:
    by_model = _group_by_model(results)
    lines = [f"# browser-model-bench ({mode})", ""]
    lines.extend(_render_summary(by_model))
    for task in ["T1_ocr", "T2_classify", "T3_diff", "T4_tool", "T5_speed"]:
        lines.extend(_render_detail_section(task, by_model))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())


# =============================================================================
# ollama-bench slice integration
# =============================================================================
# This file was ported from cli-orchestration (the cross-CLI browser bench).
# The above `main(argv)` is the standalone CLI. Below adds the ollama-bench
# subcommand shim so it slots into the existing cli.py::_SLICES registry.


def add_parser(sub, parent) -> None:
    """Register `ollama-bench browser-bench-vision` subcommand."""
    p = sub.add_parser(
        "browser-bench-vision",
        parents=[parent],
        help="Vision-grounded browser bench (T1 OCR, T2 classify, T3 diff, T4 tool, T5 speed).",
        description=(
            "Ported from cli-orchestration/src/cli_orchestration/browser/model_bench.py "
            "(2026-07-05). Distinct from `browser-tool` (which is a11y-ref dispatch): "
            "this slice measures VISION (OCR + 8-class UI state) + speed for the "
            "browser-automation role. Models updated to current champions per "
            "~/ollama-bench/.memory-bank/topics/local-ollama-lineup.md."
        ),
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--quick",
        action="store_true",
        help="2 fixtures per task (legacy; default if neither --quick nor --rigorous)",
    )
    g.add_argument(
        "--rigorous", action="store_true", help="8 fixtures + 2 reps per call + per-model variance"
    )
    p.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Override models (default: current champions from lineup)",
    )
    p.set_defaults(cmd=cmd_browser_bench_vision)


def cmd_browser_bench_vision(args) -> int:
    """ollama-bench subcommand entry point. Delegates to the standalone main()."""
    return _dispatch(args)


def _dispatch(args) -> int:
    """Convert ollama-bench namespace to the standalone main() argv list."""
    argv = []
    if args.rigorous:
        argv.append("--rigorous")
    elif args.quick:
        argv.append("--quick")
    if args.models:
        argv.extend(["--models", *args.models])
    rc = main(argv)
    return rc if isinstance(rc, int) else (0 if rc is None else 1)
