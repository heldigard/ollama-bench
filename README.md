# ollama-bench

Local Ollama model evaluation suite for LLM coding agents. Leak gates first, multi-prompt scoring second, tie-break re-benching when models tie at the saturation cap.

The original problem: 60+ throwaway bench scripts in `~/bench/ollama/` that grew without tests, packaging, or memory bank. Three Ollama version bugs (gemma4 Q4_0, qwen3next MTP, LFM think-leak) were hidden in this maze. Each was discovered by accident.

## What it does

```bash
# Core pipeline (smoke → deep → tie-break → bug-finding)
ollama-bench list                       # enumerate installed models + status
ollama-bench smoke -m M                 # 1-prompt leak gate per model (~30s/model)
ollama-bench deep -c C -t T            # 5-task × N model bench (~90s/model)
ollama-bench tie-break -w W            # re-bench tied candidates (harder prompts, no score cap)
ollama-bench bug-finding -m M          # diff-review bench (count bugs found)
ollama-bench tool-call -m M            # structured JSON tool-call (ground-truth scoring)

# Cross-CLI benches (ported from cli-orchestration)
ollama-bench browser-tool -m M          # ref-grounded a11y action bench (snap+ref)
ollama-bench browser-bench-vision       # vision-grounded browser bench (OCR/classify/diff/tool/speed)

# Specialized slices
ollama-bench pdf-extract -m M           # schema field-extraction bench (abstention)
ollama-bench embedding-retrieval        # embedding MRR + recall@5 (ground-truth)
ollama-bench lfm-variant                # codeq summary tie-break for LFM family (think-strip)
ollama-bench multi-domain               # legacy 4-domain bench

# Helpers
ollama-bench judge score -i F           # LLM-as-judge scoring (manual rubric)
ollama-bench embedding eval -m M        # embedding model benchmark
ollama-bench report build -i F          # markdown ranking from TSV
```

## Tasks covered

Canonical 5 (deep): `improve` (prompt improver), `codeq_sum` (codeq summary), `smart_trim`
(PreCompact), `web_synth` (web research synthesis), `code_gen` (small function
generation).

Hero (ground-truth, separately-benched): `bug_finding`, `tool_call`, `browser-tool` (a11y
ref dispatch), `browser-bench-vision` (5 subtasks T1-T5), `pdf_extract`,
`embedding_retrieval`.

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
├── cli.py                              # argparse multi-command root
├── shared/
│   ├── config.py                       # TASKS registry, defaults, paths
│   ├── ollama.py                       # HTTP call + cache (think=False at TOP-LEVEL)
│   ├── scorer.py                       # Leak detection, structural scoring
│   └── paths.py                        # Output paths (TSV, ranking MD)
└── features/
    ├── smoke/                          # 1-prompt leak gate
    ├── deep/                           # 5-task × N model bench
    ├── tie_break/                      # Hard prompts + structural scoring (no cap)
    ├── bug_finding/                    # Diff-review (count bugs found)
    ├── tool_call/                      # Structured JSON tool-call
    ├── browser_tool/                   # Ref-grounded a11y action (snap+ref)
    ├── browser_bench/                  # Vision-grounded browser (T1-T5; ported cli-orchestration 2026-07-05)
    ├── pdf_extract/                    # Schema field-extraction (abstention)
    ├── embedding_retrieval/            # Embedding MRR + recall@5
    ├── lfm_variant/                    # codeq summary for LFM family
    ├── multi_domain/                   # legacy 4-domain
    ├── judge/                          # LLM-as-judge helpers
    ├── embedding/                       # embedding model benchmark
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
                    └──────────────────────────────────────────┴─→ bug_finding / tool_call
                                                                   (ground-truth, 0-N direct)
```

## Current lineup (2026-07-08 refactor, Ollama 0.31.1)

| task | #1 (PRIMARY) | #2 (fallback) |
|---|---|---|
| improve | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| codeq_sum | `jaahas/crow:9b` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| smart_trim | `fredrezones55/Qwopus3.5:9b` | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| web_synth | `aratan/gemma-4-E4B-it-heretic:Q6_K` | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| code_gen | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| bug_finding | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| tool_call | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |

Full lineup + history: `.memory-bank/topics/local-ollama-lineup.md` · `RANKING.md` · `RANKING_HISTORY.md`.

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

## Test

```bash
python3 -m pytest                                       # full suite (~30s)
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
