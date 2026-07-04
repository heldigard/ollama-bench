"""deep — 5-task × N model bench.

Canonical harness tasks: improve, codeq_sum, smart_trim, web_synth, code_gen.
First-pass scoring (saturates at 7.0 for fast+clean responses — use tie_break
to discriminate when many models saturate).

# vs-soft-allow  — end-to-end pipeline (prompts → run → score → rank → write).
# Splitting would force callers to know which helper to invoke.
"""
from __future__ import annotations

import argparse
import csv
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

from ollama_bench.shared.config import NUM_PREDICT_DEFAULT
from ollama_bench.shared.ollama import CallOpts, call, get_model_names
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import first_pass_score

PROMPTS: dict[str, dict] = {
    "improve": {
        "budget_words": 120,
        "items": [
            ("improve_v1", "haz que el dashboard cargue mas rapido, esta lentisimo"),
            ("improve_v2", "fix the auth bug, users cant login"),
        ],
    },
    "codeq_sum": {
        "budget_words": 30,
        "items": [
            ("sum_v1",
             "Summarize this function in ONE sentence, max 30 words. NO preamble, no code blocks.\n\n"
             "async function sendChatMessage(trimmed: string) {\n"
             "  if (!trimmed || sending.value) return;\n"
             "  draft.value = '';\n"
             "  try {\n"
             "    await api.post('/chat', { text: trimmed });\n"
             "  } catch (e) {\n"
             "    error.value = e.message;\n"
             "  }\n"
             "}"),
            ("sum_v2",
             "Summarize in ONE sentence, max 30 words. NO preamble.\n\n"
             "function chunkText(text, maxTokens) {\n"
             "  const sentences = text.split(/(?<=[.!?])\\s+/);\n"
             "  const out = [];\n"
             "  let buf = '';\n"
             "  for (const s of sentences) {\n"
             "    if ((buf + s).split(/\\s+/).length > maxTokens) {\n"
             "      out.push(buf.trim());\n"
             "      buf = s;\n"
             "    } else buf += ' ' + s;\n"
             "  }\n"
             "  if (buf) out.push(buf.trim());\n"
             "  return out;\n"
             "}"),
        ],
    },
    "smart_trim": {
        "budget_words": 150,
        "items": [
            ("trim_v1", """Compress to handoff bullet list. Keep: task, current step, decisions, next action, blockers. 4-8 bullets, no preamble.

[Earlier] User asked about Python venv setup on WSL2. Assistant explained uv vs pip, recommended uv. Created .venv via 'uv venv'.
[Earlier] Discussion about why their existing imports broke. Root cause: site-packages vs .venv/lib conflict. Fixed by removing PYTHONPATH override.
[Now] User: 'pytest no encuentra los tests'. Output: 'collected 0 items'. Investigating tests/ dir missing __init__.py, or conftest.py not at root.
[Now] User: 'tambien falla ruff, dice no module'. Same root cause - ruff needs the .venv on path.
[Decision] Stay on uv, drop pip completely. Add conftest.py at project root, reinstall dev deps in .venv.
[Blocked] None."""),
        ],
    },
    "web_synth": {
        "budget_words": 180,
        "items": [
            ("synth_v1", """Synthesize a 3-paragraph summary (no preamble) of the following sources. Cite as [1], [2], etc.

[1] RFC 9457 (2023) "Problem Details for HTTP APIs" defines a standard format for error responses (application/problem+json) with type, title, status, detail, instance fields.
[2] Microsoft REST API Guidelines (2024) recommend using problem+json for 4xx/5xx responses; include a correlation id in 'instance' for tracing.
[3] Spring Boot 3.2+ has built-in ProblemDetail support via ResponseEntityExceptionHandler and @RestControllerAdvice."""),
        ],
    },
    "code_gen": {
        "budget_words": 90,
        "items": [
            ("code_v1",
             "Write a Python function `validate_email(s: str) -> bool` using ONLY stdlib (re). Handle None/empty/whitespace. Return False on invalid. No imports beyond re. No docstring, no comments, just the function."),
            ("code_v2",
             "Write a Python function `chunk_lines(text: str, max_chars: int) -> list[str]` that splits text into chunks of <= max_chars, splitting on '\\n' first, then on ' ' if a line is too long. No external deps. Just the function, no comments."),
        ],
    },
}

