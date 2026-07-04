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
- 2026-07-04T19:08:55Z | status:completed | session:cb6822df-6550-4e12-b29e-bcbfaf8ca306 | claude: session done
- 2026-07-04T20:00:00Z | status:completed | Quant comparison (Q4 vs Q5 vs Q6 vs Q8) for 4B/e4b/e2b winners. Pulled unsloth E4B Q5/Q8 + E2B Q8 + qwen3.5:4b-q8_0. Ran smoke+deep+tie-break (9 models). RESULT: Q8 does NOT improve quality — confirms "Q4_K_M is the quality ceiling". Same-publisher: unsloth E4B Q5 (8.89 improve) > Q8 (8.59); batiai e4b Q4≈Q6; batiai e2b Q4 > Q6. Deleted 6 higher-quant variants (~27 GB freed). See topics/quant-comparison-2026-07-04.md.
- 2026-07-04T20:23:01Z | status:completed | 2026-07-04 bench v0.2.0-improve: think-strip scoring mode + seed reproducibility + leak-pattern expansion (14 patterns) + config-drift fixes across ollama-bench/codeq/prompt-improve + new-benchmarks roadmap topic. 90 tests pass. New HF candidates pulling for eval.
- 2026-07-04T20:42:36Z | status:completed | 2026-07-04 new-models bench: 4 HF candidates pulled + benched. huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus = NEW bug_finding #1 (17.98 > incumbent cryptidbleh 15.21) + saturated smart_trim/web_synth + top tool_call 9.82. kwangsuklee reasoning = bug_finding 15.00 + --strip demonstrator (keep). yuxinlu1 Opus4.8 + DuoNeural abliterated = below incumbents (drop candidates, ~15GB). Topic: topics/new-models-bench-2026-07-04.md.
- 2026-07-04T20:58:50Z | status:completed | 2026-07-04 round-2 bench: composer v2-3.5x-tau2 (yuxinlu1) KEPT — bug_finding #2 (15.86 > cryptidbleh 15.21 > xentriom Q8_0 14.26), code_gen tied #1 (6.0), improve #2-tier (3.08), tool_call 9.83. bge-m3 KEPT (multilingual embed, dim 1024 — needs re-index vs 768-d embeddinggemma, eval deferred). Lineup now 18 LLM + 3 embed = 21. RANKING_HISTORY: 70 tested, 21 kept, 49 elim.
- 2026-07-04T21:21:40Z | status:completed | 2026-07-04 iter-2: embedding-retrieval slice landed (P0, 7 tests, hand-rolled cosine, decides embed). Live bench: bge-m3 TIES embeddinggemma (MRR 1.000 both, nomic 0.875) -> no reindex, embeddinggemma stays primary, bge-m3 alt. _post_json DRY refactor (call+embed share, nesting<=3). Layout-gate boundary-regex fix. 105 tests pass. Pulling Qwen3-Coder-30B-A3B MoE (3B active, user request) + slyfox1186 functiongemma 9B (Opus 4.6 tool-calling) for bench.
