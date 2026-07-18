# Local Ollama Model Lineup (RTX 5080, 16GB) — RE-BENCH 2026-07-08 (Ollama 0.31.1)

> **2026-07-18 agent note:** The models listed as winners / top-N in this package
> (and currently installed via `ollama list`) are **kept**. Do **not** recommend
> bulk prune for disk savings. Authority for current PRIMARY/FALLBACK is repo
> `RANKING.md` (round-17/18 supersede older tables in this file if they conflict).
> Host runtime mirror: `~/.config/dev/ollama-roles.json` + home `topics/local-ollama-lineup.md`.


> **Purpose:** Single source of truth for LOCAL Ollama winners + per-role map.
> Re-bench cycles: 2026-07-04 (16 winners) → round-3/5 → round-6 (strip mode) →
> **round-7 (2026-07-08 PM): full pipeline (smoke→deep→tie-break→specialized),
> combined ranking, lineup trimmed to top-5 union. 19 LLM + 3 embeddings = 22 models.**
>
> Round-7 rewired 7/9 PRIMARY winners + replaced qwen3.5:4b with cryptidbleh/gemma4-claude-opus-4.6
> (better on every metric); 13 models deleted (12 losers + qwen3.5:4b). See [deep-winners-20260708-pm](deep-winners-20260708-pm.md).
> think-strip mode. DeepSeek-V4-Flash is strippable but ranks last everywhere.
>
> **Round-9 (2026-07-12, Ollama 0.31.2):** tested 8 HF candidates (7 rejected pre-bench, gemma-4-oficial ollama-pull blocker).
> **`hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` DETHONED `batiai/gemma4-e4b:q4` in codeq_sum**
> (9.40 vs 9.19, +2.3% on 4-way deep). Qwythos also code_gen #2 fallback (10.38 vs lift 10.52, -1.3%).
> web_synth lost to xentriom Q8_0 (8.84 vs 10.19). Lineup grew 22 → 23 (Qwythos added; batiai held as fallback). See [candidates-round-9-2026-07-12](candidates-round-9-2026-07-12.md).
>
> **Round-10 (2026-07-12 PM, Ollama 0.31.2):** cross-task 4-way validation generalizes round-9 lesson.
> **THREE PRIMARY DETHRONES:** TeichAI/Fable-5-v1 in improve (2.46 vs OmniCoder 0.93); SC117/heretic-QAT
> in smart_trim (10.79 vs HauhauCS-Balanced 9.87); xentriom Q8_0 in bug_finding (14.97 vs OmniCoder 14.49).
> Plus pdf_extract #2 fallback swap: OmniCoder (12.00) > ykarout/Openclaw (11.97). Lineup 23 models unchanged
> (re-organized roles). Multi-task winners: TeichAI (improve + web_synth), xentriom Q8_0 (bug_finding + web_synth fallback).
> Demoted: OmniCoder (depth only), HauhauCS-Balanced (smart_trim fallback). See [candidates-round-10-2026-07-12](candidates-round-10-2026-07-12.md).
>
> **Round-11 (2026-07-12 PM):** cross-task 4-way validation with round-10 champions as challengers = **ZERO REWIRES**.
> All 4 rounds held: improve TeichAI, smart_trim SC117, tool_call SetneufPT, code_gen lift. Lineup at LOCAL OPTIMUM.
> See [candidates-round-11-2026-07-12](candidates-round-11-2026-07-12.md).
>
> **Round-12 (2026-07-12 PM, Ollama 0.31.2):** gemma-4 official family exploration = **ZERO REWIRES**.
> Tested gemma-4-26B-A4B MoE (loses code_gen 9.90 #4, 0.8 tps slow → DELETE) + gemma-4-12B-it-qat official
> (ties HauhauCS 9.87 within 0.05 noise, smart_trim 9.82 #3 → KEEP as depth). Lineup 23 → 24 (added 12B QAT, deleted 26B-A4B).
> **TERMINAL STABILITY:** all plausible architectures exhausted. Recommend TRIGGERED re-bench policy.
> See [candidates-round-12-2026-07-12](candidates-round-12-2026-07-12.md).
>
> **Round-13 (2026-07-12 PM, purge):** deleted Librellama/gemma4:e2b-Uncensored + unsloth/gemma-4-12B-it-qat-GGUF (neither in any task top-5). Lineup 24 → 22.
>
> **Round-14 (2026-07-12):** no new candidates tested.
>
> **Round-15 (2026-07-13, tiny classification empirical):** tested LFM, Qwen and Gemma3 tinys for classification role. All rejected; E2B GGUFs exceed resident-size gate.
>
> **Round-16 (2026-07-13, quality-first screen):** tested Qwythos v2, Qwen3 Embedding 4B, Granite 4.1 8B (improve). Granite rejected (isolated 3.00, fresh 3-way replication 2.33 vs TeichAI 2.46 and Negentropy 2.03).
>
> **Round-17 (2026-07-13, fresh 5-way re-bench):** **ONE PRIMARY DETHRONE** — `cryptidbleh/gemma4-claude-opus-4.6` dethroned `TeichAI/Qwen3.5-9B-Fable-5-v1` in improve (2.97 vs 2.46, +0.51). Round-10 blind spot: cryptidbleh was chain tail (legacy 2026-07-09 #1, smart_trim round-15 #2) but NOT in round-10 4-way, so its strength was never re-validated. TeichAI demoted to fallback. OmniCoder held lowest (0.93) — confirmed demoted to bug_finding/pdf_extract depth only. SetneufPT bench-validated at 1.68 (was untested in improve). Lineup unchanged. See [candidates-round-17-2026-07-13](candidates-round-17-2026-07-13.md).
>
> **Round-8 (2026-07-08 PM, same day):** tested 4 NEW HF candidates — `shuhulx/Qwopus3.5-4B-Coder-Fable5-v1`,
> `tvall43/Qwen3.6-14B-A3B-FableVibes` (MoE 3B-active), `llmfan46/...composer2.5-v2-heretic` (Q4), `KevinJK51/Qwen3.6-12B-Thinking-V2`.
> ALL 4 LOST vs round-7 champions → deleted. Lineup unchanged at 22. Key: MoE-latency thesis failed
> (14B mem-bandwidth → tps 6.9 vs 4B 10.7); composer2.5-v2 Q4 ties xentriom on bug_finding (15.01 vs 14.99)
> but loses web_synth (Q4 10.82 vs Q8 11.92) — xentriom Q8 stays. See RANKING_HISTORY.md §round-8.
> Re-pull ONLY: a CODER-tuned 14B-A3B MoE (not reasoning-distill), or a genuinely new base (not another
> Fable5/composer2.5 finetune of Qwen3.5-9B / Qwopus3.5-4B / gemma-4-12B).

## Per-task top-2 (wired into harness) — 2026-07-12 PM (round-10, cross-task 4-way validation)

| task | #1 (PRIMARY) | #2 (fallback) |
|---|---|---|
| improve | **`cryptidbleh/gemma4-claude-opus-4.6:latest`** ← round-17 NEW (2.97 fresh 5-way; dethroned TeichAI 2.46 — round-10 blind spot, cryptidbleh was chain tail never re-validated) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` (round-10 champion demoted to fallback, 2.46) |
| codeq_sum | **`hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M`** ← round-17 NEW (9.84 fresh 5-way; dethroned Qwythos 9.40 — cross-task blind spot, TeichAI was web_synth + improve champion but never tested against Qwythos in codeq_sum) | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` (round-9 champion demoted to fallback, 9.40) |
| smart_trim | **`hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL`** ← round-10 NEW (10.79; dethroned HauhauCS-Balanced 9.87) | `hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M` |
| web_synth | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` (held 10.20 4-way deep) | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` |
| code_gen | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` (held 10.52) | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` (10.38) |
| bug_finding | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`** ← round-17 NEW (15.35 fresh 5-way; dethroned xentriom 14.99 — round-10 blind spot, OmniCoder was demoted to depth after losing to xentriom but bug_finding head-to-head was never re-validated) | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` (round-10 champion demoted to fallback, 14.99; Q8_0 = 12GB VRAM, OmniCoder at 5.6GB is better low-memory choice) |
| tool_call | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` (held 10.10) | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| browser_tool | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M` |
| pdf_extract | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` (held 12.05) | **`zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`** ← round-10 NEW (12.00; was ykarout/Openclaw 11.97) |
| pdf_ocr | `hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M` (unchanged, 12.00) | `hf.co/prithivMLmods/lift-GGUF:Q4_K_M` |
| embedding | `embeddinggemma:latest` | `bge-m3:latest` |

## Key changes from 2026-07-08 PM re-bench (round-7)

0. **Round-9 (2026-07-12)**: **Qwythos** dethroned batiai in codeq_sum (+2.3%); batiai demoted to fallback. Qwythos also code_gen #2 (close). web_synth lost (Qwythos #4 vs xentriom Q8_0). Installed: 23 models.
1. **OmniCoder** — improve #1 (held) + bug_finding #1 (NEW). Multi-task champion.
2. **SetneufPT/Qwopus3.5** — tool_call + pdf_extract + browser_tool #1 (NEW). Structured-output champion.
3. **HauhauCS-Balanced** — smart_trim #1 (NEW, combined 12.30/13.53).
4. **TeichAI/Fable-5-v1** — web_synth combined #1 (NEW; tiebreak reshuffled past deep-only heretic).
5. **prithiv/lift** — code_gen #1 (NEW) + pdf_ocr fallback. Dual-role.
6. **DeltaCoder + Openclaw** (prior web_synth/bug_finding/smart_trim/code_gen #1) FELL OUT of top-5.
7. 7/9 PRIMARY changed; improve + pdf_ocr held. Lineup trimmed to top-5 union (losers deleted).
4. **Negentropy-4B** — compact 3GB model, top-5 in codeq_sum/code_gen. Good for VRAM-tight.
5. **lift** — OCR model, pdf_ocr #3 (11.12). Fallback to Unlimited-OCR.
6. **DeepSeek-V4-Flash** — strippable=1 but ranks LAST in every deep task. Not recommended.
7. **SetneufPT** — no longer improve #1; still codeq_sum #2, code_gen #5. Demoted from many PRIMARY roles.

## Strippable models

Models that leak thinking but produce usable output after `strip_reasoning()`:
- `hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M` — strippable but quality-degraded; last place everywhere.

Policy: `strippable=1` recorded at smoke; deep includes those models and scores cleaned output. Not discarded solely for recoverable CoT wrappers.

## Currently installed lineup (22 models — post round-13 purge 2026-07-12)

**Top-5 union across all 10 canonical + specialized tasks** (purge rule: models not in any task top-5 deleted).

```
# Canonical champions (round-10/11/12 best)
hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M          (codeq_sum #1 round-9, code_gen #2)
hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL               (smart_trim #1 round-10)
hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M                      (improve #1 + web_synth #1 round-10)
hf.co/prithivMLmods/lift-GGUF:Q4_K_M                                  (code_gen #1, pdf_ocr #2)
SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest               (tool_call + browser_tool + pdf_extract #1)
hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M                          (pdf_ocr #1 — vision OCR)
zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2:latest  (pdf_extract #2 round-10 swap, bug_finding depth)

# Top-5 depth (fallbacks / role fillers)
batiai/gemma4-e4b:q4                                                  (codeq_sum #2)
hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M    (smart_trim #2 fallback)
hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M             (improve #2)
hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M             (compact 3GB)
hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest        (bug_finding depth)
hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M        (tool_call #2)
hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M         (pdf_extract #3, was #2 pre-round-10)
xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0              (bug_finding #1 round-10, web_synth #2)
huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K                (code_gen #3)
jaahas/crow:9b                                                        (codeq_sum depth)
batiai/gemma4-e2b:q4                                                  (smart_trim depth)
batiai/gemma4-12b:q4                                                  (smart_trim #3 round-18 depth — Google DeepMind official Gemma 4 12B-it)

## Round-18 purge 2026-07-13 (top-5 union enforcement)

Per round-13 + round-18 top-5 union rule — deleted 4 models NOT in any task top-5:

| model | reason |
|-------|--------|
| `hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M` | model-inherent think-leak per `topics/ollama-0.23.2-gemma4-q4_0-incompat.md` line 26-30: "All 9 LFM variants deleted. Not candidates for any task." Re-emerged in ollama but kept the deletion. |
| `hf.co/RavichandranJ/Dolphin3-Cyber-8B-GGUF:Q4_K_M` | not in any task top-5; not referenced in RANKING; candidate no-show. |
| `hf.co/deepreinforce-ai/Ornith-1.0-9B-GGUF:Q4_K_M` | round-9 explicit skip (Qwen3.5-9B finetune, same-base finetunes lose vs round-7+ champions); never benched on any task. |
| `hf.co/lmstudio-community/gemma-4-E2B-it-GGUF:Q4_K_M` | lmstudio-community variant of gemma-4 E2B; batiai/gemma4-e2b is the lineup's E2B representative at higher quality (Q4 vs base). |

12GB disk freed (207GB used vs 219GB before; 4 deletion sizes 2-4GB each, larger ones already partly stored as blobs). Lineup 27 → 23 models.
cryptidbleh/gemma4-claude-opus-4.6:latest                             (universal fallback-of-fallbacks, web_synth depth)

# Embeddings
embeddinggemma:latest  bge-m3:latest  nomic-embed-text:latest
```

### Purged 2026-07-12 PM (round-13 cleanup)

| model | reason |
|---|---|
| `Librellama/gemma4:e2b-Uncensored` | not in any task top-5 (was depth-only multi-task mid); 3.4GB freed |
| `hf.co/unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL` | added round-12 as depth for gemma-4-12B official upstream; never entered top-5 in 4-way v3 (tied HauhauCS within noise, lost SC117); 6.9GB freed |
| `hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_M` | round-12 MoE exploration: lost code_gen (-0.62) + 0.8 tps partial GPU offload 10× latency; 13GB freed |

**Total freed**: 23.3GB. Lineup 24 → 22 models.

## Removed models (historical)

See `topics/candidates-round-5-2026-07-05.md` for full removal history (46 models removed 2026-07-04, 1 in round-3, 2 in cleanup).

## Bench methodology

See `topics/bench-methodology.md` for smoke → deep → tie-break → bug-finding pipeline.