WORKERS = 4


def _smoke_ok_candidates() -> list[str]:
    """Read smoke TSV and return models with status=ok. Falls back to all if no TSV."""
    smoke_tsv = result_path("smoke_all")
    if not smoke_tsv.exists():
        return get_model_names()
    candidates: list[str] = []
    with smoke_tsv.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r["status"] == "ok":
                candidates.append(r["name"])
    return candidates


def run_model(model: str, tasks: list[str], opts: CallOpts) -> dict:
    """Run model across all selected tasks. Returns {model: {task: [scores]}}."""
    out: dict = {task: [] for task in tasks}
    for task in tasks:
        cfg = PROMPTS[task]
        budget = cfg["budget_words"]
        for pid, prompt in cfg["items"]:
            res = call(model, prompt, opts=opts)
            out[task].append({"pid": pid, "sc": first_pass_score(task, res, budget)})
    return {model: out}


def _aggregate(results: dict, tasks: list[str]) -> dict[str, list]:
    """Compute mean per-task score; sort descending."""
    per_task: dict[str, list] = {t: [] for t in tasks}
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r:
            continue
        for t in tasks:
            items = r.get(t, [])
            scores = [it["sc"] for it in items if "sc" in it]
            if scores:
                per_task[t].append((m, round(mean(scores), 2)))
    for t in per_task:
        per_task[t].sort(key=lambda x: -x[1])
    return per_task


def _write_outputs(per_task: dict[str, list], tasks: list[str], base: Path) -> None:
    """Write TSV + MD summary."""
    tsv_path = base.with_suffix(".tsv")
    with tsv_path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["task", "rank", "score", "model"])
        for t, ranked in per_task.items():
            for i, (m, s) in enumerate(ranked, 1):
                w.writerow([t, i, s, m])
    md_path = base.with_suffix(".md")
    with md_path.open("w") as f:
        f.write("# Deep-bench — top-5 per task\n\n")
        for t, ranked in per_task.items():
            f.write(f"\n## {t}\n\n| # | Score | Model |\n|---|---|---|\n")
            for i, (m, s) in enumerate(ranked[:5], 1):
                f.write(f"| {i} | {s} | `{m}` |\n")
    print(f"Wrote {tsv_path}\nWrote {md_path}", file=sys.stderr)


def cmd_deep(args: argparse.Namespace) -> int:
    """`ollama-bench deep` entry point."""
    candidates = args.candidates if args.candidates else _smoke_ok_candidates()
    if not candidates or (not args.candidates and not result_path("smoke_all").exists()):
        candidates = get_model_names()
        print(f"# No smoke TSV; falling back to all {len(candidates)} installed models", file=sys.stderr)
    tasks = args.tasks if args.tasks else list(PROMPTS.keys())
    total_prompts = sum(len(PROMPTS[t]["items"]) for t in tasks)
    print(f"# Deep-bench: {len(candidates)} candidates × {total_prompts} prompts", file=sys.stderr)
    opts = CallOpts(num_predict=NUM_PREDICT_DEFAULT, num_ctx=4096)

    results: dict = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_model, m, tasks, opts): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(candidates)}] {m[:60]}", file=sys.stderr, flush=True)

    per_task = _aggregate(results, tasks)
    base = Path(args.output) if args.output else result_path("deep_bench")
    _write_outputs(per_task, tasks, base)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    """Attach deep subcommand to root CLI."""
    p = sub.add_parser("deep", parents=[parent], help="5-task × N model bench.")
    p.add_argument("-c", "--candidates", nargs="*", help="Models to bench (default: smoke-OK list).")
    p.add_argument("-t", "--tasks", nargs="*", choices=list(PROMPTS.keys()),
                   help="Tasks to include (default: all).")
    p.add_argument("-o", "--output", help="Output TSV base path (default: cache dir).")
    p.set_defaults(cmd=cmd_deep)
