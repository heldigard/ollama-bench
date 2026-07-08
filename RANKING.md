# Current Ranking — installed Ollama models (snapshot 2026-07-08, Ollama 0.31.1)

> Refactor run: `deep_refactor_20260708` + specialized benches.
> The old first-pass cap produced large ties; the new canonical task scorers
> report 15-20 unique scores per canonical task. Smoke: 20/20 generative models
> clean; embeddings skipped from generate smoke and evaluated separately.

## improve

| # | score | model |
|---|---|---|
| **1** | **7.01** | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`** ← NEW 2026-07-08 |
| 2 | 6.46 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` ← NEW |
| 3 | 6.39 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |
| 4 | 6.23 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` ← NEW |
| 5 | 6.07 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |

Discrimination: 14 unique scores; max tie group 1. OmniCoder overtakes SetneufPT
(5.79, now #8) by +1.22. SetneufPT still strong on codeq_sum/smart_trim but no
longer improve #1.

## codeq_sum

| # | score | model |
|---|---|---|
| **1** | **9.57** | **`jaahas/crow:9b`** ← confirmed #1 |
| 2 | 9.15 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| 3 | 8.91 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 4 | 8.90 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` ← NEW |
| 5 | 8.46 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |

Discrimination: 14 unique scores; max tie group 1. crow:9b remains dominant.

## smart_trim

| # | score | model |
|---|---|---|
| **1** | **11.53** | **`hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M`** ← NEW 2026-07-08 |
| 2 | 11.33 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 3 | 11.25 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 4 | 11.24 | `fredrezones55/Qwopus3.5:9b` |
| 5 | 11.23 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` ← NEW |

Discrimination: 13 unique scores; max tie group 2. Top-5 within 0.30 — Openclaw
edges out but fallback chain is dense. SetneufPT dropped to #13 (9.35) in this
14-model subset.

## web_synth

| # | score | model |
|---|---|---|
| **1** | **12.50** | **`hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M`** ← NEW 2026-07-08 (tie) |
| **1** | **12.50** | **`aratan/gemma-4-E4B-it-heretic:Q6_K`** (tie) |
| 3 | 12.20 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 4 | 12.17 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |
| 5 | 11.96 | `fredrezones55/Qwopus3.5:9b` |

Discrimination: 13 unique scores; max tie group 2. DeltaCoder ties aratan at #1.

## code_gen

| # | score | model |
|---|---|---|
| **1** | **11.65** | **`hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M`** ← NEW 2026-07-08 |
| 2 | 11.65 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` (tied) |
| 3 | 11.50 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 4 | 11.48 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` ← NEW |
| 5 | 11.40 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |

Discrimination: 12 unique scores; max tie group 2.

## bug_finding

| # | score | model |
|---|---|---|
| 1 | **14.06** | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` ← NEW 2026-07-08 |
| 2 | 14.04 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 3 | 14.02 | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| 4 | 13.94 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 5 | 13.75 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` ← NEW |

Grouped bug recall avoids counting several synonyms for the same planted bug.
Discrimination: 11 models; top-4 within 0.12. huihui (13.69) dropped to #6 in
this subset — still strong but DeltaCoder/OmniCoder edge ahead.

## tool_call

| # | score | model |
|---|---|---|
| 1 | **10.36** | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |
| 2 | 10.34 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 10.34 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 2 | 10.34 | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` ← NEW |
| 2 | 10.34 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` ← NEW |

Still near-saturated: top-7 within 0.02. The bench needs multi-turn/retry cases
to discriminate. Openclaw's +0.02 edge is not significant enough to rewire.

## browser_tool

| # | score | model |
|---|---|---|
| 1 | **10.22** | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 10.20 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 10.20 | `free01/gemma4:e4b` |
| 4 | 10.20 | `batiai/gemma4-e4b:q4` |
| 5 | 10.20 | `cryptidbleh/gemma4-claude-sonnet-4.6:latest` |

Still near-saturated: 14 unique scores; max tie group 6. `functiongemma` remains
the best browser/tool dispatch model. Not re-run with new models (saturation
makes re-bench low-value).

## pdf_extract

| # | score | model |
|---|---|---|
| 1 | **12.05** | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |
| 2 | 11.96 | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| 2 | 11.96 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| 4 | 11.96 | `jaahas/crow:9b` |
| 5 | 11.95 | `aratan/gemma-4-E4B-it-heretic:Q6_K` |

Near-saturated: top-6 within 0.10. Openclaw edges out but not enough to rewire.

## pdf_ocr

| # | score | avg recall | model |
|---|---:|---:|---|
| 1 | **12.00** | **1.00** | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` |
| 2 | 11.15 | 1.00 | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| 3 | 11.12 | 1.00 | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` ← NEW (tested) |
| 4 | 11.11 | 1.00 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` ← NEW |
| 5 | 11.09 | 1.00 | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |

