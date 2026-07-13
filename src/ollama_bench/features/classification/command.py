"""Closed-label classification benchmark with deterministic promotion gates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ollama_bench.features.classification.cases import (
    TAXONOMIES,
    build_prompt,
    select_cases,
)
from ollama_bench.features.classification.metrics import (
    parse_label,
    promotion_decision,
    summarize,
)
from ollama_bench.shared.gpu import paced
from ollama_bench.shared.ollama import CallOpts, call, get_models
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import prepare_scored_response

DEFAULT_COOLDOWN = 60
GPU_TEMP_LIMIT = 75


def evaluate_model(model: str, cases: tuple[dict, ...], opts: CallOpts) -> list[dict]:
    """Run every case for one model and retain auditable per-case outcomes."""
    rows: list[dict] = []
    for case in cases:
        raw = call(model, build_prompt(case), opts=opts)
        scored, leak = prepare_scored_response(raw)
        allowed = TAXONOMIES[case["suite"]]
        pred = None if "err" in scored else parse_label(str(scored.get("out", "")), allowed)
        rows.append(
            {
                "id": case["id"],
                "suite": case["suite"],
                "gold": case["label"],
                "pred": pred,
                "dt": scored.get("dt", 0),
                "tps": scored.get("tps", 0),
                "leak_policy": leak["policy"],
                "error": scored.get("err", ""),
            }
        )
    return rows


def _size_map() -> dict[str, float]:
    """Return installed model sizes in GiB; failure leaves sizes unknown."""
    try:
        models = get_models()
    except Exception as exc:  # noqa: BLE001 - ranking can run; promotion cannot pass
        print(f"WARNING: model sizes unavailable: {exc}", file=sys.stderr)
        return {}
    gib = 1024**3
    return {
        str(model["name"]): round(int(model["size"]) / gib, 3)
        for model in models
        if model.get("name") and model.get("size") is not None
    }


def _model_summary(rows: list[dict], cases: tuple[dict, ...], size_gib: float | None) -> dict:
    labels = tuple(sorted({label for case in cases for label in TAXONOMIES[case["suite"]]}))
    summary = summarize(rows, labels)
    summary["size_gib"] = size_gib
    summary["suites"] = {}
    for suite in sorted({case["suite"] for case in cases}):
        suite_rows = [row for row in rows if row["suite"] == suite]
        summary["suites"][suite] = summarize(suite_rows, TAXONOMIES[suite])
    return summary


def _report(
    summaries: dict[str, dict],
    rows_by_model: dict[str, list[dict]],
    baseline_name: str | None,
    args: argparse.Namespace,
) -> str:
    ranked = sorted(summaries, key=lambda name: (-summaries[name]["macro_f1"], name))
    lines = [
        "# Classification Bench",
        "",
        "Closed-label scoring is deterministic. Quality tolerance is an absolute macro-F1 "
        "difference. Speedup uses median end-to-end case latency; TPS is diagnostic only.",
        "",
        "`invalid_rate` measures outputs rejected by the syntax gate. It does not detect a "
        "valid but semantically wrong label and is not a measured production escalation rate.",
        "",
        "| # | macro-F1 | accuracy | invalid | median s | TPS | GiB | model |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for rank, name in enumerate(ranked, 1):
        item = summaries[name]
        size = "unknown" if item["size_gib"] is None else f"{item['size_gib']:.3f}"
        lines.append(
            f"| {rank} | {item['macro_f1']:.4f} | {item['accuracy']:.4f} | "
            f"{item['invalid_rate']:.4f} | {item['median_latency']:.4f} | "
            f"{item['median_tps']:.2f} | {size} | `{name}` |"
        )

    if baseline_name:
        baseline = summaries[baseline_name]
        lines.extend(["", f"## Promotion gate (baseline: `{baseline_name}`)", ""])
        for name in ranked:
            if name == baseline_name:
                continue
            decision = promotion_decision(
                summaries[name],
                baseline,
                quality_margin=args.quality_margin,
                min_speedup=args.min_speedup,
                max_size_gib=args.max_size_gib,
                max_invalid_rate=args.max_invalid_rate,
            )
            failed = ", ".join(decision["failed"]) or "none"
            lines.append(
                f"- **{decision['decision']}** `{name}`: latency speedup "
                f"{decision['latency_speedup']:.2f}x; quality floor "
                f"{decision['quality_floor']:.4f}; failed checks: {failed}."
            )

    lines.extend(["", "## Per-case audit", ""])
    for name in ranked:
        lines.extend(
            [
                f"### `{name}`",
                "",
                "| case | suite | gold | predicted | latency s | leak/error |",
                "|---|---|---|---|---:|---|",
            ]
        )
        for row in rows_by_model[name]:
            pred = row["pred"] or "INVALID"
            issue = row["error"] or (row["leak_policy"] if row["leak_policy"] != "clean" else "")
            lines.append(
                f"| {row['id']} | {row['suite']} | {row['gold']} | {pred} | "
                f"{float(row['dt']):.4f} | {str(issue)[:80]} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def cmd_classification(args: argparse.Namespace) -> int:
    """Run the classification benchmark and write a reproducible Markdown report."""
    models = list(args.models)
    if args.baseline and args.baseline not in models:
        print("ERROR: --baseline must also appear in --models", file=sys.stderr)
        return 2
    cases = select_cases(args.suite)
    print(
        f"# Classification bench: {len(models)} models x {len(cases)} cases "
        f"(suite={args.suite}, cooldown={args.cooldown}s)",
        file=sys.stderr,
    )
    opts = CallOpts(num_predict=8, num_ctx=1024, temperature=0.0)
    rows_by_model = paced(
        models,
        lambda model: evaluate_model(model, cases, opts),
        cooldown=args.cooldown,
        temp_limit=args.temp_limit,
    )
    sizes = _size_map()
    summaries = {
        model: _model_summary(rows, cases, sizes.get(model))
        for model, rows in rows_by_model.items()
        if isinstance(rows, list)
    }
    if not summaries:
        print("ERROR: no model produced benchmark rows", file=sys.stderr)
        return 1
    output = Path(args.output) if args.output else result_path("classification", ext="md")
    output.write_text(_report(summaries, rows_by_model, args.baseline, args))
    print(f"Wrote {output}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    parser = sub.add_parser(
        "classification",
        parents=[parent],
        help="Closed-label macro-F1 + latency benchmark with tiny-model promotion gates.",
    )
    parser.add_argument("-m", "--models", nargs="+", required=True, help="Models to benchmark.")
    parser.add_argument("--baseline", help="Incumbent model; must also be listed in --models.")
    parser.add_argument("--suite", choices=("all", *TAXONOMIES), default="all")
    parser.add_argument("-o", "--output", help="Output Markdown path (default: cache dir).")
    parser.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN)
    parser.add_argument("--temp-limit", type=int, default=GPU_TEMP_LIMIT)
    parser.add_argument("--quality-margin", type=float, default=0.02)
    parser.add_argument("--min-speedup", type=float, default=3.0)
    parser.add_argument("--max-size-gib", type=float, default=2.0)
    parser.add_argument("--max-invalid-rate", type=float, default=0.40)
    parser.set_defaults(cmd=cmd_classification)
