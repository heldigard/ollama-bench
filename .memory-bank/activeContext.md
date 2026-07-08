# Active Context
- 2026-07-08: Bench methodology improved. GPU-safe incremental benching implemented.

## Current Objective
- **Task**: Re-run bench with improved prompts on all models (paused for today)
- **Phase**: Bench running in background (PID 50753), will complete overnight
- **Next**: Check results tomorrow, update RANKING.md, re-run specialized benches

## What Was Done Today

### Bench Improvements (committed + pushed)
- Split canonical_tasks.py → prompts.py (data) + canonical_tasks.py (scoring)
- Added 15 new edge-case prompts (improve 7, codeq_sum 7, smart_trim 6, web_synth 6, code_gen 7)
- Redesigned HARD_PROMPTS: genuine hard scenarios instead of concatenated cases
- Improved all 5 task scorers: gradated scoring, conflict-flagging, source utilization
- Added 4 harder tool_call cases + 2 harder bug_finding diffs
- 187/187 tests pass

### GPU-Safe Incremental Benching (committed + pushed)
- `deep` command: --resume, --cooldown, --temp-limit flags
- Sequential execution (no more ThreadPoolExecutor)
- Per-model incremental TSV save (never lose progress)
- GPU temperature monitoring via nvidia-smi
- `tie_break` command: same cooldown/temp-limit support

### New Models Pulled
- hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M (6.5 GB) — Fable 5 distillation
- hf.co/FadedRedStar/Qwen3.5-9B-heretic-GGUF:Q4_K_M (6.3 GB) — heretic fine-tune
- hf.co/mradermacher/Gemma-4-12B-StyleTune-i1-GGUF:Q4_K_M (7.9 GB) — StyleTune 12B

### Bench Status
- Smoke: 31/31 models pass
- Deep bench running in background (13 models × 33 prompts, 60s cooldown)
- Results incrementally saved to ~/.cache/ollama-bench/results/
- Progress log: ~/.cache/ollama-bench/results/bench_v2_progress.log

## Lessons Learned (CRITICAL — read before next session)

1. **NEVER run all models at once** — maxes out GPU, takes hours, gets killed. Always sequential with cooldown.
2. **Save after EACH model** — old approach wrote all results at the end, losing everything on kill/crash. New approach appends to TSV after each model.
3. **--resume flag is essential** — if bench gets interrupted, just re-run with --resume to skip completed models.
4. **60s cooldown between models** — keeps GPU at ~60-65°C instead of 80°C+. Configurable via --cooldown.
5. **Background with nohup** — bench survives session disconnect. Check progress via the log file.
6. **Don't re-run what's done** — always check existing results before starting a bench run.

## Tomorrow's Checklist
1. Check bench_v2_progress.log — all 13 models done?
2. If done: read deep_bench.tsv, update RANKING.md
3. Run specialized benches (tool_call, bug_finding, pdf_extract) with same cooldown approach
4. Update config.py if winners changed
5. Update consumer repos if needed
6. Commit + push all changes

## Preserved Negative Constraints
- DO NOT pull Q5/Q6/Q8 variants of existing Q4 winners
- DO NOT install models >10GB (RTX 5080 16GB constraint)
- DO NOT discard strippable models solely for thinking leaks
- DO NOT run benches without --cooldown (GPU safety)
