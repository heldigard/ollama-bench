# Ollama Tie-Break — Hard Prompts + Structural Scoring (2026-07-04)

Each task uses a HARDER prompt + structural scoring (no 7.0 cap).
Range -5 to +15. Higher = better.

## improve

| # | Score | Model |
|---|---|---|
| 1 | 9.16 | `qwen2.5:3b` |
| 2 | 9.09 | `fredrezones55/Qwopus3.5:9b` |
| 3 | 8.99 | `ducquoc/gemma4-fast-sonnet:latest` |
| 4 | 8.91 | `batiai/gemma4-12b:q3` |
| 5 | 8.87 | `hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` |
| 6 | 8.83 | `batiai/gemma4-12b:iq4` |
| 7 | 8.79 | `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest` |
| 8 | 8.75 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 9 | 8.65 | `batiai/gemma4-12b:q4` |
| 10 | 8.63 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 11 | 5.72 | `jaahas/crow:9b` |
| 12 | 4.73 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 13 | 4.36 | `Librellama/gemma4:e2b-Uncensored` |
| 14 | 4.08 | `qwen3.5:4b` |
| 15 | 3.96 | `batiai/gemma4-12b:q2` |
| 16 | 3.75 | `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` |
| 17 | 3.65 | `ssfdre38/gemma4-turbo:latest` |
| 18 | 2.23 | `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` |
| 19 | 2.08 | `ssfdre38/gemma4-turbo:e2b` |
| 20 | 1.99 | `batiai/gemma4-e2b:q6` |
| 21 | 1.95 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest` |
| 22 | 1.79 | `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M` |
| 23 | 1.69 | `batiai/gemma4-12b:iq3` |

## codeq_sum

| # | Score | Model |
|---|---|---|
| 1 | 11.00 | `fredrezones55/Qwopus3.5:9b` |
| 2 | 11.00 | `batiai/gemma4-12b:q2` |
| 3 | 11.00 | `Librellama/gemma4:e2b-Uncensored` |
| 4 | 11.00 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 5 | 11.00 | `ducquoc/gemma4-fast-sonnet:latest` |
| 6 | 10.10 | `batiai/gemma4-12b:q3` |
| 7 | 9.27 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 8 | 9.00 | `qwen3.5:4b` |
| 9 | 9.00 | `batiai/gemma4-e2b:q6` |
| 10 | 9.00 | `ssfdre38/gemma4-turbo:e2b` |
| 11 | 9.00 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 12 | 9.00 | `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` |
| 13 | 8.59 | `hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` |
| 14 | 8.15 | `batiai/gemma4-12b:q4` |
| 15 | 8.10 | `batiai/gemma4-12b:iq3` |
| 16 | 8.08 | `jaahas/crow:9b` |
| 17 | 7.00 | `qwen2.5:3b` |
| 18 | 6.13 | `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` |
| 19 | 6.13 | `batiai/gemma4-12b:iq4` |
| 20 | 6.11 | `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest` |
| 21 | 6.10 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest` |
| 22 | 6.08 | `ssfdre38/gemma4-turbo:latest` |
| 23 | 6.08 | `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M` |

## smart_trim

| # | Score | Model |
|---|---|---|
| 1 | 10.50 | `qwen3.5:4b` |
| 2 | 10.50 | `fredrezones55/Qwopus3.5:9b` |
| 3 | 10.50 | `batiai/gemma4-e2b:q6` |
| 4 | 10.50 | `Librellama/gemma4:e2b-Uncensored` |
| 5 | 10.50 | `ssfdre38/gemma4-turbo:e2b` |
| 6 | 10.50 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 7 | 10.50 | `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` |
| 8 | 10.50 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 9 | 10.50 | `ssfdre38/gemma4-turbo:latest` |
| 10 | 10.50 | `batiai/gemma4-12b:q3` |
| 11 | 10.50 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 12 | 10.50 | `ducquoc/gemma4-fast-sonnet:latest` |
| 13 | 10.50 | `batiai/gemma4-12b:iq3` |
| 14 | 10.50 | `batiai/gemma4-12b:q4` |
| 15 | 9.00 | `qwen2.5:3b` |
| 16 | 8.14 | `batiai/gemma4-12b:iq4` |
| 17 | 8.11 | `batiai/gemma4-12b:q2` |
| 18 | 7.98 | `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest` |
| 19 | 7.97 | `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` |
| 20 | 7.91 | `hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` |
| 21 | 7.87 | `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M` |
| 22 | 7.85 | `jaahas/crow:9b` |
| 23 | 7.78 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest` |

## web_synth

| # | Score | Model |
|---|---|---|
| 1 | 6.00 | `batiai/gemma4-e2b:q6` |
| 2 | 6.00 | `Librellama/gemma4:e2b-Uncensored` |
| 3 | 6.00 | `ssfdre38/gemma4-turbo:e2b` |
| 4 | 6.00 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 5 | 6.00 | `qwen2.5:3b` |
| 6 | 6.00 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 7 | 6.00 | `ssfdre38/gemma4-turbo:latest` |
| 8 | 6.00 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 9 | 6.00 | `ducquoc/gemma4-fast-sonnet:latest` |
| 10 | 4.02 | `batiai/gemma4-12b:iq3` |
| 11 | 3.79 | `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` |
| 12 | 3.75 | `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest` |
| 13 | 3.72 | `fredrezones55/Qwopus3.5:9b` |
| 14 | 3.70 | `batiai/gemma4-12b:iq4` |
| 15 | 3.69 | `batiai/gemma4-12b:q4` |
| 16 | 3.48 | `hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` |
| 17 | 3.43 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest` |
| 18 | 3.43 | `batiai/gemma4-12b:q3` |
| 19 | 1.00 | `qwen3.5:4b` |
| 20 | 1.00 | `batiai/gemma4-12b:q2` |
| 21 | 1.00 | `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` |
| 22 | -1.07 | `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M` |
| 23 | -4.10 | `jaahas/crow:9b` |

## code_gen

| # | Score | Model |
|---|---|---|
| 1 | 16.00 | `qwen3.5:4b` |
| 2 | 16.00 | `jaahas/crow:9b` |
| 3 | 16.00 | `batiai/gemma4-e2b:q6` |
| 4 | 16.00 | `batiai/gemma4-12b:q2` |
| 5 | 16.00 | `ssfdre38/gemma4-turbo:e2b` |
| 6 | 16.00 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 7 | 16.00 | `qwen2.5:3b` |
| 8 | 16.00 | `ssfdre38/gemma4-turbo:latest` |
| 9 | 16.00 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| 10 | 16.00 | `ducquoc/gemma4-fast-sonnet:latest` |
| 11 | 16.00 | `batiai/gemma4-12b:iq3` |
| 12 | 13.33 | `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest` |
| 13 | 13.31 | `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` |
| 14 | 13.30 | `batiai/gemma4-12b:iq4` |
| 15 | 13.27 | `batiai/gemma4-12b:q4` |
| 16 | 13.27 | `fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M` |
| 17 | 13.25 | `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` |
| 18 | 13.23 | `Librellama/gemma4:e2b-Uncensored` |
| 19 | 13.21 | `fredrezones55/Qwopus3.5:9b` |
| 20 | 13.21 | `batiai/gemma4-12b:q3` |
| 21 | 13.19 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 22 | 13.18 | `hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0` |
| 23 | 13.18 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest` |

