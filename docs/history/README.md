# docs/history/ — Deprecated bench scripts

These 40+ Python scripts are **the historical record of model evaluation rounds
from 2026-06-27 through 2026-07-04**, before ollama-bench was a proper package.

## Why they exist here

- They are the raw, throwaway scripts that grew `~/bench/ollama/` from 7 → 60+
  files across 6+ rounds of evaluation.
- They each test a single candidate or family (`bench_qwopus_v3.py` only tests
  the qwopus v3 family; `bench_composer_quants.py` only tests composer quants).
- The canonical 9-slices in `src/ollama_bench/features/` REPLACE these.

## How to use

These are **NOT in the ollama-bench CLI**. They are kept here as:
1. **Historical record** of what was tested and how
2. **Reference for new bench designs** — see how a specific family was benched
3. **Debugging aid** — if a regression appears, compare old vs new bench output

To re-evaluate a model today, use the new package:

```bash
ollama-bench smoke                    # 1-prompt leak gate
ollama-bench deep -t improve          # specific task
ollama-bench tie-break -w 'model a' 'model b'
ollama-bench report build              # render ranking
```

## Categories

| prefix | purpose | kept because |
|---|---|---|
| `bench_round*.py` | 6 evaluation rounds (June 27) | historical baseline |
| `bench_qwopus*.py` | qwopus family (4 variants) | variant-specific learnings |
| `bench_qwen35*.py` | qwen3.5 family (3 variants) | bug-finding + niche + Q8 |
| `bench_composer_quants*.py` | composer quants (Q4_K_M, Q6_K, Q8_0) | quant shootout data |
| `bench_omnicoder.py`, `bench_hauhau.py` | single-family evals | family-specific |
| `bench_new*.py` | "new model" evals (catch-all) | per-pull evaluation |
| `bench_improve_real.py` | long-form improve | the deep of improve task |
| `bench_webresearch.py` | web_research synth (4 sources) | synth judgment |
| `bench_triage.py`, `bench_untested.py`, `bench_extra.py` | model triage | pre/post prune bookkeeping |
| `smoke_qwen35.py` | qwen3.5-specific smoke | variant-specific |
| `quality_*.py` | quality_test helpers | LLM-as-judge scaffolding |
| `embed_eval.py`, `embedding_eval_*.py` | embedding evaluation | now in `embedding` slice |
| `judge.py`, `judge_deep.py` | LLM-as-judge helpers | now in `judge` slice |
| `smoke_all.py`, `deep_bench.py`, `tie_break.py`, `lfm_bench.py` | the 4 NEW scripts I wrote 2026-07-04 | superseded by package slices (smoke/deep/tie_break/lfm_variant) |
| `bench.py`, `bench_candidates.py` | the original 4-domain bench (June 27) | superseded by `multi_domain` slice |
| `bench_deep.py` | 5-task deep bench (early) | superseded by `deep` slice |

## When to delete

Delete this directory once ollama-bench has been in production for 6+ months
and the bench methodology has stabilized. Until then, the scripts are
authoritative when investigating regressions.

## Restoration

If you need to re-run a historical bench, copy the script out of `docs/history/`
and execute it standalone. The scripts are not part of the ollama-bench
package — they are raw Python with hardcoded paths.