# Benchmark Refactor Plan - 2026-07-08

Objective: rebuild `ollama-bench` so local Ollama model rankings use task-specific
metrics with enough variance to choose practical primary/fallback models for the
CLI ecosystem.

## Acceptance

- `deep` no longer ranks models mostly by leak/speed/concision saturation.
- Canonical tasks keep the same public keys: `improve`, `codeq_sum`,
  `smart_trim`, `web_synth`, `code_gen`.
- Each canonical task has multiple varied cases and task-specific scoring.
- Bench commands still emit existing TSV/MD outputs and also emit detail JSONL
  where useful.
- Unit tests cover new metrics and guard against high-score saturation.
- All installed Ollama LLM models are re-benched after the refactor.
- Embedding models are evaluated with embedding-specific commands.
- Related projects (`cli-orchestration`, `cheap-llm`, `prompt-improve`) are
  reviewed for task routing opportunities.

## Working Design

- Keep `first_pass_score` for smoke/legacy compatibility, but move `deep` to
  semantic task scorers.
- Add a shared canonical-task module with:
  - richer case sets per task,
  - per-case metadata,
  - component-level score details,
  - deterministic/heuristic checks that do not require cloud judge calls.
- Keep `tie-break` as a hard prompt suite but reuse the same scoring layer.
- Add a discrimination check: tasks where too many models collapse to one score
  are considered weak and need redesign.

## Deferred By Design

- Executing generated model code in a sandbox. This can improve `code_gen`, but
  it needs an isolated no-network runner and timeouts.
- LLM-as-judge pairwise Elo. Useful for qualitative tasks, but it adds cloud
  cost, judge bias, and non-determinism.
- Full local-vs-cloud router benchmark. This pass will produce the route matrix
  and recommendations; router training/eval can follow in `cheap-llm`.

## Steps

1. Baseline current tie/saturation metrics from cached results.
2. Implement canonical task cases and scorers.
3. Wire `deep` and `tie-break` to new scorers and detail output.
4. Expand deterministic task slices where low sample count causes ties.
5. Update tests and run full local test suite.
6. Run smoke/deep/tie-break/specialized benches on installed models.
7. Research/select any high-value Hugging Face GGUF candidates and bench them.
8. Review related repos and write routing recommendations.
9. Update `.memory-bank` with durable outcomes.
