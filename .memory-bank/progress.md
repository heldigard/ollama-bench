# Progress
> Bench history for ollama-bench

## 2026-07-04 — Initial v0.1.0 release

- 2026-07-04T15:30:00Z | status:completed | Vertical-slice split: 40+ scripts in `~/bench/ollama/` migrated to `~/ollama-bench/` package (9 vertical slices: smoke, deep, tie_break, lfm_variant, multi_domain, judge, embedding, report, list).
- 2026-07-04T15:25:00Z | status:completed | 46 tests passing (smoke/deep/tie_break/lfm_variant/judge/ollama/scorer/paths/layout).
- 2026-07-04T12:30:00Z | status:completed | Bench session: 63+ models → 51 evaluated → 23 unique winners via combined-rank (avg of first-pass + tie-break rank).
- 2026-07-04T12:00:00Z | status:completed | 3 DEAD models deleted + re-pulled: Mobius (still broken — Ollama Q4_0 gemma4 incompat), SetneufPT (still broken — qwen3next MTP init fail), VladimirGav (works now — was slow/leaky first time).

## Earlier bench rounds (June 27 — preserved in `~/bench/ollama/results_*/`)

- 6 rounds of model evaluation: triage + 4 deep + 1 quick = 19 models tested, 31+ deleted.
- Final lineup: 7 working + 1 utility = 8 total. ~33 GB.

## Bench results carried over (raw TSVs)

Historical results from earlier rounds (pre-package) live in `docs/history/results/`.
Current re-bench (2026-07-04, Ollama 0.31.1) outputs:

- `~/.cache/ollama-bench/results/smoke_all.tsv` — 64 models × leak status
- `~/.cache/ollama-bench/results/deep_bench.{tsv,md}` — 47 candidates × 5 tasks
- `~/.cache/ollama-bench/results/tiebreak_ranking.md` — 24 winners × 5 hard tasks
- `~/.cache/ollama-bench/results/bug_finding.md` — 15 candidates × 2 diffs

The CLI `ollama-bench` is the way to regenerate these.
## 2026-07-04 — Re-bench on unified Ollama 0.31.1

- 2026-07-04T19:00:00Z | status:completed | Re-bench after Ollama server unification (Windows+WSL → single WSL 0.31.1). Smoke 64 models → 47 OK. Deep 5 tasks × 47. Tie-break 24 saturated winners. Bug-finding NEW slice (15 candidates). Combined-rank top-5 → 16 LLM winners + 2 embeddings = 18 models kept (76 GB, was 325 GB).
- 2026-07-04T19:05:00Z | status:completed | 46 non-winners deleted. ex-DEAD verdicts (Mobius, SetneufPT) corrected — they load fine on 0.31.1; SetneufPT is now smart_trim #1. Mobius ranks low (deleted on merit).
- 2026-07-04T19:10:00Z | status:completed | Harness wiring updated: 8 points (warmup/browser/diff-review/pdf/project-memory/CODEQ_SUMMARY_MODEL/OLLAMA_SYNTH_MODEL/prompt_improve chain) → new top-2 winners per task.
- 2026-07-04T19:15:00Z | status:completed | bug_finding slice added (features/bug_finding/) — diff-with-known-bugs + recall scorer. composer Q8_0 kept (#5 bug-finding).
