# Local Ollama Model Lineup (RTX 5080, 16GB) — RE-BENCH 2026-07-08 (Ollama 0.31.1)

> **Purpose:** Single source of truth for LOCAL Ollama winners + per-role map.
> Re-bench cycles: 2026-07-04 (16 winners) → round-3/5 → round-6 (strip mode) →
> **round-7 (2026-07-08 PM): full pipeline (smoke→deep→tie-break→specialized),
> combined ranking, lineup trimmed to top-5 union. 19 LLM + 3 embeddings = 22 models.**
>
> Round-7 rewired 7/9 PRIMARY winners + replaced qwen3.5:4b with cryptidbleh/gemma4-claude-opus-4.6
> (better on every metric); 13 models deleted (12 losers + qwen3.5:4b). See [deep-winners-20260708-pm](deep-winners-20260708-pm.md).
> think-strip mode. DeepSeek-V4-Flash is strippable but ranks last everywhere.
>
> **Round-8 (2026-07-08 PM, same day):** tested 4 NEW HF candidates — `shuhulx/Qwopus3.5-4B-Coder-Fable5-v1`,
> `tvall43/Qwen3.6-14B-A3B-FableVibes` (MoE 3B-active), `llmfan46/...composer2.5-v2-heretic` (Q4), `KevinJK51/Qwen3.6-12B-Thinking-V2`.
> ALL 4 LOST vs round-7 champions → deleted. Lineup unchanged at 22. Key: MoE-latency thesis failed
> (14B mem-bandwidth → tps 6.9 vs 4B 10.7); composer2.5-v2 Q4 ties xentriom on bug_finding (15.01 vs 14.99)
> but loses web_synth (Q4 10.82 vs Q8 11.92) — xentriom Q8 stays. See RANKING_HISTORY.md §round-8.
> Re-pull ONLY: a CODER-tuned 14B-A3B MoE (not reasoning-distill), or a genuinely new base (not another
> Fable5/composer2.5 finetune of Qwen3.5-9B / Qwopus3.5-4B / gemma-4-12B).

## Per-task top-2 (wired into harness) — 2026-07-08 PM (round-7, combined deep+tiebreak)

| task | #1 (PRIMARY) | #2 (fallback) |
|---|---|---|
| improve | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2`** (7.74/6.40) | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B` |
| codeq_sum | **`batiai/gemma4-e4b:q4`** ← NEW (10.24/11.20) | `jaahas/crow:9b` |
| smart_trim | **`hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced`** ← NEW (12.30/13.53) | `hf.co/SC117/gemma-4-12B-it-heretic-QAT` |
| web_synth | **`hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1`** ← NEW (11.85/12.83) | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| code_gen | **`hf.co/prithivMLmods/lift-GGUF`** ← NEW (12.13/8.23) | `SetneufPT/Qwopus3.5-4B-Coder-MTP` |
| bug_finding | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2`** ← NEW (15.43) | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| tool_call | **`SetneufPT/Qwopus3.5-4B-Coder-MTP`** ← NEW (10.10) | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus` |
| browser_tool | `SetneufPT/Qwopus3.5-4B-Coder-MTP` ← NEW | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus` |
| pdf_extract | **`SetneufPT/Qwopus3.5-4B-Coder-MTP`** ← NEW (12.07) | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled` |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF` (unchanged, 12.00) | `hf.co/prithivMLmods/lift-GGUF` |
| embedding | `embeddinggemma:latest` | `bge-m3:latest` |

## Key changes from 2026-07-08 PM re-bench (round-7)

1. **OmniCoder** — improve #1 (held) + bug_finding #1 (NEW). Multi-task champion.
2. **SetneufPT/Qwopus3.5** — tool_call + pdf_extract + browser_tool #1 (NEW). Structured-output champion.
3. **HauhauCS-Balanced** — smart_trim #1 (NEW, combined 12.30/13.53).
4. **TeichAI/Fable-5-v1** — web_synth combined #1 (NEW; tiebreak reshuffled past deep-only heretic).
5. **prithiv/lift** — code_gen #1 (NEW) + pdf_ocr fallback. Dual-role.
6. **DeltaCoder + Openclaw** (prior web_synth/bug_finding/smart_trim/code_gen #1) FELL OUT of top-5.
7. 7/9 PRIMARY changed; improve + pdf_ocr held. Lineup trimmed to top-5 union (losers deleted).
4. **Negentropy-4B** — compact 3GB model, top-5 in codeq_sum/code_gen. Good for VRAM-tight.
5. **lift** — OCR model, pdf_ocr #3 (11.12). Fallback to Unlimited-OCR.
6. **DeepSeek-V4-Flash** — strippable=1 but ranks LAST in every deep task. Not recommended.
7. **SetneufPT** — no longer improve #1; still codeq_sum #2, code_gen #5. Demoted from many PRIMARY roles.

## Strippable models

Models that leak thinking but produce usable output after `strip_reasoning()`:
- `hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M` — strippable but quality-degraded; last place everywhere.

Policy: `strippable=1` recorded at smoke; deep includes those models and scores cleaned output. Not discarded solely for recoverable CoT wrappers.

## Currently installed lineup (22 models — post 2026-07-08 PM trim)

```
# Canonical winners (round-7 combined)
zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2:latest  (improve #1, bug_finding #1)
batiai/gemma4-e4b:q4                                                  (codeq_sum #1)
hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M    (smart_trim #1)
hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M                      (web_synth #1)
hf.co/prithivMLmods/lift-GGUF:Q4_K_M                                  (code_gen #1, pdf_ocr #2)
SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest               (tool_call/browser_tool/pdf_extract #1)
hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M                          (pdf_ocr #1 — vision OCR)

# Top-5 depth (fallbacks / role fillers)
hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M             (improve #2)
hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M             (compact 3GB; tool_call depth)
hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL               (smart_trim #2)
hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest        (bug_finding depth)
hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M        (tool_call #2)
hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M         (pdf_extract #2)
xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0              (bug_finding #2, web_synth #2)
huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K                (code_gen #3)
jaahas/crow:9b                                                        (codeq_sum #2)
Librellama/gemma4:e2b-Uncensored                                      (multi-task mid)
batiai/gemma4-e2b:q4                                                  (smart_trim #3)
cryptidbleh/gemma4-claude-opus-4.6:latest                             (universal infra default; web_synth #2)

# Embeddings
embeddinggemma:latest  (default embed)   bge-m3:latest  (multilingual)   nomic-embed-text:latest
```
> 12 losers + qwen3.5:4b deleted this round (qwen3.5:4b replaced by cryptidbleh). See "Removed models" below.

## Removed models (historical)

See `topics/candidates-round-5-2026-07-05.md` for full removal history (46 models removed 2026-07-04, 1 in round-3, 2 in cleanup).

## Bench methodology

See `topics/bench-methodology.md` for smoke → deep → tie-break → bug-finding pipeline.
