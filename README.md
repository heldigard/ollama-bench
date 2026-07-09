# ollama-bench

Local Ollama model evaluation suite for LLM coding agents. Leak gates first, multi-prompt scoring second, tie-break re-benching when models tie at the saturation cap.

The original problem: 60+ throwaway bench scripts in `~/bench/ollama/` that grew without tests, packaging, or memory bank. Three Ollama version bugs (gemma4 Q4_0, qwen3next MTP, LFM think-leak) were hidden in this maze. Each was discovered by accident.

## What it does

```bash
# Core pipeline (smoke → deep → tie-break → bug-finding)
ollama-bench list                       # enumerate installed models + status
ollama-bench smoke -m M                 # 1-prompt leak gate per model (~30s/model)
ollama-bench deep -c C -t T             # 5-task × N model bench (~90s/model)
ollama-bench tie-break -w W             # re-bench tied candidates (harder prompts, no score cap)
ollama-bench bug-finding -m M           # diff-review bench (count bugs found)
ollama-bench tool-call -m M             # structured JSON tool-call (ground-truth scoring)

# Cross-CLI benches (ported from cli-orchestration)
ollama-bench browser-tool -m M          # ref-grounded a11y action bench (snap+ref)
ollama-bench browser-bench-vision       # vision-grounded browser bench (OCR/classify/diff/tool/speed)

# Specialized slices
ollama-bench pdf-extract -m M           # schema field-extraction bench (abstention)
ollama-bench pdf-ocr -m M               # rendered PDF OCR bench (vision/OCR models)
ollama-bench embedding-retrieval        # embedding MRR + recall@5 (ground-truth)
ollama-bench lfm-variant                # codeq summary tie-break for LFM family (think-strip)
ollama-bench multi-domain               # legacy 4-domain bench

# Orchestrator + helpers
ollama-bench candidates M [M ...]       # end-to-end sweep: pull → smoke → deep → MD report
ollama-bench judge score -i F           # LLM-as-judge scoring (manual rubric)
ollama-bench embedding eval -m M        # embedding model benchmark
ollama-bench report build [-i F]        # markdown ranking from TSV (defaults to last deep TSV)
```

## Tasks covered

Canonical 5 (deep): `improve` (prompt improver), `codeq_sum` (codeq summary), `smart_trim`
(PreCompact), `web_synth` (web research synthesis), `code_gen` (small function
generation).

Hero (ground-truth, separately-benched): `bug_finding`, `tool_call`, `browser-tool` (a11y
ref dispatch), `browser-bench-vision` (5 subtasks T1-T5), `pdf_extract`,
`pdf_ocr` (vision/OCR models only), `embedding_retrieval`.

The canonical tasks mirror the harness wiring in
`~/.claude/{hooks,scripts}/`. New tasks can be added by registering them in
`shared/config.py::TASKS` and writing the prompt in the appropriate feature.

## Architecture

Vertical-slice CLI package, graduated from a 40-script maze at `~/bench/ollama/`.
Each command family owns its CLI behavior under `src/ollama_bench/features/`.
Shared infrastructure (HTTP, scoring, paths, config) lives in
`src/ollama_bench/shared/`.

```text
src/ollama_bench/
├── cli.py                              # argparse multi-command root (17 slices)
├── shared/
│   ├── config.py                       # TASKS registry, defaults, paths
│   ├── ollama.py                       # HTTP call + cache (think=False at TOP-LEVEL)
│   ├── scorer.py                       # Leak detection, structural scoring
│   ├── paths.py                        # Output paths (TSV, ranking MD)
│   └── gpu.py                          # GPU safety: sequential exec, cooldown, resume
└── features/
    ├── smoke/                          # 1-prompt leak gate
    ├── deep/                           # 5-task × N model bench
    ├── candidates/                     # Orchestrator: pull → smoke → deep → MD report
    ├── tie_break/                      # Hard prompts + structural scoring (no cap)
    ├── bug_finding/                    # Diff-review (count bugs found)
    ├── tool_call/                      # Structured JSON tool-call
    ├── browser_tool/                   # Ref-grounded a11y action (snap+ref)
    ├── browser_bench/                  # Vision-grounded browser (T1-T5; ported cli-orchestration 2026-07-05)
    ├── pdf_extract/                    # Schema field-extraction (abstention)
    ├── pdf_ocr/                        # Rendered PDF OCR (vision/OCR models)
    ├── embedding_retrieval/            # Embedding MRR + recall@5
    ├── lfm_variant/                    # codeq summary for LFM family
    ├── multi_domain/                   # legacy 4-domain
    ├── judge/                          # LLM-as-judge helpers
    ├── embedding/                      # embedding model benchmark
    ├── list/                           # enumerate installed models
    └── report/                         # TSV → markdown ranking
```

