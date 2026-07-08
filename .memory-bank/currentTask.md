# Current Task
<!-- task-guidance:start -->
## Active Implementation Guide
- Source: codex-update-plan
- Plan: `docs/plans/benchmark-refactor-2026-07-08.md`
- Objective: Benchmark Refactor Plan - 2026-07-08
- Checklist: use the CLI native tracker (`TaskCreate/TaskUpdate` in Claude, `update_plan` in Codex); keep it current after each step.
- Step 1: `deep` no longer ranks models mostly by leak/speed/concision saturation.
- Step 2: Canonical tasks keep the same public keys: `improve`, `codeq_sum`,
- Step 3: Each canonical task has multiple varied cases and task-specific scoring.
<!-- task-guidance:end -->

> Project stable — no active multi-session work

The 7-phase build + re-bench cycle is complete. The package is live at
https://github.com/heldigard/ollama-bench with 72 passing tests.

## When a new task surfaces

- **New fine-tune to evaluate** → `ollama-bench smoke && ollama-bench deep && ollama-bench tie-break -w <winners> && ollama-bench bug-finding -m <winners>`
- **New task type** → add `features/<slice>/` + register in `cli.py::_SLICES` + test
- **Ollama upgrade** → re-smoke the lineup to confirm no regression
- **DO NOT** pull Q5/Q6/Q8 variants of existing Q4 winners — see `topics/quant-comparison-2026-07-04.md`

## Verification (always green)

- `python3 -m pytest tests/ -q` → 72 passed
- `ruff check src/ tests/ scripts/` → clean
- `ollama-bench --help` → lists 14 sub-commands