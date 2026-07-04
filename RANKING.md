# Current Ranking — installed Ollama models (snapshot 2026-07-04, Ollama 0.31.1)

> Combined rank = avg(deep_rank, tie_break_rank). Lower = better.
> Only **currently installed** models. For the full test history (incl. eliminated), see `RANKING_HISTORY.md`.


## improve

| # | combined | deep (rank/score) | tie-break (rank/score) | model |
|---|---|---|---|---|
| 1 | 2.5 | #2 / 3.44 | #3 / 8.57 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` |
| 2 | 3.5 | #6 / 2.59 | #1 / 8.75 | `Librellama/gemma4:e2b-Uncensored` |
| 3 | 5.5 | #1 / 4.74 | #10 / 3.82 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 4 | 6.5 | #9 / 2.21 | #4 / 8.52 | `jaahas/crow:9b` |
| 5 | 9.0 | #4 / 3.03 | #14 / 3.63 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |

## codeq_sum

| # | combined | deep (rank/score) | tie-break (rank/score) | model |
|---|---|---|---|---|
| 1 | 3.5 | #5 / 6.52 | #2 / 11.00 | `batiai/gemma4-e4b:q4` |
| 2 | 4.0 | #3 / 6.89 | #5 / 10.93 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 3 | 6.0 | #9 / 6.13 | #3 / 11.00 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 4 | 6.0 | #8 / 6.26 | #4 / 11.00 | `free01/gemma4:e4b` |
| 5 | 6.5 | #2 / 7.00 | #11 / 9.00 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |

## smart_trim

| # | combined | deep (rank/score) | tie-break (rank/score) | model |
|---|---|---|---|---|
| 1 | 1.0 | #1 / 7.00 | #1 / 10.50 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 2 | 6.5 | #3 / 7.00 | #10 / 10.50 | `fredrezones55/Qwopus3.5:9b` |
| 3 | 7.0 | #9 / 7.00 | #5 / 10.50 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 4 | 8.0 | #4 / 7.00 | #12 / 10.50 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 5 | 9.5 | #13 / 7.00 | #6 / 10.50 | `batiai/gemma4-e4b:q4` |

## web_synth

| # | combined | deep (rank/score) | tie-break (rank/score) | model |
|---|---|---|---|---|
| 1 | 5.0 | #6 / 7.00 | #4 / 10.50 | `batiai/gemma4-e4b:q4` |
| 2 | 6.0 | #7 / 7.00 | #5 / 10.50 | `batiai/gemma4-12b:iq3` |
| 3 | 6.5 | #4 / 7.00 | #9 / 10.50 | `free01/gemma4:e4b` |
| 4 | 7.5 | #12 / 7.00 | #3 / 10.50 | `Librellama/gemma4:e2b-Uncensored` |
| 5 | 8.0 | #15 / 5.00 | #1 / 10.50 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |

## code_gen

| # | combined | deep (rank/score) | tie-break (rank/score) | model |
|---|---|---|---|---|
| 1 | 6.0 | #7 / 6.00 | #5 / 16.00 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 2 | 6.0 | #3 / 6.00 | #9 / 16.00 | `fredrezones55/Qwopus3.5:9b` |
| 3 | 7.0 | #1 / 7.00 | #13 / 16.00 | `qwen3.5:4b` |
| 4 | 7.5 | #9 / 6.00 | #6 / 16.00 | `batiai/gemma4-e4b:q4` |
| 5 | 8.0 | #6 / 6.00 | #10 / 16.00 | `free01/gemma4:e4b` |

## bug_finding (separate bench: count bugs found in a diff)

| # | score | model |
|---|---|---|
| 1 | 15.21 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 2 | 15.00 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 3 | 14.56 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 4 | 14.40 | `Librellama/gemma4:e2b-Uncensored` |
| 5 | 14.26 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |

## Per-task PRIMARY + FALLBACK (wired into harness)

| task | PRIMARY (#1) | FALLBACK (#2) |
|---|---|---|
| improve | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | `Librellama/gemma4:e2b-Uncensored` |
| codeq_sum | `batiai/gemma4-e4b:q4` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| smart_trim | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `fredrezones55/Qwopus3.5:9b` |
| web_synth | `batiai/gemma4-e4b:q4` | `batiai/gemma4-12b:iq3` |
| code_gen | `fredrezones55/Qwopus3.5:9b` | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| bug_finding | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |

## Installed models (18 = 16 LLM + 2 embeddings)

- `Librellama/gemma4:e2b-Uncensored` 
- `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` 
- `aratan/gemma-4-E4B-it-heretic:Q6_K` 
- `batiai/gemma4-12b:iq3` 
- `batiai/gemma4-e2b:q4` 
- `batiai/gemma4-e4b:q4` 
- `cryptidbleh/gemma4-claude-opus-4.6:latest` 
- `cryptidbleh/gemma4-claude-sonnet-4.6:latest` 
- `embeddinggemma:latest` (embedding)
- `fredrezones55/Qwopus3.5:9b` 
- `free01/gemma4:e4b` 
- `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` 
- `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` 
- `jaahas/crow:9b` 
- `nomic-embed-text:latest` (embedding)
- `qwen3.5:4b` 
- `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` 
- `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` 
