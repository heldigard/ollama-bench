"""candidates — orchestrate pull → smoke → deep → report for new HF candidates.

Encapsulates the workflow done manually across rounds 3-4:
1. ollama pull <models...>
2. ollama-bench smoke -m <models>          # leak classification
3. ollama-bench deep -c <survivors>        # task score; strippable leaks cleaned
4. write a single MD report with recommendations vs incumbents

Replaces ~15 min of manual orchestration per round with one command. Reuses
existing slices via subprocess (no slice-to-slice imports, per CLAUDE.md rules).

Usage:
  ollama-bench candidates 'hf.co/owner/model:Q4_K_M' 'owner/model2:latest'
  ollama-bench candidates --tasks code_gen tool_call bug_finding 'owner/m:q4'

Output: ~/.cache/ollama-bench/results/candidates-<ts>.md + TSV
"""

from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
import sys
import time
from pathlib import Path

from ollama_bench.shared.paths import result_path

# vs-soft-allow  — orchestrator pipeline (pull → smoke → deep → report). Multi-step
# subprocess invocations inflate lexical depth without adding control-flow nesting.

__all__ = ["cmd_candidates", "add_parser"]


# Default tasks to bench in `deep`. Matches `deep` subcommand default.
DEFAULT_TASKS = ("improve", "codeq_sum", "smart_trim", "web_synth", "code_gen")


