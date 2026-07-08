# Current Task
> Project stable after 2026-07-08 benchmark refactor.

No active multi-session implementation task.

## Latest Durable State

- Canonical `deep` scorers were refactored to reduce score saturation.
- Rebench artifacts: `~/.cache/ollama-bench/results/deep_refactor_20260708.*`.
- Current ranking/config: `RANKING.md` + `src/ollama_bench/shared/config.py`.
- Deep context: `topics/benchmark-refactor-2026-07-08.md`.

## When a new task surfaces

- **New fine-tune to evaluate** → `ollama-bench candidates <model...>` or `smoke` + `deep`.
- **New task type** → add `features/<slice>/` + register in `cli.py::_SLICES` + tests.
- **Ollama upgrade** → re-run `ollama-bench smoke` and at least canonical `deep`.
- **Reasoning leak model** → do not hard-drop if `strippable=1`; benchmark with cleaned output and record runtime handling.
