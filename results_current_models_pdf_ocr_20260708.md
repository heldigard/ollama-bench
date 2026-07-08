# PDF-OCR Bench — rendered PDF page OCR

Prompt: `ocr [img]`. Scoring: 10 * recall - 4 * hallucination_rate + speed bonus capped at 2. 3 synthetic PDF cases per model.

| # | Score | Avg Recall | Model |
|---|---:|---:|---|
| 1 | 12.00 | 1.00 | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` |
| 2 | 11.15 | 1.00 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 11.12 | 1.00 | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` |
| 4 | 11.11 | 1.00 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| 5 | 11.09 | 1.00 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| 6 | 10.68 | 1.00 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 7 | -100.00 | 0.00 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 8 | -100.00 | 0.00 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` |
| 9 | -100.00 | 0.00 | `jaahas/crow:9b` |
| 10 | -100.00 | 0.00 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |

## Per-Case Details

### `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 12.00 | 1.00 | 0.00 | 4.71 | 573.1 |
| lab_report | 12.00 | 1.00 | 0.00 | 0.65 | 573.3 |
| statement_noise | 12.00 | 1.00 | 0.00 | 0.60 | 581.1 |

### `hf.co/prithivMLmods/lift-GGUF:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.10 | 1.00 | 0.00 | 17.08 | 110.2 |
| lab_report | 11.12 | 1.00 | 0.00 | 1.71 | 111.7 |
| statement_noise | 11.14 | 1.00 | 0.00 | 1.82 | 114.4 |

### `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.11 | 1.00 | 0.00 | 11.29 | 111.2 |
| lab_report | 11.07 | 1.00 | 0.00 | 2.08 | 107.5 |
| statement_noise | 11.10 | 1.00 | 0.00 | 2.05 | 109.9 |

### `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| lab_report | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| statement_noise | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |

### `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.12 | 1.00 | 0.00 | 11.20 | 112.5 |
| lab_report | 11.12 | 1.00 | 0.00 | 1.83 | 112.4 |
| statement_noise | 11.09 | 1.00 | 0.00 | 1.99 | 108.8 |

### `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| lab_report | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| statement_noise | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |

### `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.14 | 1.00 | 0.00 | 11.36 | 113.7 |
| lab_report | 11.15 | 1.00 | 0.00 | 1.77 | 115.1 |
| statement_noise | 11.15 | 1.00 | 0.00 | 1.93 | 115.3 |

### `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 10.68 | 1.00 | 0.00 | 14.41 | 67.8 |
| lab_report | 10.68 | 1.00 | 0.00 | 1.74 | 67.8 |
| statement_noise | 10.69 | 1.00 | 0.00 | 4.47 | 68.7 |

### `jaahas/crow:9b`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| lab_report | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| statement_noise | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |

### `aratan/gemma-4-E4B-it-heretic:Q6_K`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| lab_report | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| statement_noise | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |

