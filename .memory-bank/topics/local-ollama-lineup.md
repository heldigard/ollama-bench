# Local Ollama Model Lineup (RTX 5080, 16GB) — RE-BENCH 2026-07-05 round-5 (Ollama 0.31.1)

> **Purpose:** Single source of truth for LOCAL Ollama winners + per-role map.
> Three re-bench cycles to date: 2026-07-04 (16 winners) + 2026-07-05 round-3
> (Grug-12B improve upset) + 2026-07-05 round-5 (e4b collapse → SetneufPT/crow). 20 LLM winners + 3 embeddings = 23 models (84 GB).
>
> Round-5 details: `topics/candidates-round-5-2026-07-05.md`. Round-3: `topics/candidates-round-3-2026-07-05.md`.

## Final lineup — 20 LLM winners + 3 embeddings = 23 models (84 GB)

Combined-rank = avg(deep_rank, tie_break_rank). Top-5 per task with ties.

### Per-task top-2 (wired into harness)

| task | #1 (PRIMARY) | #2 (fallback) |
|---|---|---|
| improve | **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** ← rewired 2026-07-05 r3 (r5 confirmed: tb 8.35 >> field) | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` |
| codeq_sum | **`SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU`** ← rewired 2026-07-05 r5 (e4b collapsed tb 9.00) | `batiai/gemma4-e4b:q4` (demoted) |
| smart_trim | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` (saturated; maintained r5) | `fredrezones55/Qwopus3.5:9b` |
| web_synth | **`jaahas/crow:9b`** ← rewired 2026-07-05 r5 (e4b collapsed tb 5.50) | `batiai/gemma4-e2b:q4` |
| code_gen | `aratan/gemma-4-E4B-it-heretic:Q6_K` (saturated; maintained r5) | `fredrezones55/Qwopus3.5:9b` |
| bug_finding | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | `cryptidbleh/gemma4-claude-sonnet-4.6` |
| tool_call | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | `hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M` |

### All 20 LLM winners (lineup matches actual `ollama list`)

```
Librellama/gemma4:e2b-Uncensored                 (improve #3, codeq_sum #4, web_synth #4, smart_trim #3, code_gen #3)
SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU  (smart_trim #1, codeq_sum #2, bug_finding #3, web_synth #5)
aratan/gemma-4-E4B-it-heretic:Q6_K               (code_gen #3, smart_trim #3, bug_finding mid)
batiai/gemma4-12b:iq3                            (web_synth #2, smart_trim #7)
batiai/gemma4-e2b:q4                             (code_gen tied, smart_trim alt — Q4 only; Q6 deleted, see quant-comparison) ✅ re-installed 2026-07-05 round-4
batiai/gemma4-e4b:q4                             (was codeq_sum/web_synth #1 — DEMOTED r5: collapsed tb 9.00/5.50; now codeq_sum fallback)
cryptidbleh/gemma4-claude-opus-4.6               (codeq_sum #5, smart_trim #8, web_synth #6, code_gen #7, bug_finding mid)
cryptidbleh/gemma4-claude-sonnet-4.6             (bug_finding #2, codeq_sum #3, smart_trim #9, web_synth #7, code_gen #8)
fredrezones55/Qwopus3.5:9b                       (code_gen #1, smart_trim #2, codeq_sum #7, web_synth #8, improve mid)
free01/gemma4:e4b                                (codeq_sum #4, smart_trim #11, web_synth #3, code_gen #10)
hf.co/SC117/gemma-4-12B-it-heretic-QAT-UD-Q4_K_XL (smart_trim #4, bug_finding #4, improve mid)
hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl (improve #2 [was #1], bug_finding #7)
hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M ← NEW 2026-07-05 (code_gen #2 saturated, improve tier-3)
hf.co/kai-os/Grug-12B-GGUF:Q4_K_M                ← NEW 2026-07-05 (improve #1, bug_finding #5 tie, tool_call #2, code_gen saturated)
huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K (bug_finding #1, tool_call #1)
hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M (tool_call #2)
jaahas/crow:9b                                   (improve #4, codeq_sum #10, bug_finding #6)
qwen3.5:4b                                       (universal default, code_gen #3, smart_trim #14)
xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0 (bug_finding #5, deep-code historical)
zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2 (improve #4 deep, smart_trim #2, codeq_sum #8)
nomic-embed-text + embeddinggemma                (embeddings)
```

## Removed in this re-bench (46 models, 2026-07-04)

- **MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf** — was improve PRIMARY historically; now loads but ranks #23 improve / #37 codeq_sum. Outperformed by pegasus912.
- **9 LFM2.5-8B-A1B variants** — ALL leak thinking despite `think=False` on every Ollama version tested. Model-inherent, not Ollama. Re-pulling won't fix.
- **Huihui gemma4-12B abliterated** — was wired as improve fallback after Mobius "died"; now ranks outside top-5 everywhere.
- **VladimirGav/Qwen3.6-27B** (15 GB) — slow + leaky.
- **12 mradermacher gemma4-12B variants** — duplicates of base gemma4-12B; one winner kept (via pegasus912/SC117 which are different quants).
- **xentriom composer latest (Q4_K_M)** — Q8_0 kept (bug-finding #5); Q4 lost.
- Other gemma4-12B/qwen3.6 non-winners.

## Removed in round-3 (1 model, 2026-07-05)

- **hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M** — pulled expecting DeepSeek-V4-distilled tool_call upset. Failed smoke: leaks `thinking_process` despite `think=False` (reasoning-distilled Qwen3.5-9B pattern; same as `kwangsuklee`). 6.6 GB freed.

## Cleanup 2026-07-05 — top-5 hygiene (post-round-3)

User asked: clean models NOT in top-5 of any task. Audit of installed (24) vs lineup (20 winners + 3 embed) found 2 extras + 1 missing winner.

**Deleted (13 GB freed):**
- `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` (7.4 GB) — was DROPPED in round-2 (new-models-bench-2026-07-04.md::DECISIONS::DROP) but never `ollama rm`'d. yuxinlu1's other model (the non-tau2 base) is **already** absent from the lineup. Pure leftover.
- `kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest` (5.6 GB) — leaks `thinking_process` despite `think=False`; not in any task's top-5. Was kept only as `--strip` demonstrator from round-2. Stale.

**Missing winner (NOT deleted; documented for re-pull):**
- `batiai/gemma4-e2b:q4` ✅ re-installed 2026-07-05 round-4.

**Header count fix:** prior version said "17 LLM winners + 2 embeddings = 19 models (84 GB)" but the file actually lists 20 LLMs + 3 embed = 23. Header was off by 3 from a typo carried since round-3 (when 2 winners were added but the header wasn't incremented for the round-2 winners huihui + slyfox). Fixed.

## Bench methodology (smoke → deep → tie-break → bug-finding)

1. **smoke** (1 prompt × N models) — leak gate; 64 → 47 OK + 8 LFM leaks + 9 errors
2. **deep** (5 tasks × 47 candidates) — first-pass score (saturates 7.0)
3. **tie-break** (5 hard prompts × 24 saturated winners) — structural scoring (no cap)
4. **combined-rank** = avg(deep_rank, tie_break_rank) → top-5 per task
5. **bug-finding** (2 diff-with-bugs × 15 candidates) — recall scoring; composer Q8 kept

See `topics/bench-methodology.md` for the full pipeline rationale.