# Current Ranking — installed Ollama models (snapshot 2026-07-08, Ollama 0.31.1)

> Refactor run: `deep_refactor_20260708` + specialized benches.
> The old first-pass cap produced large ties; the new canonical task scorers
> report 15-20 unique scores per canonical task. Smoke: 20/20 generative models
> clean; embeddings skipped from generate smoke and evaluated separately.

## improve

| # | score | model |
|---|---|---|
| **1** | **6.60** | **`SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest`** |
| 2 | 6.39 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 3 | 6.08 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 4 | 5.78 | `fredrezones55/Qwopus3.5:9b` |
| 5 | 5.57 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |

Discrimination: 20 unique scores; max tie group 1.

## codeq_sum

| # | score | model |
|---|---|---|
| **1** | **9.23** | **`jaahas/crow:9b`** |
| 2 | 9.15 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 3 | 9.11 | `free01/gemma4:e4b` |
| 4 | 9.11 | `batiai/gemma4-e4b:q4` |
| 5 | 8.67 | `batiai/gemma4-12b:iq3` |

Discrimination: 18 unique scores; max tie group 2.

## smart_trim

| # | score | model |
|---|---|---|
| **1** | **11.25** | **`fredrezones55/Qwopus3.5:9b`** |
| 2 | 11.24 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 3 | 11.23 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 4 | 10.70 | `free01/gemma4:e4b` |
| 5 | 10.67 | `batiai/gemma4-12b:iq3` |

Discrimination: 17 unique scores; max tie group 3. The top three are within
0.02, so keep a fallback chain rather than treating #1 as absolute.

## web_synth

| # | score | model |
|---|---|---|
| **1** | **12.50** | **`aratan/gemma-4-E4B-it-heretic:Q6_K`** |
| 2 | 12.50 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 3 | 12.08 | `free01/gemma4:e4b` |
| 4 | 11.91 | `fredrezones55/Qwopus3.5:9b` |
| 5 | 11.90 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |

Discrimination: 15 unique scores; max tie group 2. #1 and #2 are tied on
rounded score; `aratan` is listed first by runner order.

## code_gen

| # | score | model |
|---|---|---|
| **1** | **11.65** | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`** |
| 2 | 11.50 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 3 | 11.40 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 4 | 11.30 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 5 | 11.03 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |

Discrimination: 20 unique scores; max tie group 1.

## bug_finding

| # | score | model |
|---|---|---|
| 1 | **15.58** | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 2 | 14.50 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 3 | 14.18 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` |
| 4 | 13.74 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 5 | 13.70 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |

Grouped bug recall avoids counting several synonyms for the same planted bug.
Discrimination: 20 unique scores; max tie group 1.

## tool_call

| # | score | model |
|---|---|---|
| 1 | **10.35** | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 10.34 | `batiai/gemma4-e2b:q4` |
| 3 | 10.34 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 4 | 10.34 | `jaahas/crow:9b` |
| 5 | 10.34 | `free01/gemma4:e4b` |

Still near-saturated: 11 unique scores; max tie group 6. The #1 is stable but
future work should add retry/multi-turn tool-call cases.

## browser_tool

| # | score | model |
|---|---|---|
| 1 | **10.22** | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 10.20 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 10.20 | `free01/gemma4:e4b` |
| 4 | 10.20 | `batiai/gemma4-e4b:q4` |
| 5 | 10.20 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |

Still near-saturated: 14 unique scores; max tie group 6. `functiongemma` remains
the best browser/tool dispatch model.

## pdf_extract

| # | score | model |
|---|---|---|
| 1 | **12.00** | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 11.96 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 11.95 | `jaahas/crow:9b` |
| 4 | 11.95 | `free01/gemma4:e4b` |
| 5 | 11.95 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |

Discrimination improved with noisy/abstention cases: 15 unique scores; max tie
group 3.

## embedding_retrieval

| # | MRR | recall@5 | model |
|---|---|---|---|
| 1 | **1.000** | **1.000** | `embeddinggemma:latest` |
| 2 | **1.000** | **1.000** | `bge-m3:latest` |
| 3 | 0.875 | 1.000 | `nomic-embed-text:latest` |

`embeddinggemma` and `bge-m3` tie on this 8-case retrieval set; keep
`embeddinggemma` as default for existing cache compatibility and `bge-m3` as
multilingual fallback.

## Runtime Handling

The benchmark no longer hard-drops models solely for recoverable reasoning
traces. Smoke records `strippable=1`; `deep` includes those models by default
and scores cleaned output. Current installed generative lineup was clean
(20/20); the policy remains important for future reasoning-distilled pulls.

Runtime clients updated in this pass:

- shared `~/.claude/scripts/ollama_client.py`
- `agent-memory/src/agent_memory/shared/ollama.py`
- `cheap-llm/cheap_llm.py`
- `cli-orchestration/browser/_subagent_call.py`

## Per-task PRIMARY + FALLBACK

| task | PRIMARY | FALLBACK |
|---|---|---|
| improve | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| codeq_sum | `jaahas/crow:9b` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| smart_trim | `fredrezones55/Qwopus3.5:9b` | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| web_synth | `aratan/gemma-4-E4B-it-heretic:Q6_K` | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| code_gen | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| bug_finding | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| tool_call | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| browser_tool | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| pdf_extract | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| embedding | `embeddinggemma:latest` | `bge-m3:latest` |
