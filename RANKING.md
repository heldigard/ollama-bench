# Current Ranking — installed Ollama models (snapshot 2026-07-05, Ollama 0.31.1)

> Combined rank = avg(deep_rank, tie_break_rank). Lower = better.
> Only **currently installed** models. For the full test history (incl. eliminated), see `RANKING_HISTORY.md`.
>
> **2026-07-05 round-3 update**: added `Grug-12B` (improve PRIMARY via 2× hard-prompt win) + `HauhauCS Gemma4 Balanced` (code_gen tier-2 saturated tie). DeepSeek-V4-Flash dropped (leak). Full report: `topics/candidates-round-3-2026-07-05.md`.


## improve

| # | combined | deep (rank/score) | tie-break (rank/score) | model |
|---|---|---|---|---|
| **1** | **1.0** | **#1 / 3.54** | **#1 / 8.39 (verified 8.53)** | **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** ← **NEW #1 (2026-07-05)** |
| 2 | 2.5 | #2 / 3.44 | #3 / 4.15 (was 8.57 in pre-7/5 bench) | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` (demoted to #2) |
| 3 | 3.5 | #6 / 2.59 | — / 5.08 (round-3 tie-break) | `Librellama/gemma4:e2b-Uncensored` |
| 4 | 5.5 | — / — | — / — | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 5 | 6.5 | #9 / 2.21 | #4 / 8.52 | `jaahas/crow:9b` |

> Note: pegasus912's pre-7/5 tie-break score of 8.57 was on a different prompt iteration;
> 2026-07-05 re-run on Grug vs pegasus912-only gave pegasus912 4.37 (Grug 8.53, delta +4.16).
> Grug-12B confirmed winner under both bench seeds.

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
| 2 | 6.0 | #5 / 6.00 | #1 / 16.00 (round-3) | **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** (saturated tie — rewire TBD) |
| 2 | 6.0 | — / — | #1 / 16.00 (round-3, ties 3-way) | **`hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M`** ← NEW 2026-07-05 |
| 3 | 7.0 | #1 / 7.00 | #13 / 16.00 | `qwen3.5:4b` |

## bug_finding (separate bench: count bugs found in a diff)

| # | score | model |
|---|---|---|
| 1 | **18.50** | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` (re-verified 2026-07-05) |
| 2 | **15.35** | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` (re-verified 2026-07-05) |
| 3 | **15.09** | **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** ← NEW 2026-07-05 (only 0.26 below #2) |
| 4 | 14.37 | **`hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M`** ← NEW 2026-07-05 |
| 5 | 12.15 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |

## tool_call (structured JSON output — new slice, ground-truth)

| # | score | model |
|---|---|---|
| 1 | **9.85** | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` (function-calling fine-tune; re-verified 2026-07-05) |
| 2 | **9.82** | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` (re-verified 2026-07-05) |
| 2 | **9.81** | **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** ← NEW 2026-07-05 (0.01 within noise vs huihui) |
| 4 | 9.02 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` ← NEW 2026-07-05 |
| 5 | 8.67 | `kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest` |

> **Update 2026-07-05**: Grug-12B is statistically tied with huihui (9.81 vs 9.82, within tps-bonus noise).
> Either is a safe #1. functiongemma is the original champion.
>
> tool_call harness wiring status:  subagent PRIMARY=functiongemma
> (per ). Grug-12B / huihui are drop-in alternates.

## browser_tool (ref-grounded a11y action — new slice, ground-truth)

| # | score | model |
|---|---|---|
| 1 | **10.19** | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` (browser #1 + tool_call #1) |
| 2 | 10.18 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 10.15 | `jaahas/crow:9b` |
| 4 | 10.01 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 5 | 9.70 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` (was the agent-browser PROXY PRIMARY — retired: only #5) |
| 6 | 8.06 | `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` |

> agent_browser_subagent.py rewired 2026-07-04: PRIMARY = functiongemma (#1), FALLBACK =
> pegasus912 (#5, gemma4 family diversity). Both now BENCHED, no more proxies.

## pdf_extract (schema field extraction + abstention — new slice, ground-truth)

| # | score | model |
|---|---|---|
| 1 | **11.15** | `jaahas/crow:9b` |
| 2 | 11.14 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 11.14 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` (pdf-extract-structured.py default — proxy RETIRED: confirmed tied #1) |
| 2 | 11.14 | `batiai/gemma4-12b:iq3` |
| 5 | 11.13 | `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` |
| 6 | 11.12 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |

> Field saturated within 0.03 (6 models) — pdf extraction at this difficulty is easy for the
> whole lineup; pegasus912 is a sound default (crow:9b edges it on noise only). Harder docs
> (messy OCR, ambiguous tables) needed to discriminate further.

## Per-task PRIMARY + FALLBACK (wired into harness)

| task | PRIMARY (#1) | FALLBACK (#2) |
|---|---|---|
| improve | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | `Librellama/gemma4:e2b-Uncensored` |
| codeq_sum | `batiai/gemma4-e4b:q4` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| smart_trim | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `fredrezones55/Qwopus3.5:9b` |
| web_synth | `batiai/gemma4-e4b:q4` | `batiai/gemma4-12b:iq3` |
| code_gen | `fredrezones55/Qwopus3.5:9b` | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| bug_finding | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |
| browser_tool | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` (gemma4 family diversity) |
| pdf_extract | `jaahas/crow:9b` (11.15, edge) | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` (tied 11.14; current pdf-extract default) |

## Installed models (22 = 19 LLM + 3 embeddings)

- `Librellama/gemma4:e2b-Uncensored`
- `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest`
- `aratan/gemma-4-E4B-it-heretic:Q6_K`
- `batiai/gemma4-12b:iq3`
- `batiai/gemma4-e4b:q4`
- `bge-m3:latest` (embedding — multilingual #1, dim 1024, added 2026-07-04)
- `cryptidbleh/gemma4-claude-opus-4.6:latest`
- `cryptidbleh/gemma4-claude-sonnet-4.6:latest`
- `embeddinggemma:latest` (embedding)
- `fredrezones55/Qwopus3.5:9b`
- `free01/gemma4:e4b`
- `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL`
- `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest`
- `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` (tool_call #1 + code_gen #1-tier, added 2026-07-04)
- `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` (bug_finding #2 + code_gen tied #1, added 2026-07-04)
- `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` (bug_finding #1, added 2026-07-04)
- `jaahas/crow:9b`
- `kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest` (reasoning; leaks `<think>` strippable; added 2026-07-04)
- `nomic-embed-text:latest` (embedding)
- `qwen3.5:4b`
- `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0`
- `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`
