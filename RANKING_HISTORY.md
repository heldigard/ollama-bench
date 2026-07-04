# Ranking History — full test registry (snapshot 2026-07-04, Ollama 0.31.1)

> Every model ever loaded into this bench cycle. **[KEPT]** = installed; **[DEL]** = tested then removed.
> Check here BEFORE pulling a model — if it's [DEL], the verdict stands unless a NEW fine-tune (not a requant) drops.

> Total tested: 72 · Kept: 22 · Eliminated: 50


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
| 1 | **17.98** | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | **[KEPT]** NEW 2026-07-04 (beats prev #1) |
| 2 | 15.21 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` | **[KEPT]** (now bug_finding fallback) |
| 3 | 15.00 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | **[KEPT]** |
| 3 | 15.00 | `kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest` | **[KEPT]** NEW 2026-07-04 (reasoning; leaks `<think>`, strippable) |
| 5 | 14.56 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` | **[KEPT]** |
| 6 | 14.40 | `Librellama/gemma4:e2b-Uncensored` | **[KEPT]** |
| 7 | 14.26 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` | **[KEPT]** |
| 8 | 14.11 | `jaahas/crow:9b` | **[KEPT]** |
| 9 | 13.20 | `qwen3.5:4b` | **[KEPT]** |
| 10 | 12.78 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | **[KEPT]** |

## 2026-07-04 incremental batch — new HF candidates (first-pass deep + ground-truth)

> Benched with `seed=42`. Deep scores are first-pass (saturate 7.0); these
> models did NOT go through the full tie-break, so they're not in the
> combined-rank tables above — kept here as a complete metric record so they're
> never re-pulled blindly.

| model | improve | codeq_sum | smart_trim | web_synth | code_gen | bug_finding | tool_call | verdict |
|---|---|---|---|---|---|---|---|---|
| `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | 0.52 | 5.98 | 7.0 (sat) | 7.0 (sat) | 5.83 | **17.98** | 9.82 | **[KEPT]** — new bug_finding #1 |
| `kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest` | 0.75 | -4.0 | 5.0 | 0.0 | -1.0 | 15.00 | 8.74 | **[KEPT]** — reasoning; leaks (strippable=1); bug_finding parity |
| `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` | 0.10 | 2.19 | 2.59 | 1.08 | 1.90 | 13.48 | 8.30 | **[DEL]** below incumbents on all 5 deep + bug_finding |
| `hf.co/DuoNeural/OpenYourMind-Gemma4-12B-IT-Abliterated-GGUF:Q4_K_M` | -0.29 | 1.73 | 2.96 | 3.17 | 0.71 | 11.66 | 8.30 | **[DEL]** below incumbents everywhere; incremental over existing heretic Gemma4-12B |
| `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` | 3.08 | 5.80 | 7.0 (sat) | 5.00 | 6.00 | **15.86** | 9.83 | **[KEPT]** — bug_finding #2, code_gen ties #1, improve #2-tier; beats xentriom Q8_0 (14.26) |
| `bge-m3:latest` (embedding) | — | — | — | — | — | — | — | **[KEPT]** — multilingual embed #1 (dim 1024); TIES embeddinggemma on embedding-retrieval (MRR 1.000); no rewire (768-d index stays) |
| `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | 3.05 | 6.04 | 7.0 (sat) | 5.00 | **7.00** | 15.50 | **9.85** | **[KEPT]** — tool_call #1 (9.85 > huihui 9.82), code_gen deep #1-tier (7.0 > incumbent 6.0), bug_finding #3; Opus 4.6 + function-calling fine-tune |
| `hf.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:Q3_K_M` | 1.75 | 3.98 | 4.67 | 2.51 | 4.82 | 12.59 | 9.81 | **[DEL]** — 30B MoE (3B active) hypothesis (large knowledge + small active compute) did NOT pan out: slower (20s/smoke) AND weaker than dense 9-12B on every task except tool_call (9.81). Q3 quant on 30B degrades; VRAM spill on 16GB. Dense Qwen3.5-9B+Opus merges (functiongemma/huihui) outperform. Culled (14 GB freed). |

## 2026-07-04 ground-truth slices — browser_tool + pdf_extract (proxy retirement)

> Two new bench slices landed (`features/browser_tool/`, `features/pdf_extract/`) to retire
> the last PROXY model choices in the cross-CLI harness (agent_browser + pdf-extract both
> used pegasus912 as an un-benched "improve #1" proxy). Existing models re-benched — no new
> pulls, no change to tested/kept/elim counts (72/22/50).

**browser_tool** (ref-grounded a11y action; +3 JSON, +3 known action, +3 grounded ref):

| model | browser_tool | verdict |
|---|---|---|
| `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | **10.19 (#1)** | agent_browser PRIMARY — was FALLBACK, promoted (also tool_call #1) |
| `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | 10.18 | #2 |
| `jaahas/crow:9b` | 10.15 | #3 |
| `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | 10.01 | #4 |
| `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | 9.70 | agent_browser FALLBACK — was PROXY PRIMARY, retired (only #5); kept as gemma4-family diversity fallback |
| `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` | 8.06 | #6 |

**pdf_extract** (schema field extraction + abstention; +3 JSON, +1.5/field, +2 abstain / -2 hallucinate):

| model | pdf_extract | verdict |
|---|---|---|
| `jaahas/crow:9b` | **11.15 (#1)** | edges on noise only |
| `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | 11.14 | tied |
| `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | 11.14 | pdf-extract DEFAULT — proxy caveat RETIRED (confirmed tied #1) |
| `batiai/gemma4-12b:iq3` | 11.14 | tied |
| `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` | 11.13 | tied |
| `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | 11.12 | tied |

> pdf_extract saturated within 0.03 across the whole field — extraction at this difficulty is
> easy for the lineup; pegasus912 stays the pdf-extract default (sound, 12B, improve #1).
> Harder docs (messy OCR, ambiguous tables) needed to discriminate further — deferred.

## Eliminated registry (49 models — DO NOT re-pull unless a new fine-tune appears)

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
- `hf.co/DuoNeural/OpenYourMind-Gemma4-12B-IT-Abliterated-GGUF:Q4_K_M` — [DEL 2026-07-04] below incumbents on all 5 deep tasks + bug_finding (11.66); incremental over existing heretic/abliterated Gemma4-12B (SC117, pegasus912)
- `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` — [DEL 2026-07-04] Opus 4.8 style didn't beat Opus 4.6 incumbents; weak on all 5 deep tasks + bug_finding (13.48 < 15.21). Ollama normalizes dots→hyphens in tags (invoke as Claude-4.6-4.8, not Claude-4.6.4.8)
- `batiai/gemma4-e2b:q4` — [DEL 2026-07-04] top-5 cull: not in combined-rank top-5 on any task. Tie-break metrics (from quant-comparison-2026-07-04): improve 6.00, codeq_sum 11.0, smart_trim 10.5, web_synth 7.0, code_gen 16.0. Strong code_gen tie-break but deep-rank pulled combined outside top-5; e4b:q4 (codeq_sum/web_synth #1) + qwen3.5:4b (anchor) cover the small-Q4 slots. Not wired anywhere in ~/.claude.
