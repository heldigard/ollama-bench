# ollama-bench

Local Ollama model evaluation suite for LLM coding agents. Leak gates first, multi-prompt scoring second, tie-break re-benching when models tie at the saturation cap.

The original problem: 60+ throwaway bench scripts in `~/bench/ollama/` that grew without tests, packaging, or memory bank. Three Ollama version bugs (gemma4 Q4_0, qwen3next MTP, LFM think-leak) were hidden in this maze. Each was discovered by accident.

## What it does

```bash
ollama-bench list                       # enumerate installed models + status (gemma4 Q4_0 broken, etc.)
ollama-bench smoke                      # 1-prompt leak gate per model (~30s/model)
ollama-bench deep                       # 5-task × N model bench (~90s/model, 5 prompts/task)
ollama-bench tie-break --winners W      # re-bench tied candidates with harder prompts (no score cap)
ollama-bench lfm-variant                # codeq summary tie-break for LFM family (think-strip)
ollama-bench multi-domain               # legacy 4-domain bench (improve/compact/code/reason)
ollama-bench judge score --input F      # LLM-as-judge scoring (manual rubric)
ollama-bench embedding eval             # embedding model benchmark
ollama-bench report build               # markdown ranking from TSV
```

## Tasks covered

`improve` (prompt improver), `codeq_sum` (codeq summary), `smart_trim`
(PreCompact), `web_synth` (web research synthesis), `code_gen` (small function
generation). The 5 canonical tasks mirror the harness wiring in
`~/.claude/{hooks,scripts}/`. New tasks can be added by registering them in
`shared/config.py::TASKS` and writing the prompt in the appropriate feature.

## Architecture

Vertical-slice CLI package, graduated from a 40-script maze at `~/bench/ollama/`.
Each command family owns its CLI behavior under `src/ollama_bench/features/`.
Shared infrastructure (HTTP, scoring, paths, config) lives in
`src/ollama_bench/shared/`.

```text
src/ollama_bench/
├── cli.py
├── shared/
│   ├── config.py      # TASKS registry, defaults, paths
│   ├── ollama.py      # HTTP call + cache (think=False at TOP-LEVEL)
│   ├── scorer.py      # Leak detection, structural scoring
│   └── paths.py       # Output paths (TSV, ranking MD)
└── features/
    ├── smoke/        # 1-prompt leak gate
    ├── deep/         # 5-task × N model bench
    ├── tie_break/    # Hard prompts + structural scoring (no cap)
    ├── lfm_variant/  # codeq summary for LFM family
    ├── multi_domain/ # legacy 4-domain bench
    ├── judge/        # LLM-as-judge helpers
    ├── embedding/    # embedding model evaluation
    └── report/       # markdown ranking
```

The `shared/` package is intentionally small and holds reusable infrastructure
only. New functionality should normally start as a new slice under `features/`.

## Install (dev)

```bash
git clone https://github.com/heldigard/ollama-bench.git
cd ollama-bench
python3 -m pip install -e '.[test]'
pytest
```

## Requirements

- Python 3.11+
- Local Ollama running at `http://localhost:11434` (auto-detected)
- For deep/tie-break benches: models already `ollama pull`'d

## Critical caveats

- **Ollama 0.23.2** rejects `gemma4 Q4_0` + `qwen3next MTP` architectures. Use
  Q4_K_M variants of the same base models (e.g. `Huihui gemma4-12B abliterated`
  instead of `Mobius`). See
  `.memory-bank/topics/ollama-0.23.2-gemma4-q4_0-incompat.md`.
- **LFM2.5-8B-A1B** leaks thinking despite `think=False` on Ollama 0.23.2.
  Hits length cap before emitting the real answer. Not a codeq-summary candidate.
- **First-pass score saturation**: a per-task cap-of-7.0 makes 20+ models tie.
  Re-bench with `tie-break` for real discrimination.

## Test

```bash
python3 -m pytest
python3 -m pytest tests/test_layout.py   # vertical-slice integrity
```

The layout gate enforces: one `cmd_<slice>` per feature, `shared/` never
imports `features/`, no cross-feature imports except via `shared/`.

## License

MIT.