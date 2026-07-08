# PDF-OCR Bench — rendered PDF page OCR

Prompt: `ocr [img]`. Scoring: 10 * recall - 4 * hallucination_rate + speed bonus capped at 2. 3 synthetic PDF cases per model.

| # | Score | Avg Recall | Model |
|---|---:|---:|---|
| 1 | 12.00 | 1.00 | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` |
| 2 | 11.08 | 1.00 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 11.05 | 1.00 | `fredrezones55/Qwopus3.5:9b` |
| 4 | 10.77 | 1.00 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 5 | 10.52 | 0.89 | `qwen3.5:4b` |
| 6 | 9.16 | 0.83 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` |

## Per-Case Details

### `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 12.00 | 1.00 | 0.00 | 1.50 | 578.7 |
| lab_report | 12.00 | 1.00 | 0.00 | 0.61 | 579.9 |
| statement_noise | 12.00 | 1.00 | 0.00 | 0.60 | 581.0 |

### `qwen3.5:4b`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.64 | 1.00 | 0.00 | 5.96 | 163.8 |
| lab_report | 8.29 | 0.67 | 0.00 | 1.29 | 161.9 |
| statement_noise | 11.63 | 1.00 | 0.00 | 2.45 | 162.8 |

### `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.07 | 1.00 | 0.00 | 16.19 | 107.4 |
| lab_report | 11.07 | 1.00 | 0.00 | 2.00 | 107.3 |
| statement_noise | 11.09 | 1.00 | 0.00 | 2.06 | 109.4 |

### `fredrezones55/Qwopus3.5:9b`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 11.07 | 1.00 | 0.00 | 17.12 | 106.8 |
| lab_report | 11.04 | 1.00 | 0.00 | 1.99 | 104.3 |
| statement_noise | 11.03 | 1.00 | 0.00 | 2.20 | 103.4 |

### `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 10.73 | 1.00 | 0.00 | 10.97 | 72.9 |
| lab_report | 10.79 | 1.00 | 0.00 | 1.50 | 78.8 |
| statement_noise | 10.79 | 1.00 | 0.00 | 3.84 | 78.9 |

### `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL`

| Case | Score | Recall | Hallucination | Seconds | tok/s |
|---|---:|---:|---:|---:|---:|
| invoice_table | 10.82 | 1.00 | 0.00 | 12.17 | 82.5 |
| lab_report | 5.82 | 0.50 | 0.00 | 2.61 | 82.1 |
| statement_noise | 10.85 | 1.00 | 0.00 | 3.62 | 84.5 |