This is a separate rendered-PDF OCR category, not the same task as
`pdf_extract`. Unlimited OCR requires vision input via `/api/chat` and the
literal prompt `ocr [img]`; generic extraction prompts returned empty output in
live testing. lift works at ~112 tok/s vs Unlimited-OCR at ~573 tok/s.
General models (DeltaCoder, OmniCoder, crow, aratan) completely fail this task
(-100 score, 0 recall).

## embedding_retrieval

| # | MRR | recall@5 | model |
|---|---|---|---|
| 1 | **1.000** | **1.000** | `embeddinggemma:latest` |
| 2 | **1.000** | **1.000** | `bge-m3:latest` |
| 3 | 0.875 | 1.000 | `nomic-embed-text:latest` |

`embeddinggemma` and `bge-m3` tie on this 8-case retrieval set; keep
`embeddinggemma` as default for existing cache compatibility and `bge-m3` as
multilingual fallback.

## Runtime Handling

The benchmark no longer hard-drops models solely for recoverable reasoning
traces. Smoke records `strippable=1`; `deep` includes those models by default
and scores cleaned output. Current installed generative lineup was clean
(20/20); the policy remains important for future reasoning-distilled pulls.

Runtime clients updated in this pass:

- shared `~/.claude/scripts/ollama_client.py`
- `agent-memory/src/agent_memory/shared/ollama.py`
- `cheap-llm/cheap_llm.py`
- `cli-orchestration/browser/_subagent_call.py`

Model-specific runtime handling:

- Reasoning/tag leaks are stripped at clients before scoring/consumption when
  recoverable; models are not discarded solely for strippable CoT wrappers.
- Unlimited OCR is not a normal text completion model. Use `ocr [img]` with
  rendered PDF page images through `/api/chat`.
- `cheap-llm` keeps `qwen3.5:4b` for free-text compatibility and routes
  schema/JSON local T1 calls to functiongemma when no explicit model is passed.

## Per-task PRIMARY + FALLBACK

Updated 2026-07-08 with new model results. Where new models show clear
improvement (>0.3 score delta), PRIMARY is updated. Near-saturated tasks
(tool_call, browser_tool, pdf_extract) keep existing wiring.

| task | PRIMARY | FALLBACK |
|---|---|---|
| improve | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` ← NEW (+0.41 over old) | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |
| codeq_sum | `jaahas/crow:9b` (unchanged) | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` |
| smart_trim | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW (+0.28 over old) | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |
| web_synth | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` ← NEW (tied with aratan) | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| code_gen | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` (tied, keep) | `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` ← NEW |
| bug_finding | `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` ← NEW | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` |
| tool_call | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` (unchanged, saturated) | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| browser_tool | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` (unchanged, saturated) | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| pdf_extract | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` (unchanged, saturated) | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` (unchanged) | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` ← NEW fallback |
| embedding | `embeddinggemma:latest` | `bge-m3:latest` |

## Strippable models (2026-07-08)

Models that leak thinking but produce usable output after `strip_reasoning()`:
- `hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M` — strippable=1,
  but even stripped output ranks LAST in every deep task (-0.18 improve, 3.02
  codeq_sum, 5.73 smart_trim, 7.00 web_synth, 2.59 code_gen). Not recommended
  despite strippable status — the reasoning distillation degrades output quality
  even after stripping.

## New models tested (2026-07-08)

| Model | Size | Best task | Best rank | Notes |
|---|---|---|---|---|
| `hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M` | ~6 GB | smart_trim #1, code_gen #1, improve #3 | #1 | Strong generalist; new smart_trim/code_gen champion |
| `hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M` | ~6 GB | web_synth #1, bug_finding #1 | #1 | Strong coder; new web_synth/bug_finding champion |
| `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` | ~6 GB | improve #2, code_gen #5 | #2 | Solid; top-5 in most tasks |
| `hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M` | ~3 GB | codeq_sum #4, code_gen #4 | #4 | Compact; good for VRAM-tight |
| `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` | ~8 GB | improve #7, codeq_sum #6 | #6 | Gemma4 fine-tune; mid-pack |
| `hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M` | ~6 GB | — | last | Strippable but quality-degraded; not recommended |
| `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` | ~5 GB | pdf_ocr #3 | #3 | OCR specialist; fallback to Unlimited-OCR |
