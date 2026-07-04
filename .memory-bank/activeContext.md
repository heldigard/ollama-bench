# Active Context
> Current handoff / recent state

- 2026-07-04T20:00:00Z | status:live | Re-bench cycle complete on unified Ollama 0.31.1. 16 LLM winners + 2 embeddings kept (75 GB, was 325 GB). 8 harness wiring points updated to per-task top-2. Quant comparison (Q4 vs Q8) confirmed Q4_K_M is the quality ceiling — all higher-quant variants deleted. Project stable.
- 2026-07-04T15:30:00Z | status:completed | Initial vertical-slice split from `~/bench/ollama/` into `~/ollama-bench/` package (v0.1.0). 72 tests passing. Public repo: https://github.com/heldigard/ollama-bench.

## Current state (stable)

- 10 CLI subcommands (smoke/deep/tie-break/bug-finding/lfm-variant/multi-domain/judge/embedding/report/list)
- 72 tests passing, ruff clean
- 18-model lineup (16 LLM winners Q4_K_M + 2 embeddings)
- Harness fully wired to per-task top-2
- Memory bank reorganized: pointer in `~/.memory-bank/topics/local-ollama-lineup.md` → detail here

## Next actions (on demand)

- Re-bench ONLY when a new fine-tune appears (not a mere requant — Q8/Q6 don't help, see `topics/quant-comparison-2026-07-04.md`).
- After Ollama upgrades, re-smoke to confirm no regression.
- If a new task type is needed (e.g. multi-turn, vision), add a new `features/<slice>/` + register in `cli.py::_SLICES`.- 2026-07-04T20:23:01Z | status:active | session:bench-improve-2026-07-04 | Bench improvements + think-strip mode landed: seed=42 in CallOpts (reproducibility), 14 leak patterns incl <|channel|> + reasoning/reflection/output tags, strip_reasoning()+leaks_are_strippable(), smoke strippable column, deep --strip flag. Unlocks thinking-leak models (DeepSeek-R1/Qwen3-think/GPT-OSS/LFM) judged on cleaned answer. Config drift fixed: codeq default Mobius->batiai/gemma4-e4b:q4, config.py primary_model_default aligned to RANKING (q6->q4), prompt-improve REFERENCE memory Huihui->pegasus912. 90 tests green, ruff clean. New topic: topics/new-benchmarks-roadmap-2026-07-04.md (8 new bench dimensions mapped to cross-cli consumers). Pulling 4 new HF candidates (Opus/abliterated/reasoning-distilled) for bench.
