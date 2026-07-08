# Local Ollama Model Lineup (RTX 5080, 16GB) — RE-BENCH 2026-07-08 (Ollama 0.31.1)

> **Purpose:** Single source of truth for LOCAL Ollama winners + per-role map.
> Five re-bench cycles: 2026-07-04 (16 winners) → round-3 (Grug upset) →
> round-5 (e4b collapse → SetneufPT/crow) → round-6 (2026-07-08 new models
> + strip mode). 26 LLM winners + 3 embeddings = 29 models (~100 GB).
>
> Round-6 introduced 7 new models (Negentropy 4B/9B, Openclaw, DeltaCoder,
> yuxinlu1 Gemma4, DeepSeek-V4-Flash, lift) and re-benched with `--strip`
> think-strip mode. DeepSeek-V4-Flash is strippable but ranks last everywhere.

## Per-task top-2 (wired into harness) — 2026-07-08

| task | #1 (PRIMARY) | #2 (fallback) |
|---|---|---|
| improve | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2`** ← NEW (7.01) | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled` ← NEW |
| codeq_sum | **`jaahas/crow:9b`** (unchanged, 9.57) | `SetneufPT/Qwopus3.5-4B-Coder-MTP` |
| smart_trim | **`hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled`** ← NEW (11.53) | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf` |
| web_synth | **`hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B`** ← NEW (12.50 tie) | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| code_gen | **`hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled`** ← NEW (11.65 tie) | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2` |
| bug_finding | **`hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B`** ← NEW (14.06) | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2` |
| tool_call | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf` (saturated) | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| browser_tool | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf` (saturated) | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| pdf_extract | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf` (saturated) | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF` (unchanged, 12.00) | `hf.co/prithivMLmods/lift-GGUF` ← NEW |
| embedding | `embeddinggemma:latest` | `bge-m3:latest` |

## Key changes from 2026-07-08 re-bench

1. **Openclaw** (`hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M`) — NEW #1 smart_trim + code_gen (tied). Strong generalist Qwen3.5-9B fine-tune.
2. **DeltaCoder** (`hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M`) — NEW #1 web_synth (tied) + bug_finding. Coder-optimized Qwen3.5-9B.
3. **OmniCoder** promoted to improve #1 (was #4); SetneufPT demoted from improve #1 to #8.
4. **Negentropy-4B** — compact 3GB model, top-5 in codeq_sum/code_gen. Good for VRAM-tight.
5. **lift** — OCR model, pdf_ocr #3 (11.12). Fallback to Unlimited-OCR.
6. **DeepSeek-V4-Flash** — strippable=1 but ranks LAST in every deep task. Not recommended.
7. **SetneufPT** — no longer improve #1; still codeq_sum #2, code_gen #5. Demoted from many PRIMARY roles.

## Strippable models

Models that leak thinking but produce usable output after `strip_reasoning()`:
- `hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M` — strippable but quality-degraded; last place everywhere.

Policy: `strippable=1` recorded at smoke; deep includes those models and scores cleaned output. Not discarded solely for recoverable CoT wrappers.

## All installed LLM winners (26 models)

```
# NEW 2026-07-08
hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M  (smart_trim #1, code_gen #1, improve #3, web_synth #4)
hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M       (web_synth #1, bug_finding #1, smart_trim #5)
hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M       (improve #2, code_gen #5, pdf_ocr #4)
hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M       (codeq_sum #4, code_gen #4 — compact 3GB)
hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M  (improve #7, codeq_sum #6 — mid-pack)
hf.co/prithivMLmods/lift-GGUF:Q4_K_M                            (pdf_ocr #3 — OCR specialist)
hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M        (strippable, last everywhere — NOT recommended)

# CARRIED from round-5
zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2  (improve #1, code_gen #1, bug_finding #2)
jaahas/crow:9b                                                   (codeq_sum #1)
SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU                 (codeq_sum #2, code_gen #5)
hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M  (tool_call/browser/pdf_extract #1)
huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K           (bug_finding/tool_call fallback)
fredrezones55/Qwopus3.5:9b                                       (smart_trim #4, web_synth #5)
aratan/gemma-4-E4B-it-heretic:Q6_K                               (web_synth #1 tie, code_gen mid)
hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M (web_synth #3, code_gen #3)
hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M                    (pdf_ocr #1 — purpose-built OCR)
qwen3.5:4b                                                       (universal default anchor)
Librellama/gemma4:e2b-Uncensored                                  (multi-task mid-tier)
batiai/gemma4-12b:iq3                                            (web_synth #2 old)
batiai/gemma4-e2b:q4                                             (code_gen tied)
batiai/gemma4-e4b:q4                                             (demoted r5)
cryptidbleh/gemma4-claude-opus-4.6                               (codeq_sum #5, web_synth #6)
cryptidbleh/gemma4-claude-sonnet-4.6                             (bug_finding #2 old)
free01/gemma4:e4b                                                (codeq_sum #4 old, web_synth #3)
hf.co/SC117/gemma-4-12B-it-heretic-QAT-UD-Q4_K_XL               (smart_trim #4 old)
hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl          (improve #2 old)
hf.co/kai-os/Grug-12B-GGUF:Q4_K_M                               (improve #1 old)
xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0          (bug_finding #5 old)
nomic-embed-text + embeddinggemma + bge-m3                        (embeddings)
```

## Removed models (historical)

See `topics/candidates-round-5-2026-07-05.md` for full removal history (46 models removed 2026-07-04, 1 in round-3, 2 in cleanup).

## Bench methodology

See `topics/bench-methodology.md` for smoke → deep → tie-break → bug-finding pipeline.
