# Bug-Finding Bench — diff-review task

Scoring: grouped bug recall + COUNT calibration - leak_penalty + tps_bonus. 4 diffs per model.

| # | Score | Model |
|---|---|---|
| 1 | 14.06 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` |
| 2 | 14.04 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 3 | 14.02 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 4 | 13.94 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 5 | 13.75 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` |
| 6 | 13.69 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 7 | 13.59 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` |
| 8 | 13.25 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` |
| 9 | 13.01 | `jaahas/crow:9b` |
| 10 | 12.79 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| 11 | 11.78 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
