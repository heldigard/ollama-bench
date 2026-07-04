# Ranking History — full test registry (snapshot 2026-07-04, Ollama 0.31.1)

> Every model ever loaded into this bench cycle. **[KEPT]** = installed; **[DEL]** = tested then removed.
> Check here BEFORE pulling a model — if it's [DEL], the verdict stands unless a NEW fine-tune (not a requant) drops.

> Total tested: 64 · Kept: 17 · Eliminated: 47


## improve — top-10 (with status)

| # | combined | model | status |
|---|---|---|---|
| 1 | 2.5 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | **[KEPT]** |
| 2 | 3.5 | `Librellama/gemma4:e2b-Uncensored` | **[KEPT]** |
| 3 | 5.5 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | **[KEPT]** |
| 4 | 6.5 | `jaahas/crow:9b` | **[KEPT]** |
| 5 | 9.0 | `fredrezones55/Qwopus3.5:9b` | **[KEPT]** |
| 6 | 9.0 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` | **[KEPT]** |
| 7 | 11.0 | `ssfdre38/gemma4-turbo:latest` | **[DEL]** |
| 8 | 11.5 | `aratan/gemma-4-E4B-it-heretic:Q6_K` | **[KEPT]** |
| 9 | 12.5 | `cryptidbleh/gemma4-claude-opus-4.6:latest` | **[KEPT]** |
| 10 | 12.5 | `batiai/gemma4-e2b:q6` | **[DEL]** |

## codeq_sum — top-10 (with status)

| # | combined | model | status |
|---|---|---|---|
| 1 | 3.5 | `batiai/gemma4-e4b:q4` | **[KEPT]** |
| 2 | 4.0 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | **[KEPT]** |
| 3 | 6.0 | `free01/gemma4:e4b` | **[KEPT]** |
| 4 | 6.0 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` | **[KEPT]** |
| 5 | 6.5 | `ssfdre38/gemma4-turbo:latest` | **[DEL]** |
| 6 | 6.5 | `cryptidbleh/gemma4-claude-opus-4.6:latest` | **[KEPT]** |
| 7 | 8.0 | `jaahas/crow:9b` | **[KEPT]** |
| 8 | 8.5 | `aratan/gemma-4-E4B-it-heretic:Q6_K` | **[KEPT]** |
| 9 | 9.5 | `HanifAR24/gemma4-e2b-distilled:latest` | **[DEL]** |
| 10 | 10.0 | `Librellama/gemma4:e2b-Uncensored` | **[KEPT]** |

## smart_trim — top-10 (with status)

| # | combined | model | status |
|---|---|---|---|
| 1 | 1.0 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | **[KEPT]** |
| 2 | 6.5 | `fredrezones55/Qwopus3.5:9b` | **[KEPT]** |
| 3 | 7.0 | `aratan/gemma-4-E4B-it-heretic:Q6_K` | **[KEPT]** |
| 4 | 8.0 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` | **[KEPT]** |
| 5 | 9.5 | `free01/gemma4:e4b` | **[KEPT]** |
| 6 | 9.5 | `batiai/gemma4-e4b:q4` | **[KEPT]** |
| 7 | 10.0 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | **[KEPT]** |
| 8 | 10.0 | `qwen3.5:4b` | **[KEPT]** |
| 9 | 10.5 | `batiai/gemma4-e2b:q6` | **[DEL]** |
| 10 | 11.5 | `batiai/gemma4-12b:iq3` | **[KEPT]** |

## web_synth — top-10 (with status)

| # | combined | model | status |
|---|---|---|---|
| 1 | 5.0 | `batiai/gemma4-e4b:q4` | **[KEPT]** |
| 2 | 6.0 | `batiai/gemma4-12b:iq3` | **[KEPT]** |
| 3 | 6.5 | `free01/gemma4:e4b` | **[KEPT]** |
| 4 | 7.5 | `Librellama/gemma4:e2b-Uncensored` | **[KEPT]** |
| 5 | 8.0 | `HanifAR24/gemma4-e2b-distilled:latest` | **[DEL]** |
| 6 | 8.0 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | **[KEPT]** |
| 7 | 8.5 | `ssfdre38/gemma4-nano:12b` | **[DEL]** |
| 8 | 8.5 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` | **[KEPT]** |
| 9 | 9.0 | `hf.co/Disya/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` | **[DEL]** |
| 10 | 9.5 | `hf.co/google/gemma-4-12B-it-qat-q4_0-gguf:latest` | **[DEL]** |

