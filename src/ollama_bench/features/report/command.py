"""report - markdown ranking generation from deep_bench TSV."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from ollama_bench.shared.paths import result_path


def _render_markdown(per_task: dict, title: str) -> str:
    """Render a per-task leaderboard as a Markdown table."""
    lines = [f"# {title}\n"]
    if not per_task:
        lines.append("(no data)")
        return "\n".join(lines)
    for task, ranked in per_task.items():
        lines.append(f"\n## {task}\n")
        lines.append("| # | Score | Model |")
        lines.append("|---|---|---|")
        for i, (m, s) in enumerate(ranked, 1):
            lines.append(f"| {i} | {s} | `{m}` |")
    return "\n".join(lines) + "\n"


def _read_tsv(path: Path) -> dict:
    """Read deep_bench TSV (task/rank/score/model columns). Returns {task: [(model, score)]}."""
    per_task: dict[str, list] = {}
    with path.open() as f:
        for row in csv.DictReader(f, delimiter="\t"):
            task = row["task"]
            score = float(row["score"])
            per_task.setdefault(task, []).append((row["model"], score))
    for t in per_task:
        per_task[t].sort(key=lambda x: -x[1])
    return per_task


def cmd_report_build(args) -> int:
    """`ollama-bench report build` - read deep TSV -> write ranking MD."""
    src = Path(args.input) if args.input else result_path("deep_bench", ext="tsv")
    if not src.exists():
        print(f"ERROR: no TSV at {src}", file=sys.stderr)
        return 2
    per_task = _read_tsv(src)
    title = args.title or f"Ollama Deep-Bench — Top 5 per task ({src.stat().st_mtime})"
    md = _render_markdown(per_task, title)
    out = Path(args.output) if args.output else src.with_suffix(".md")
    out.write_text(md)
    print(f"Wrote {out}", file=sys.stderr)
    return 0


def add_parser(sub, parent):
    p = sub.add_parser("report", parents=[parent], help="Generate markdown ranking from bench results.")
    sp = p.add_subparsers(dest="report_cmd", required=True)
    bc = sp.add_parser("build", parents=[parent], help="Read TSV -> write MD.")
    bc.add_argument("-i", "--input", help="Input TSV (default: cache/deep_bench.tsv).")
    bc.add_argument("-o", "--output", help="Output MD path.")
    bc.add_argument("-t", "--title", help="MD title.")
    bc.set_defaults(cmd=cmd_report_build)
