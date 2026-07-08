# Active Context
> 2026-07-08: GPU-safe bench suite + full pipeline. All benches sequential via shared paced().

## Current Objective
- **Task**: Run the full bench sequence (deep → specialized → tie-break) GPU-safe.
- **Phase**: Running detached (nohup). deep 14/30 → orchestrator waits, then runs specialized + tie-break.
- **Next**: When pipeline finishes, read `~/.cache/ollama-bench/results/*.md`, update RANKING.md if winners changed, rewire config.py primary/fallback if needed.

## What Landed This Session

### Critical bug fix — resume no longer drops scored models
- `deep` details JSONL is now **append-only** (flushed per model) — was end-only, so a kill left no JSONL → resume reconstructed empty → final TSV rewrite DROPPED every benched model. Fixed + pinned by `test_resume_aggregate_preserves_completed_model`.

### Parallel-pool OVERHEATING root cause removed from ALL benches
- bug_finding/tool_call/pdf_extract used `ThreadPoolExecutor(max_workers=4)` (= yesterday's 80°C+ cause). Replaced with `shared/gpu.py::paced()` (sequential + temp-gate + cooldown). pdf_ocr + tie_break also paced/deduped.
- Every bench now has `--cooldown`/`--temp-limit`; smoke has `--resume` + incremental save too.

### Pipeline orchestrator
- `scripts/run_pipeline.sh` (wait-deep → bug-finding/tool-call/pdf-extract/pdf-ocr → tie-break; idempotent, GPU-safe, nohup).
- `scripts/tie_winners.py` (models within 0.5 of per-task top → tie-break winners).

## Run Status (live)
- deep: ✅ 30/30. tie-break: ✅ 26/26. Specialized: 🔄 running (bug-finding → tool-call → pdf-extract ×30, pdf-ocr ×2).
- Winners SHIFTED 4/5 vs config primaries (see [deep-winners-20260708-pm](topics/deep-winners-20260708-pm.md)). Openclaw + DeltaCoder fell out of top-5.
- config.py primaries + RANKING.md STALE → rewire AFTER full pipeline (specialized + combined) done.
- Noise cleaned: 6 orphan result dumps + 4 old logs + 22 __pycache__; kept _refactor_20260708 baselines.

## Preserved Negative Constraints
- DO NOT re-introduce parallel pools (ThreadPoolExecutor) — GPU overheat root cause.
- DO NOT run benches without `--cooldown`/`--temp-limit` (GPU safety).
- DO NOT pull Q5/Q6/Q8 of existing Q4 winners; DO NOT install >10GB models (RTX 5080 16GB).
- DO NOT discard strippable models solely for thinking leaks.
- Fresh (non-resume) deep runs clear stale TSV/JSONL — intentional (prevents append-stacking).

## Key Paths
- Results: `~/.cache/ollama-bench/results/` (deep_bench_strip.{tsv,md,_details.jsonl}, smoke_all.tsv, *.md per bench)
- Logs: `~/.cache/ollama-bench/logs/{deep,pipeline}_*.log`
- Resume deep: `nohup ollama-bench deep --resume --cooldown 60 --temp-limit 75 &`
- Resume pipeline: `nohup bash scripts/run_pipeline.sh &`