def _run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    """Run a subprocess, capture stdout, return (rc, output)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, f"TIMEOUT after {timeout}s: {' '.join(shlex.quote(c) for c in cmd)}"
    except FileNotFoundError as exc:
        return -1, f"COMMAND NOT FOUND: {exc}"


def _ollama_pull(model: str, timeout: int = 600) -> tuple[bool, str]:
    """Pull one model. Return (success, tail-of-output)."""
    rc, out = _run(["ollama", "pull", model], timeout=timeout)
    return rc == 0, out.strip().splitlines()[-3:][0] if out else "(no output)"


def _smoke(models: list[str], out_tsv: Path) -> dict[str, tuple[str, str, int]]:
    """Run smoke gate via subprocess. Return {model: (status, strippable, etoks)}."""
    cmd = ["ollama-bench", "smoke", "-m", *models, "-o", str(out_tsv)]
    rc, out = _run(cmd, timeout=300)
    if rc != 0 or not out_tsv.exists():
        return {}
    rows: dict[str, tuple[str, str, int]] = {}
    with out_tsv.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows[row["name"]] = (
                row["status"],
                row.get("strippable", "0"),
                int(row.get("etoks", "0") or 0),
            )
    return rows


def _deep(models: list[str], tasks: list[str], out_tsv: Path) -> list[dict]:
    """Run deep bench via subprocess. Return list of result rows."""
    cmd = ["ollama-bench", "deep", "-c", *models, "-t", *tasks, "-o", str(out_tsv)]
    rc, out = _run(cmd, timeout=1800)
    if rc != 0 or not out_tsv.exists():
        return []
    rows = []
    with out_tsv.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)
    return rows


def _render_report(
    candidates: list[str],
    smoke_results: dict[str, tuple[str, str, int]],
    deep_rows: list[dict],
    survivors: list[str],
    strip_required: list[str],
    dropped: list[str],
    pull_log: dict[str, str],
    run_id: str,
    tasks: list[str],
) -> str:
    """Single markdown report: pull log → smoke gate → deep scores → recommendations."""
    lines = [
        f"# candidates report ({run_id})",
        "",
        f"**Candidates tested**: {len(candidates)}",
        f"**Survived smoke**: {len(survivors)}",
        f"**Survived with strip-required handling**: {len(strip_required)}",
        f"**Dropped at smoke**: {len(dropped)}",
        "",
        "## 1. Pull log",
        "",
        "| model | status |",
        "|---|---|",
    ]
    for m in candidates:
        status = "OK" if m in pull_log and "success" in pull_log[m].lower() else "FAIL"
        lines.append(f"| `{m}` | {status} |")
    lines.append("")

    lines.extend(["## 2. Smoke classification", "", "| model | status | handling | etoks |", "|---|---|---|---|"])
    for m in candidates:
        if m in smoke_results:
            status, strippable, etoks = smoke_results[m]
            handling = "strip-required" if strippable == "1" else ("clean" if status == "ok" else "drop")
            lines.append(f"| `{m}` | {status} | {handling} | {etoks} |")
        else:
            lines.append(f"| `{m}` | (no result) | drop | — |")
    lines.append("")

    if survivors:
        lines.extend(
            [
            f"## 3. Deep bench ({len(tasks)} tasks, clean + strip-required survivors)",
                "",
                "| task | model | score |",
                "|---|---|---|",
            ]
        )
        # Sort: task asc, score desc
        sorted_rows = sorted(deep_rows, key=lambda r: (r["task"], -float(r["score"])))
        for r in sorted_rows:
            lines.append(f"| {r['task']} | `{r['model']}` | {r['score']} |")
        lines.append("")

    lines.extend(
        [
            "## 4. Recommendations",
            "",
            "- **Re-bench saturated** (deep = 7.00): re-run `ollama-bench tie-break -w <survivor> <incumbent>` for hard-prompt discrimination.",
            "- **Compare vs incumbent**: see `RANKING.md` for current top-5 per task.",
            "- **Strip-required is benchable**: use cleaned output plus a runtime output filter in consuming tools.",
            "- **Drop at smoke**: only for non-strippable leaks, empty outputs, or load failures.",
            "",
            "## 5. Next steps",
            "",
            "1. Read `RANKING.md` for incumbent ranks.",
            "2. For any `7.00 SAT` deep score, run tie-break vs the incumbent (see `topics/bench-methodology.md`).",
            "3. For models that win tie-break hard prompts: update `RANKING.md` + `shared/config.py::TASKS` + `prompt-improve` chain (cross-project rewire).",
            "4. Delete losers: `ollama rm <dropped>`.",
        ]
    )
    return "\n".join(lines) + "\n"


def cmd_candidates(args: argparse.Namespace) -> int:
    if not args.models:
        print("candidates: error: at least one model required", file=sys.stderr)
        return 1

    run_id = time.strftime("%Y%m%d-%H%M%S")
    out_dir = result_path("").parent
    out_dir.mkdir(parents=True, exist_ok=True)
    smoke_tsv = out_dir / f"candidates-smoke-{run_id}.tsv"
    deep_tsv = out_dir / f"candidates-deep-{run_id}.tsv"
    md_path = out_dir / f"candidates-{run_id}.md"

    tasks = list(args.tasks) if args.tasks else list(DEFAULT_TASKS)

    # 1. Pull each model (sequential, ~5-10 min/model)
    pull_log: dict[str, str] = {}
    print(f"[1/3] Pulling {len(args.models)} models...", file=sys.stderr)
    for m in args.models:
        ok, tail = _ollama_pull(m)
        pull_log[m] = "success " + tail if ok else "FAIL " + tail
        print(f"  {'OK' if ok else 'FAIL'} {m} — {tail}", file=sys.stderr)
        if not ok and not args.keep_on_pull_fail:
            print(
                "  stopping (use --keep-on-pull-fail to continue past failures)", file=sys.stderr
            )
            break

    # 2. Smoke gate (all models)
    print(f"[2/3] Smoke gating {len(args.models)} models...", file=sys.stderr)
    smoke_results = _smoke(args.models, smoke_tsv)
    survivors = [
        m
        for m in args.models
        if m in smoke_results
        and (smoke_results[m][0] == "ok" or smoke_results[m][1] == "1")
    ]
    strip_required = [m for m in survivors if smoke_results[m][1] == "1"]
    dropped = [m for m in args.models if m in smoke_results and m not in survivors]

    # 3. Deep bench (survivors only)
    deep_rows: list[dict] = []
    if survivors:
        print(
            f"[3/3] Deep bench on {len(survivors)} survivors × {len(tasks)} tasks...",
            file=sys.stderr,
        )
        deep_rows = _deep(survivors, tasks, deep_tsv)

    # 4. Write report
    report = _render_report(
        candidates=args.models,
        smoke_results=smoke_results,
        deep_rows=deep_rows,
        survivors=survivors,
        strip_required=strip_required,
        dropped=dropped,
        pull_log=pull_log,
        run_id=run_id,
        tasks=tasks,
    )
    md_path.write_text(report)
    print(f"\n[OK] report → {md_path}", file=sys.stderr)
    print(f"[OK] smoke tsv → {smoke_tsv}", file=sys.stderr)
    if deep_rows:
        print(f"[OK] deep tsv → {deep_tsv}", file=sys.stderr)
    return 0


def add_parser(sub, parent) -> None:
    p = sub.add_parser(
        "candidates",
        parents=[parent],
        help="End-to-end candidate sweep: pull + smoke + deep + MD report.",
        description=(
            "Orchestrates the manual workflow done across rounds 3-4: pull each HF model, "
            "smoke gate (leak detection), deep bench on survivors, write a single MD report "
            "with recommendations. Reuses `smoke` and `deep` slices via subprocess (no "
            "slice-to-slice imports per CLAUDE.md). Tie-break remains manual (needs human "
            "judgment on saturated scores)."
        ),
    )
    p.add_argument(
        "models", nargs="*", help="HF model tags to test (e.g. hf.co/owner/model:Q4_K_M)"
    )
    p.add_argument(
        "--tasks",
        nargs="+",
        default=None,
        help=f"Tasks for deep bench (default: {' '.join(DEFAULT_TASKS)})",
    )
    p.add_argument(
        "--keep-on-pull-fail",
        action="store_true",
        help="Continue past pull failures (default: stop on first failure)",
    )
    p.set_defaults(cmd=cmd_candidates)
