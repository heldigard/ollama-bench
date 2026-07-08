# Tool-Call Bench — structured JSON output

Scoring: +3 valid JSON, +2 per ground-truth hit (tool name + key arg values), leak penalty, tps bonus. 9 cases per model.

| # | Score | Model |
|---|---|---|
| 1 | 10.36 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| 2 | 10.34 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 3 | 10.34 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 4 | 10.34 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` |
| 5 | 10.34 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| 6 | 10.34 | `jaahas/crow:9b` |
| 7 | 10.34 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 8 | 10.30 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` |
| 9 | 10.11 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 10 | 9.90 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 11 | 9.68 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 12 | 8.35 | `hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M` |
