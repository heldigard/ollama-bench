"""Deterministic quality-first benchmark for local document rerankers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ollama_bench.features.rerank.cases import CASES, build_prompt
from ollama_bench.features.rerank.metrics import (
    mrr_at_k,
    ndcg_at_k,
    parse_ranking,
    promotion_decision,
    summarize,
)
from ollama_bench.shared.gpu import paced
from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import prepare_scored_response

DEFAULT_COOLDOWN = 60
GPU_TEMP_LIMIT = 75


def evaluate_model(model: str, cases: tuple[dict, ...], opts: CallOpts) -> list[dict]:
    """Rank every fixed corpus and retain auditable quality outcomes."""
    rows: list[dict] = []
    for case in cases:
        raw = call(model, build_prompt(case), opts=opts)
        scored, leak = prepare_scored_response(raw)
        relevance = {
            document["id"]: document["relevance"] for document in case["documents"]
        }
        ranking = (
            None
            if "err" in scored
            else parse_ranking(str(scored.get("out", "")), set(relevance))
        )
        rows.append(
            {
                "id": case["id"],
                "language": case["language"],
                "difficulty": case["difficulty"],
                "ranking": ranking,
                "ndcg_at_3": ndcg_at_k(ranking, relevance),
                "mrr_at_3": mrr_at_k(ranking, relevance),
                "top1_correct": bool(
                    ranking and relevance[ranking[0]] == max(relevance.values())
                ),
                "leak_policy": leak["policy"],
                "error": scored.get("err", ""),
            }
        )
    return rows


def _report(
    summaries: dict[str, dict],
    rows_by_model: dict[str, list[dict]],
    baseline_name: str | None,
    args: argparse.Namespace,
) -> str:
    ranked = sorted(
        summaries,
        key=lambda name: (
            -summaries[name]["ndcg_at_3"],
            -summaries[name]["mrr_at_3"],
            name,
        ),
    )
    lines = [
        "# Rerank Bench",
        "",
        "Ground-truth quality benchmark: graded relevance (0-3), nDCG@3, MRR@3, "
        "top-1 accuracy, and strict JSON validity. Latency and TPS do not affect ranking or promotion.",
        "",
        "| # | nDCG@3 | MRR@3 | top-1 | invalid | model |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for rank, name in enumerate(ranked, 1):
        item = summaries[name]
        lines.append(
            f"| {rank} | {item['ndcg_at_3']:.4f} | {item['mrr_at_3']:.4f} | "
            f"{item['top1_accuracy']:.4f} | {item['invalid_rate']:.4f} | `{name}` |"
        )
    if baseline_name:
        lines.extend(["", f"## Promotion gate (baseline: `{baseline_name}`)", ""])
        for name in ranked:
            if name == baseline_name:
                continue
            decision = promotion_decision(
                summaries[name],
                summaries[baseline_name],
                min_ndcg_gain=args.min_ndcg_gain,
            )
            failed = ", ".join(decision["failed"]) or "none"
            lines.append(
                f"- **{decision['decision']}** `{name}`: nDCG@3 gain "
                f"{decision['ndcg_gain']:+.4f}; failed checks: {failed}."
            )
    lines.extend(["", "## Per-case audit", ""])
    for name in ranked:
        lines.extend(
            [
                f"### `{name}`",
                "",
                "| case | language | difficulty | ranking | nDCG@3 | MRR@3 | issue |",
                "|---|---|---|---|---:|---:|---|",
            ]
        )
        for row in rows_by_model[name]:
            issue = row["error"] or (
                row["leak_policy"] if row["leak_policy"] != "clean" else ""
            )
            ranking = ", ".join(row["ranking"]) if row["ranking"] else "INVALID"
            lines.append(
                f"| {row['id']} | {row['language']} | {row['difficulty']} | {ranking} | "
                f"{row['ndcg_at_3']:.4f} | {row['mrr_at_3']:.4f} | {str(issue)[:80]} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def cmd_rerank(args: argparse.Namespace) -> int:
    """Run the reranking benchmark and write its deterministic Markdown report."""
    models = list(args.models)
    if args.baseline and args.baseline not in models:
        print("ERROR: --baseline must also appear in --models", file=sys.stderr)
        return 2
    print(f"# Rerank bench: {len(models)} models x {len(CASES)} cases", file=sys.stderr)
    opts = CallOpts(num_predict=64, num_ctx=4096, temperature=0.0)
    rows_by_model = paced(
        models,
        lambda model: evaluate_model(model, CASES, opts),
        cooldown=args.cooldown,
        temp_limit=args.temp_limit,
    )
    summaries = {
        model: summarize(rows)
        for model, rows in rows_by_model.items()
        if isinstance(rows, list)
    }
    if not summaries:
        print("ERROR: no model produced benchmark rows", file=sys.stderr)
        return 1
    output = Path(args.output) if args.output else result_path("rerank", ext="md")
    output.write_text(_report(summaries, rows_by_model, args.baseline, args))
    print(f"Wrote {output}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    parser = sub.add_parser(
        "rerank",
        parents=[parent],
        help="Ground-truth reranking bench: nDCG@3 + MRR@3, quality-first.",
    )
    parser.add_argument("-m", "--models", nargs="+", required=True, help="Models to benchmark.")
    parser.add_argument("--baseline", help="Incumbent reranker; must also appear in --models.")
    parser.add_argument("-o", "--output", help="Output Markdown path (default: cache dir).")
    parser.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN)
    parser.add_argument("--temp-limit", type=int, default=GPU_TEMP_LIMIT)
    parser.add_argument(
        "--min-ndcg-gain",
        type=float,
        default=0.02,
        help="Required strict nDCG@3 gain over baseline; speed is never considered.",
    )
    parser.set_defaults(cmd=cmd_rerank)
