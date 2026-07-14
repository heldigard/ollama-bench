# Current Role Wiring + Historical Ranking

## Wiring validation (2026-07-09, Ollama 0.31.2)

Risk-weighted semantic scorer, task-specific consumer protocol, seed 42, two
stored response sets plus a fresh final run. Speed contributes at most 0.25;
authority, error-branch, security, and verification cases receive 2x weight.
Full evidence: `results_wiring_validation_20260709.md`.

| task | PRIMARY | FALLBACK | repeated score |
|---|---|---|---|
| improve | `cryptidbleh/gemma4-claude-opus-4.6:latest` | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | 2.97 / 2.46 |
| codeq_sum | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` | 9.84 / 9.40 |
| smart_trim | `batiai/gemma4-e2b:q4` | `cryptidbleh/gemma4-claude-opus-4.6:latest` | 11.67 / 11.63 |

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
| **1** | **2.97** | (round-17 fresh) | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| **2** | 2.46 | (round-17 fresh) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` |
| 3 | 2.03 | (round-17 fresh) | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| 4 | 1.68 | (round-17 fresh) | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 5 | 0.93 | (round-17 fresh) | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| *(round-10 #1, demoted round-17)* | 2.46 | (round-10 only) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` |
| *(round-7 #1, held round-10, removed round-17)* | 7.74 | 6.40 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |

Discrimination: round-17 2026-07-13 fresh 5-way deep re-bench (smoke-passed models: cryptidbleh, TeichAI, Negentropy-9B, SetneufPT, OmniCoder). Round-10 4-way did NOT include cryptidbleh (chain tail, legacy 2026-07-09 #1, smart_trim round-15 #2) — its strength was never re-validated against TeichAI. Round-17 caught the drift: **cryptidbleh 2.97 dethroned TeichAI 2.46 (+0.51, +21%)**. OmniCoder held lowest (0.93), confirmed demoted to bug_finding/pdf_extract depth only. Round-7 historical *(held)* row preserved for reference (old cap-of-7.0 scoring). See `topics/candidates-round-17-2026-07-13.md`.

## codeq_sum

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | **9.84** | (round-17 fresh) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` |
| **2** | 9.40 | (round-17 fresh) | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` |
| 3 | 9.19 | (round-17 fresh) | `batiai/gemma4-e4b:q4` |
| 4 | 8.99 | (round-17 fresh) | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 5 | 8.87 | (round-17 fresh) | `jaahas/crow:9b` |
| *(round-9 #1, demoted round-17)* | 9.40 | 9.93 | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` |

Discrimination: round-17 2026-07-13 fresh 5-way deep re-bench (smoke-passed: TeichAI, Qwythos, batiai/e4b, SetneufPT, jaahas/crow). Round-9/10 blind spot: TeichAI (web_synth + improve champion) was never tested against Qwythos in codeq_sum directly. Round-17 caught the drift: **TeichAI 9.84 dethroned Qwythos 9.40 (+0.44, +4.7%)**. Qwythos demoted to fallback. batiai/e4b held at #3. SetneufPT held at #4. jaahas/crow held at #5. Round-9 historical *(held)* row preserved for reference. See `topics/candidates-round-17-2026-07-13.md`.

## smart_trim

| # | deep | tiebreak | model |
|---|---|---|---|
| **1** | 11.67 | round-15 cross-validation | `batiai/gemma4-e2b:q4` |
| 2 | 11.63 | round-15 cross-validation | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| 3 | 10.79 | round-10 4-way | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 4 | 9.87 | round-10 4-way | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |

Discrimination: round-15 2026-07-13 cross-validation (same round, same smart_trim rubric) scored batiai-e2b 11.67 and cryptidbleh 11.63 ABOVE SC117 10.79 and Hauhau 9.87. Quality governs, not throughput: batiai-e2b wins on score. The earlier round-15 "candidate" demotion was a name-bias error ('e2b' was treated as a low-fidelity tiny though Ollama reports it as 4.6B); reverted. batiai-e2b also held smart_trim #3 (11.93) in round-7 — two consistent data points above SC117.

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
| **1** | 14.97 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| 2 | 14.70 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` |
| 3 | 14.68 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |
| 4 | 14.49 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 5 | 14.06 | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` |
| *(round-7 #1)* | 15.43 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` (held, now #4 above) |

Discrimination: 30 models scored; combined deep+tiebreak rank. Round-10 2026-07-12 cross-task promotion: **xentriom Q8_0 (web_synth champion) dethroned OmniCoder in 5-way specialized bug_finding (14.97 vs 14.49, +0.48)**. WARNING: xentriom Q8_0 = 12GB VRAM; OmniCoder retained as fallback for VRAM-tight contexts. TeichAI 14.06 (#5) — no displace. See `topics/candidates-round-10-2026-07-12.md`.

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
| **1** | 12.05 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| **2** | 12.00 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 3 | 11.97 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| 4 | 11.80 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 5 | 12.03 *(deleted)* | `hf.co/FadedRedStar/Qwen3.5-9B-heretic-GGUF:Q4_K_M` |

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
| improve | `cryptidbleh/gemma4-claude-opus-4.6:latest` | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` |
| codeq_sum | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` |
| smart_trim | `batiai/gemma4-e2b:q4` | `cryptidbleh/gemma4-claude-opus-4.6:latest` |
| web_synth | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| code_gen | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| bug_finding | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| tool_call | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| browser_tool | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| pdf_extract | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
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
- `cryptidbleh/gemma4-claude-opus-4.6` is the prompt-improve primary (round-17 2026-07-13 fresh 5-way 2.97) and smart-trim fallback. It replaced qwen3.5:4b as the lightweight infra default. Multi-task champion: improve #1 + smart_trim #2.
