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

## 2026-07-05T20:53:27
Method: ollama-SetneufPT/Qwopus3.5-4B-Coder-MTP
Session: unknown

## Current Objective (from current-objective.json)
**Task**: que otros modelos nuevos de hugging face que no hayamos probado crees que podrías probar? descargamos y pruebas? creo que en otro proyectos y en claude code, quedaron tests bench de codigo y browser agent, eso deberias traerlos para aca, o
**Phase**: Test
**Next**: Think -> Plan -> Build -> Review -> Test -> Validate -> Ship -> Reflect
**Files**: /home/eldi/ollama-bench/src/ollama_bench/cli.py, /home/eldi/ollama-bench/src/ollama_bench/features/browser_bench/command.py, /home/eldi/ollama-bench/.memory-bank/topics/candidates-round-4-2026-07-05.md, /home/eldi/ollama-bench/.memory-bank/topics/_index.md, /home/eldi/ollama-bench/.memory-bank/topics/local-ollama-lineup.md, /home/eldi/ollama-bench/README.md, /home/eldi/ollama-bench/.memory-bank/activeContext.md, /home/eldi/ollama-bench/src/ollama_bench/features/candidates/command.py

## Preserved Negative Constraints
- DO NOT** pull Q5/Q6/Q8 variants of existing Q4 winners — see `topics/quant-comparison-2026-07-04.md

**Task**: Project improvements (README, activeContext, candidates slice)  
**Acceptance**: All 14 subcommands listed; `ollama-bench candidates` works end-to-end; activeContext reflects 2026-07-05 state; Preserved Negative Constraints intact.  
**Verified**: `python3 -m py_compile`, `ruff check`, `pytest tests/test_layout.py tests/test_list.py` (9/9); `ollama-bench candidates --help`; `codeq refs` (1 ref added).  
**Current**: Commit + push completed (`ba463e5`).  
**Errors**: None.  
**Decisions**: Encapsulated `pull → smoke → deep → report` into `cmd_candidates`; fixed unused import/f-string in `candidates/command.py`; wired `add_candidates` to `cli.py::_SLICES`; refreshed README with full pipeline + deferred section.  
**Next**: User meta-task complete; proceed to next round or new feature request.  

**Files**: `/home/eldi/ollama-bench/README.md`, `/home/eldi/ollama-bench/.memory-bank/activeContext.md`, `/home/eldi/ollama-bench/.memory-bank/progress.md`, `/home/eldi/ollama-bench/src/ollama_bench/cli.py`, `/home/eldi/ollama-bench/src/ollama_bench/features/candidates/command.py`
---
POST-COMPACT RULES (next 3 turns):
1. DO NOT re-read files you already know from this summary
2. DO NOT read screenshots/images into context
3. Use grep/find to locate, read ONLY needed lines (max 50)
4. DO NOT re-read rules files — they are already loaded
5. Work from this summary, not from scratch
