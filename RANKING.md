# Current Role Wiring + Historical Ranking

## Wiring validation (2026-07-09, Ollama 0.31.2)

Risk-weighted semantic scorer, task-specific consumer protocol, seed 42, two
stored response sets plus a fresh final run. Speed contributes at most 0.25;
authority, error-branch, security, and verification cases receive 2x weight.
Full evidence: `results_wiring_validation_20260709.md`.

| task | PRIMARY | FALLBACK | repeated score |
|---|---|---|---|
| improve | `cryptidbleh/gemma4-claude-opus-4.6:latest` | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` | 3.50 / 2.70 |
| codeq_sum | `batiai/gemma4-e4b:q4` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | 9.18 / 8.99 |
| smart_trim | `batiai/gemma4-e2b:q4` | `cryptidbleh/gemma4-claude-opus-4.6:latest` | 11.81 / 11.63 |

The tables below preserve the full 2026-07-08 PM pipeline snapshot. Do not
compare their absolute scores with the quality-first validation above.

## Full-field snapshot (2026-07-08 PM, Ollama 0.31.1)

> Full pipeline: smoke 31/31 → deep (30×33, --strip) → tie-break (26×15) →
> bug_finding/tool_call/pdf_extract (×30) → pdf_ocr (×2). Canonical #1 = COMBINED
> rank (deep+tiebreak)/2. Lineup trimmed to top-5 union (losers deleted).
> config.py primaries/fallbacks + cross-CLI consumers rewired from this run.
> Rows marked *(deleted)* were benched then trimmed from the installed lineup; PRIMARY/FALLBACK below are all installed.

## improve

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | 7.74 | 6.40 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 2 | 6.30 | 6.65 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| 3 | 5.87 | 6.95 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` |
| 4 | 6.64 | 6.07 | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| 5 | 5.90 | 6.00 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |

Discrimination: 30 models scored; combined deep+tiebreak rank.

## codeq_sum

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | 10.24 | 11.20 | `batiai/gemma4-e4b:q4` |
| 2 | 10.01 | 11.25 | `jaahas/crow:9b` |
| 3 | 10.15 | 11.07 | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| 4 | 9.52 | 11.77 | `Librellama/gemma4:e2b-Uncensored` |
| 5 | 9.53 | 11.47 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |

Discrimination: 30 models scored; combined deep+tiebreak rank.

## smart_trim

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | 12.30 | 13.53 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 2 | 12.10 | 12.28 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 3 | 12.19 | 11.93 | `batiai/gemma4-e2b:q4` |
| 4 | 12.10 | 12.28 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` |
| 5 | 12.19 | 11.78 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |

Discrimination: 30 models scored; combined deep+tiebreak rank.

## web_synth

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | 11.85 | 12.83 | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` |
| 2 | 11.92 | 12.20 | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 3 | 11.95 | 12.03 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| 4 | 11.67 | 12.83 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 5 | 12.27 | 11.13 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |

Discrimination: 30 models scored; combined deep+tiebreak rank.

## code_gen

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | 12.13 | 8.23 | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` |
| 2 | 11.79 | 8.25 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 3 | 11.79 | 7.55 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 4 | 11.79 | 7.40 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 5 | 11.84 | 6.92 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |

Discrimination: 30 models scored; combined deep+tiebreak rank.

## bug_finding

| # | score | model |
|---|---|---|
| **1** | 15.43 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 2 | 14.99 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| 3 | 14.70 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` |
| 4 | 14.60 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 5 | 14.49 | `hf.co/mradermacher/Gemma-4-12B-StyleTune-i1-GGUF:Q4_K_M` *(deleted)* |

## tool_call

| # | score | model |
|---|---|---|
| **1** | 10.10 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 2 | 10.09 | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| 3 | 9.95 | `hf.co/FadedRedStar/Qwen3.5-9B-heretic-GGUF:Q4_K_M` *(deleted)* |
| 4 | 9.95 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` *(deleted)* |
| 5 | 9.95 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` |

## pdf_extract

| # | score | model |
|---|---|---|
| **1** | 12.07 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 2 | 12.06 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| 3 | 12.06 | `qwen3.5:4b` *(deleted)* |
| 4 | 12.05 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 5 | 12.03 | `hf.co/FadedRedStar/Qwen3.5-9B-heretic-GGUF:Q4_K_M` *(deleted)* |

## pdf_ocr

| # | score | avg recall | model |
|---|---:|---:|---|
| **1** | 12.00 |  | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` |
| 2 | 11.18 |  | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` |

Separate rendered-PDF OCR category. Unlimited-OCR needs `/api/chat` vision + `ocr [img]`.

## embedding_retrieval

| # | MRR | recall@5 | model |
|---|---|---|---|
| 1 | **1.000** | **1.000** | `embeddinggemma:latest` |
| 2 | **1.000** | **1.000** | `bge-m3:latest` |
| 3 | 0.875 | 1.000 | `nomic-embed-text:latest` |

## Per-task PRIMARY + FALLBACK (validated 2026-07-09)

| task | PRIMARY | FALLBACK |
|---|---|---|
| improve | `cryptidbleh/gemma4-claude-opus-4.6:latest` | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| codeq_sum | `batiai/gemma4-e4b:q4` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| smart_trim | `batiai/gemma4-e2b:q4` | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| web_synth | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M ← NEW` | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| code_gen | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M ← NEW` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| bug_finding | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest ← NEW` | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| tool_call | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest ← NEW` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| browser_tool | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest ← NEW` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| pdf_extract | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest ← NEW` | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` |
| embedding | `embeddinggemma:latest` | `bge-m3:latest` |

## Highlights (2026-07-08 PM)

- **OmniCoder**: bug_finding #1; removed from prompt rewriting after fidelity regressions.
- **SetneufPT/Qwopus3.5**: tool_call + pdf_extract + browser_tool #1. Structured-output champion.
- **batiai/gemma4-e2b**: smart_trim #1. **TeichAI/Fable-5-v1**: web_synth combined #1.
- **prithiv/lift**: code_gen #1 + pdf_ocr fallback. **DeltaCoder + Openclaw** (prior champs) fell out of top-5.
- 7/9 PRIMARY changed; improve + pdf_ocr held. 12 loser models deleted; qwen3.5:4b replaced by cryptidbleh/gemma4-claude-opus-4.6 (better on every metric: 9.97 vs 8.85 avg, faster).

## Runtime notes

- Smoke records `strippable=1`; `deep --strip` includes them, scoring cleaned output.
- Unlimited-OCR is vision-only (`/api/chat` + `ocr [img]`); general models score -100 on pdf_ocr.
- `cryptidbleh/gemma4-claude-opus-4.6` is the prompt-improve primary and smart-trim fallback. It replaced qwen3.5:4b as the lightweight infra default.
