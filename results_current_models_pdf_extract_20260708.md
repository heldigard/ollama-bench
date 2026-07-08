# PDF-Extract Bench — schema-driven field extraction

Scoring: +3 valid JSON, +1.5 per correct field value, +2 abstention on absent fields (-2 hallucinate), leak penalty, tps bonus. 8 cases per model.

| # | Score | Model |
|---|---|---|
| 1 | 12.05 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| 2 | 11.96 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 3 | 11.96 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 4 | 11.96 | `jaahas/crow:9b` |
| 5 | 11.95 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 6 | 11.95 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 7 | 11.75 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` |
| 8 | 11.72 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 9 | 11.72 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| 10 | 11.55 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