## code_gen — top-10 (with status)

| # | combined | model | status |
|---|---|---|---|
| 1 | 6.0 | `fredrezones55/Qwopus3.5:9b` | **[KEPT]** |
| 2 | 6.0 | `aratan/gemma-4-E4B-it-heretic:Q6_K` | **[KEPT]** |
| 3 | 7.0 | `qwen3.5:4b` | **[KEPT]** |
| 4 | 7.5 | `batiai/gemma4-e4b:q4` | **[KEPT]** |
| 5 | 8.0 | `free01/gemma4:e4b` | **[KEPT]** |
| 6 | 8.0 | `batiai/gemma4-e2b:q6` | **[DEL]** |
| 7 | 9.5 | `Librellama/gemma4:e2b-Uncensored` | **[KEPT]** |
| 8 | 9.5 | `jaahas/crow:9b` | **[KEPT]** |
| 9 | 10.0 | `igorls/gemma4-e4b-classifier:Q4_K_M` | **[DEL]** |
| 10 | 10.5 | `qwen2.5:3b` | **[DEL]** |

## bug_finding — count bugs found in a diff

| # | score | model | status |
|---|---|---|---|
| 1 | 15.21 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` | **[KEPT]** |
| 2 | 15.00 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | **[KEPT]** |
| 3 | 14.56 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` | **[KEPT]** |
| 4 | 14.40 | `Librellama/gemma4:e2b-Uncensored` | **[KEPT]** |
| 5 | 14.26 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` | **[KEPT]** |
| 6 | 14.11 | `jaahas/crow:9b` | **[KEPT]** |
| 7 | 13.20 | `qwen3.5:4b` | **[KEPT]** |
| 8 | 12.78 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | **[KEPT]** |
| 9 | 12.56 | `aratan/gemma-4-E4B-it-heretic:Q6_K` | **[KEPT]** |
| 10 | 12.28 | `free01/gemma4:e4b` | **[KEPT]** |

## Eliminated registry (47 models — DO NOT re-pull unless a new fine-tune appears)

- `HanifAR24/gemma4-e2b-distilled:latest` — reasoning-distilled trap
- `MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest` — low rank after Ollama 0.31.1 unification (improve #23, codeq_sum #37)
- `VladimirGav/Qwen3.6-27B-16GB-VRAM-Uncensored:latest` — 15GB heavy, slow + leaky on long prompts
- `batiai/gemma4-12b:iq4` — non-winner (below top-5 combined-rank)
- `batiai/gemma4-12b:q2` — non-winner (below top-5 combined-rank)
- `batiai/gemma4-12b:q3` — non-winner (below top-5 combined-rank)
- `batiai/gemma4-12b:q4` — non-winner (below top-5 combined-rank)
- `batiai/gemma4-e2b:q6` — quant-cleanup: Q6 = Q4 quality, kept lighter Q4
- `batiai/qwen3.6-27b:iq3` — 27B/35B heavy, leak reasoning
- `baytout3/gemma4-12b-qat-uncensored-hauhaucs-balanced:q4_k_m` — budget-burn (done=length verbose)
- `ducquoc/gemma4-fast-sonnet:latest` — non-winner (below top-5)
- `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` — non-winner (below top-5 combined-rank)
- `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M` — 27B/35B heavy, leak reasoning
- `hf.co/AXONVERTEX-AI-RESEARCH/LFM2.5-8B-A1B-Q8_0-GGUF:latest` — smoke leak gate (think_tag)
- `hf.co/DevQuasar/google.gemma-4-12B-it-qat-q4_0-unquantized-GGUF:Q6_K` — non-winner gemma4-12B variant
- `hf.co/Disya/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` — non-winner (below top-5 combined-rank)
- `hf.co/DuoNeural/LFM2.5-8B-A1B-Abliterated-GGUF:Q4_K_M` — smoke leak gate (think_tag)
- `hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M` — smoke leak gate (think_tag)
- `hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:q4_k_m` — smoke leak gate (think_tag)
- `hf.co/batiai/LFM2.5-8B-A1B-GGUF:Q4_K_M` — model-inherent think-leak (all 9 LFM variants, persists on every Ollama version)
- `hf.co/brownsauto/LFM2.5-8B-A1B-GGUF:Q4_K_M` — smoke leak gate (think_tag)
- `hf.co/cloudnathan5/gemma-4-12b-it-MTP-GGUF:q4_k_m-mtp` — HTTP 500 (MTP arch not supported)
- `hf.co/cucu3281uc3182/ravenx-Gemma4-12B-MTP-Q4_K_M:latest` — MTP variant, non-winner
- `hf.co/gaston-parravicini/LFM2.5-8B-A1B-Uncensored-Gaston-GGUF:Q4_K_M` — model-inherent think-leak (all 9 LFM variants, persists on every Ollama version)
- `hf.co/google/gemma-4-12B-it-qat-q4_0-gguf:latest` — gemma4 Q4_0 — outperformed by pegasus912 heretic same base
- `hf.co/ji-farthing/gemma-4-12B-it-MTP-ik-llama-GGUF:Q4_K_M` — HTTP 500 (MTP arch not supported)
- `hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` — non-winner gemma4-12B variant
- `hf.co/llmfan46/gemma-4-12B-it-qat-q4_0-uncensored-heretic-GGUF:latest` — non-winner gemma4-12B variant
- `hf.co/lmstudio-community/gemma-4-12B-it-QAT-GGUF:Q4_0` — gemma4 Q4_0 — outperformed by pegasus912 heretic same base
- `hf.co/mradermacher/Huihui-LFM2.5-8B-A1B-abliterated-i1-GGUF:Q4_K_M` — smoke leak gate (think_tag)
- `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/mradermacher/Iris-12B-gemma-4-it-qat-i1-GGUF:Q4_K_M` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/mradermacher/gemma-4-12B-it-qat-q4_0-unquantized-GGUF:Q4_K_M` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/mradermacher/gemma-4-12B-it-qat-q4_0-unquantized-i1-GGUF:Q4_K_M` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/mradermacher/gemma-4-12B-it-qat-q4_0-unquantized-uncensored-heretic-GGUF:Q4_K_M` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/mradermacher/gemma-4-12B-it-qat-q4_0-unquantized-uncensored-heretic-i1-GGUF:q4_k_m` — duplicate gemma4-12B variant (winner kept via pegasus912/SC117)
- `hf.co/nathanrchn/LFM2.5-8B-A1B-GGUF-fixed:Q4_K_M` — smoke leak gate (think_tag)
- `hf.co/sliderforthewin/lfm2.5-8b-a1b-ft-GGUF:Q3_K_M` — smoke leak gate (think_tag)
- `igorls/gemma4-e4b-classifier:Q4_K_M` — non-winner (bug_finding -100, leaks)
- `nutboy02/Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-uncenfull:Q2_K_MTX` — 27B/35B heavy, leak reasoning
- `qwen2.5:3b` — non-winner (below top-5 combined-rank)
- `ssfdre38/gemma4-nano:12b` — non-winner ssfdre38 variant
- `ssfdre38/gemma4-turbo:12b` — non-winner ssfdre38 variant
- `ssfdre38/gemma4-turbo:e2b` — non-winner ssfdre38 variant
- `ssfdre38/gemma4-turbo:latest` — non-winner (below top-5 combined-rank)
- `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest` — Q4_K_M lost to Q8_0 of same family (Q8 kept for bug-finding)
