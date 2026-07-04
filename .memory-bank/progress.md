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

- `~/bench/ollama/results_smoke_all.tsv` — 63 models × leak status (2026-07-04)
- `~/bench/ollama/results_deep_bench.tsv` — 40 candidates × 5 tasks (2026-07-04)
- `~/bench/ollama/RANKING_TIEBREAK.md` — 23 winners × 5 hard tasks (2026-07-04)
- `~/bench/ollama/LFM_RANKING.md` — 9 LFM variants × codeq summary (2026-07-04)

The CLI `ollama-bench` is the new way to generate these.