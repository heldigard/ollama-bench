# session-handoffs
> Deep memory topic. Read on demand; keep entries factual.

## 2026-07-04T16:39:01
Method: ollama-qwen3.5:4b
Session: unknown

## Current Objective (from current-objective.json)
**Task**: bien, haz limpieza de ruido y commit. Luego vuelves repetir todo lo hecho en esta session: mejorar benchmarks, buscar modelos que quizas nos sirvan, probarlos, clasificar, reconectar, actualizar memory, limpiar perdedores y ruido
**Phase**: Ship
**Acceptance**: same regex, same check, same suggestion
**Next**: Think -> Plan -> Build -> Review -> Test -> Validate -> Ship -> Reflect

## Preserved Negative Constraints
- DO NOT** pull Q5/Q6/Q8 variants of existing Q4 winners — see `topics/quant-comparison-2026-07-04.md

**Task**: Ship Iter-2 benchmarks, classify models (keep functiongemma, drop MoE), align registry.
**Acceptance**: 72 passing tests; clean ruff; lineup aligned to RANKING.md; no Q5/Q6/Q8 pulls of existing winners.
**Verified**: `python3 -m pytest` (105 pass); `ruff check` (clean); MoE bench complete (slow, weak on code_gen/bug_finding vs dense 9-12B) → culled; functiongemma kept (#1 tool_call). Registry count aligned: ollama list=22 distinct blobs.
**Current**: None pending. Session closed.
**Errors**: `uv.lock` spurious (project uses hatchling); MoE pull initially stalled then completed 14GB but failed performance hypothesis.
**Decisions**: 
- Embedding retrieval slice landed; bge-m3 ties embeddinggemma on MRR/recall@5 → no reindex, keep gemma primary.
- functiongemma (Qwen3.5-9B+Opus) = tool_call #1 + code_gen tier 7.0 → KEEP.
- Qwen3-Coder-30B-A3B MoE hypothesis rejected (20s runtime, weak scores) → DROP to free 14GB.
- Composer-v2 tag duplication (`:Q4_K_M` vs `:latest`) resolved via dedup.
**Next**: None. Ready for new task or maintenance cycle.
**Files**: 
- `/home/eldi/ollama-bench/.memory-bank/progress.md` (updated iter-2 complete)
- `/home/eldi/ollama-bench/RANKING_HISTORY.md` (functiongemma added, MoE rejected)
- `/home/eldi/ollama-bench/RANKING.md` (installed list aligned to 22 models)
- `/tmp/bench-moe-fg.sh` (bench script ready/fixed)
---
POST-COMPACT RULES (next 3 turns):
1. DO NOT re-read files you already know from this summary
2. DO NOT read screenshots/images into context
3. Use grep/find to locate, read ONLY needed lines (max 50)
4. DO NOT re-read rules files — they are already loaded
5. Work from this summary, not from scratch
