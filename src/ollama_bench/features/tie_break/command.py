"""tie_break — re-bench tied candidates with harder prompts.

Use when first-pass `deep` saturates (20+ models all at 7.0). Harder prompts +
structural scoring (no cap) discriminates quality.

# vs-soft-allow  — end-to-end pipeline (prompts → run → score → rank → MD).
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import (
    quality_score,
    structural_score,
    tie_break_score,
)

PROMPTS: dict[str, dict] = {
    "improve": {
        "budget": 250,
        "v_hard": """Rewrite this vague prompt into a structured spec.

Original: "make my api faster, sometimes slow"

Your rewrite MUST have these explicit sections:
## GOAL (one sentence)
## ASSUMPTIONS (what I had to guess — list 2-3)
## FILES (likely files to touch, or 'unknown')
## STEPS (numbered, 3-5 max)
## ACCEPTANCE (one measurable check)

Be specific. No generic advice. Output ONLY the spec, no preamble.""",
        "scorer": lambda out: structural_score(
            out,
            expected_sections=("## GOAL", "## ASSUMPTIONS", "## STEPS", "## ACCEPTANCE"),
        ),
    },
    "codeq_sum": {
        "budget": 35,
        "v_hard": """Summarize this function in ONE sentence, max 30 words. Mention the most important behavior.

async function subscribeToTopic(topic, handler) {
  if (subscriptions.has(topic)) return false;
  const controller = new AbortController();
  const conn = await openStream(topic, { signal: controller.signal });
  subscriptions.set(topic, { controller, handler });
  conn.on('data', msg => {
    if (msg.type === 'error') {
      controller.abort();
      unsubscribe(topic);
    } else handler(msg);
  });
  return true;
}""",
        "scorer": lambda out: quality_score(
            out,
            keywords=("abort", "unsubscribe", "stream", "topic", "error"),
        ),
    },
    "smart_trim": {
        "budget": 200,
        "v_hard": """Compress to handoff. KEEP: task, decisions, current step, next action, blockers. 5-10 bullets. NO preamble.

[Earlier 6 turns ago] User complained about slow CI. Assistant asked for timing breakdown. Got: install=4min, test=8min, build=12min, deploy=3min. Total ~27min.
[Earlier 5 turns ago] Discussed nx vs lerna. Decided nx because already using it for caching.
[Earlier 3 turns ago] Enabled nx affected:only in CI. Tried. Still 18min. Not enough.
[Earlier 2 turns ago] Investigated vitest vs jest. vitest 2x faster for their tests. Migration underway.
[Now] User: 'vitest migration done, but the snapshot tests still slow'. Assistant found: 14 snapshot tests with deeply nested objects taking 2.1s each.
[Now] User: 'tried happy-dom vs jsdom — happy-dom 30% faster'. Confirmed via local run.
[Decision] Drop snapshots for non-visual assertions. Use plain object comparison. Keep snapshots ONLY for SVG/PNG renders. Estimated savings: 8min.
[Blocked] None.
[Next] PR the snapshot-delete changes (branch: drop-snapshots-v1). Re-run CI. If <10min, ship. If not, look at test parallel config (currently 2 workers).""",
        "scorer": lambda out: structural_score(
            out, must_have=("task", "decision", "next", "block", "current")
        ),
    },
    "web_synth": {
        "budget": 220,
        "v_hard": """Synthesize a 3-paragraph summary (cite as [1][2][3]). If sources disagree, surface the disagreement.

[1] Anthropic 2024 announcement: Claude 3.5 Sonnet scores 64.3% on SWE-bench Verified (release date: Oct 2024).
[2] Anthropic blog (Mar 2025) claims Claude 3.7 Sonnet scores 62.3% on SWE-bench Verified.
[3] Independent benchmark by The Decoder (Dec 2025) reports Claude 3.7 Sonnet at 70.3% on the SAME benchmark.

Note: there's a discrepancy between sources [2] and [3] about the same model/benchmark. Surface it.""",
        "scorer": lambda out: structural_score(
            out, must_have=("62.3", "70.3", "[3]")
        ) + (3 if "discrep" in out.lower() or "disagree" in out.lower() else 0),
    },
    "code_gen": {
        "budget": 120,
        "v_hard": """Write a Python function:

def unique_preserve_order(items: list[str | None]) -> list[str]:
    \"\"\"Return unique items in first-seen order. Skip None. Treat '' as falsy, skip it.\"\"\"

- No imports.
- No docstring, no comments. Just the function.
- Handle None items without crashing.
- Empty input → empty output.""",
        "scorer": lambda out: quality_score(
            out, keywords=("def unique_preserve_order", "none", "if", "return")
        ) + (5 if "None" in out and "return" in out else 0),
    },
}


def run_model(model: str, opts: CallOpts) -> dict:
    """Run a single model across all hard tasks. Returns {model: {task: score}}."""
    out: dict = {}
    for task, cfg in PROMPTS.items():
        res = call(model, cfg["v_hard"], opts=opts)
        out[task] = tie_break_score(res, cfg["scorer"], cfg["budget"])
    return {model: out}


def _aggregate(results: dict, tasks: list[str]) -> dict[str, list]:
    """Aggregate per-task scores into ranked lists."""
    per_task: dict[str, list] = {t: [] for t in tasks}
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r:
            continue
        for t in tasks:
            sc = r.get(t)
            if isinstance(sc, (int, float)):
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
    with out_path.open("w") as f:
        f.write("# Ollama Tie-Break — Hard Prompts + Structural Scoring\n\n")
        f.write("Each task uses a HARDER prompt + structural scoring (no 7.0 cap).\n")
        f.write("Range -5 to +15. Higher = better.\n\n")
        for task, ranked in per_task.items():
            f.write(f"\n## {task}\n\n| # | Score | Model |\n|---|---|---|\n")
            for i, (m, s) in enumerate(ranked, 1):
                f.write(f"| {i} | {s:.2f} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
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
