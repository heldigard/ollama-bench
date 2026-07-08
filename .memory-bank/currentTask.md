# Current Task
> 2026-07-08 (PM): GPU-safe bench suite + full pipeline running. Consumer rewires still pending.

## Completed (this session)
- Fixed CRITICAL resume data-loss bug (deep JSONL now append-only; pinned by regression test).
- Removed parallel ThreadPoolExecutor from bug_finding/tool_call/pdf_extract (overheat root cause) → shared `paced()`.
- All benches: `--cooldown`/`--temp-limit`; smoke gained `--resume` + incremental.
- Pipeline: `scripts/run_pipeline.sh` + `scripts/tie_winners.py`. Launched detached.
- 194/194 tests pass; ruff + shellcheck clean.

## Running now
- deep 14/30 → orchestrator (PID 45450) auto-runs bug-finding/tool-call/pdf-extract/pdf-ocr → tie-break.

## Pending consumer rewires (from prior bench, still open)
- ~/prompt-improve: improve chain → OmniCoder primary
- ~/smart-trim: smart_trim → Openclaw primary
- ~/web-research: web_synth → DeltaCoder primary
- ~/.claude/scripts/diff-review.py: bug_finding → DeltaCoder

## Latest Durable State
- New champions: Openclaw (smart_trim, code_gen), DeltaCoder (web_synth, bug_finding), OmniCoder (improve)
- SetneufPT demoted from improve #1 to #8; still codeq_sum #2
- DeepSeek-V4-Flash: strippable but last everywhere — not recommended
- lift: pdf_ocr fallback (11.12, 112 tok/s)

## When a new task surfaces
- **New fine-tune to evaluate** → `ollama-bench candidates <model...>` or `smoke` + `deep`.
- **New task type** → add `features/<slice>/` + register in `cli.py::_SLICES` + tests.
- **Ollama upgrade** → re-run `ollama-bench smoke` and at least canonical `deep`.
- **Reasoning leak model** → do not hard-drop if `strippable=1`; benchmark with cleaned output and record runtime handling.