The `shared/` package is intentionally small and holds reusable infrastructure
only. New functionality should normally start as a new slice under `features/`.

## Pipeline

```
smoke (leak gate) ──┐
                    ├─→ deep (5-task, 0-7 SAT cap) ─→ tie-break (hard prompts, -5 to +15)
                    │                                          │
                    └──────────────────────────────────────────┴─→ bug_finding / tool_call /
                                                                   browser_tool / pdf_extract /
                                                                   pdf_ocr (ground-truth, 0-N direct)

candidates = one-shot orchestrator wrapping the pipeline above for new HF models
```

## Current lineup (2026-07-08 PM re-bench, Ollama 0.31.1)

Combined deep+tiebreak rank; ground-truth scores for the hero tasks. PRIMARY/FALLBACK
mirror `shared/config.py` (single source of truth) and the live harness wiring in
`~/.claude/{hooks,scripts}/`.

| task | #1 PRIMARY | #2 FALLBACK |
|---|---|---|
| improve | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| codeq_sum | `batiai/gemma4-e4b:q4` | `jaahas/crow:9b` |
| smart_trim | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| web_synth | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| code_gen | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| bug_finding | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| tool_call | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| browser_tool | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| pdf_extract | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` |

Full lineup + history: `.memory-bank/topics/local-ollama-lineup.md` · `RANKING.md` · `RANKING_HISTORY.md`.

## Install (dev)

```bash
git clone https://github.com/heldigard/ollama-bench.git
cd ollama-bench
python3 -m pip install -e '.[test]'
pytest                  # 194 tests, ~0.5s
```

## Requirements

- Python 3.11+
- Local Ollama running at `http://localhost:11434` (auto-detected)
- For deep/tie-break benches: models already `ollama pull`'d

## Critical caveats

- **Ollama 0.23.2** rejects `gemma4 Q4_0` + `qwen3next MTP` architectures. Use
  Q4_K_M variants of the same base models. See
  `.memory-bank/topics/ollama-0.23.2-gemma4-q4_0-incompat.md` (resolved: use
  Ollama 0.31.1+).
- **LFM2.5-8B-A1B family** leaks thinking despite `think=False` on every Ollama
  version tested. Model-inherent (fine-tune baked thinking into response channel).
  9 variants deleted in 2026-07-04 re-bench.
- **Reasoning-distilled small models** consistently leak at smoke gate: `kwangsuklee`,
  `DeepSeek-V4-Flash`, `Phi-4-mini-reasoning`. Predictable — pre-reject without pull.
- **First-pass score saturation**: a per-task cap-of-7.0 makes 20+ models tie.
  Re-bench with `tie-break` for real discrimination.
- **Tie-break saturation at 10.50 / 16.00**: hard-prompt scores for smart_trim /
  web_synth / code_gen saturate at structural-scoring caps. Real winners hidden
  in ties. Workaround: bump scoring bounds or add 3rd hard prompts (open task).
- **`pdf_ocr` is vision-only**: unlimited-OCR needs `/api/chat` + `ocr [img]`.
  General text models score -100 on this task (use `pdf_extract` instead).

## Test

```bash
python3 -m pytest                                       # full suite (194 tests, ~0.5s)
python3 -m pytest tests/test_layout.py                  # vertical-slice integrity
python3 -m pytest tests/test_browser_tool.py            # slice-specific
```

The layout gate enforces: one `cmd_<slice>` per feature, `shared/` never
imports `features/`, no cross-feature imports except via `shared/`, cli.py imports
`add_parser` from every feature.

## Cross-CLI bench ownership

ollama-bench is the canonical source of bench truth for the cross-CLI ecosystem.
Bench slices ported in (graduated from sibling projects):
- `browser-bench-vision` ← `cli-orchestration/browser/model_bench.py` (2026-07-05 round-4)

Remaining ports (deferred): `cheap_bench` cross-provider benchmark from `~/cheap-llm/`.

When a sibling project graduates a model-evaluation bench, port it here as a new
slice per the `vertical-slice-architect` pattern.

## License

MIT.