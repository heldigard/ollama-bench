# Local Ollama Model Lineup (RTX 5080, 16GB) — RE-BENCH 2026-07-04 (Ollama 0.31.1)

> **Purpose:** Single source of truth for LOCAL Ollama winners + per-role map.
> Re-bench ran after unifying the dual Ollama servers (Windows+WSL) into a single
> WSL Ollama 0.31.1 (was 0.23.2 — that old version falsely marked Mobius/SetneufPT
> as DEAD; they load fine now).

## Final lineup — 16 LLM winners + 2 embeddings = 18 models (76 GB)

Combined-rank = avg(deep_rank, tie_break_rank). Top-5 per task with ties.

### Per-task top-2 (wired into harness)

| task | #1 (PRIMARY) | #2 (fallback) |
|---|---|---|
| improve | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl` | `Librellama/gemma4:e2b-Uncensored` |
| codeq_sum | `batiai/gemma4-e4b:q4` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` |
| smart_trim | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` | `fredrezones55/Qwopus3.5:9b` |
| web_synth | `batiai/gemma4-e4b:q4` | `batiai/gemma4-12b:iq3` |
| code_gen | `fredrezones55/Qwopus3.5:9b` | `aratan/gemma-4-E4B-it-heretic:Q6_K` |
| bug_finding | `cryptidbleh/gemma4-claude-sonnet-4.6` | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` |

### All 16 LLM winners kept installed

```
Librellama/gemma4:e2b-Uncensored                 (improve #2, codeq_sum #4, web_synth #4, smart_trim #3, code_gen #3)
SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU  (smart_trim #1, codeq_sum #2, bug_finding #2, web_synth #5)
aratan/gemma-4-E4B-it-heretic:Q6_K               (code_gen #2, smart_trim #3, bug_finding mid)
batiai/gemma4-12b:iq3                            (web_synth #2, smart_trim #7)
batiai/gemma4-e2b:q4                             (code_gen tied, smart_trim alt — Q4 only; Q6 deleted, see quant-comparison)
batiai/gemma4-e4b:q4                             (codeq_sum #1, web_synth #1, bug_finding mid)
cryptidbleh/gemma4-claude-opus-4.6               (codeq_sum #5, smart_trim #8, web_synth #6, code_gen #7, bug_finding mid)
cryptidbleh/gemma4-claude-sonnet-4.6             (bug_finding #1, codeq_sum #3, smart_trim #9, web_synth #7, code_gen #8)
fredrezones55/Qwopus3.5:9b                       (code_gen #1, smart_trim #2, codeq_sum #7, web_synth #8, improve mid)
free01/gemma4:e4b                                (codeq_sum #4, smart_trim #11, web_synth #3, code_gen #10)
hf.co/SC117/gemma-4-12B-it-heretic-QAT-UD-Q4_K_XL (smart_trim #4, bug_finding #3, improve mid)
hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl (improve #1, bug_finding #8)
jaahas/crow:9b                                   (improve #4, codeq_sum #10, bug_finding #6)
qwen3.5:4b                                       (universal default, code_gen #3, smart_trim #14)
xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0 (bug_finding #5, deep-code historical)
zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2 (improve #3 deep, smart_trim #2, codeq_sum #8)
nomic-embed-text + embeddinggemma                (embeddings)
```

## Removed in this re-bench (46 models)

- **MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf** — was improve PRIMARY historically; now loads but ranks #23 improve / #37 codeq_sum. Outperformed by pegasus912.
- **9 LFM2.5-8B-A1B variants** — ALL leak thinking despite `think=False` on every Ollama version tested. Model-inherent, not Ollama. Re-pulling won't fix.
- **Huihui gemma4-12B abliterated** — was wired as improve fallback after Mobius "died"; now ranks outside top-5 everywhere.
- **VladimirGav/Qwen3.6-27B** (15 GB) — slow + leaky.
- **12 mradermacher gemma4-12B variants** — duplicates of base gemma4-12B; one winner kept (via pegasus912/SC117 which are different quants).
- **xentriom composer latest (Q4_K_M)** — Q8_0 kept (bug-finding #5); Q4 lost.
- Other gemma4-12B/qwen3.6 non-winners.

## Bench methodology (smoke → deep → tie-break → bug-finding)

1. **smoke** (1 prompt × N models) — leak gate; 64 → 47 OK + 8 LFM leaks + 9 errors
2. **deep** (5 tasks × 47 candidates) — first-pass score (saturates 7.0)
3. **tie-break** (5 hard prompts × 24 saturated winners) — structural scoring (no cap)
4. **combined-rank** = avg(deep_rank, tie_break_rank) → top-5 per task
5. **bug-finding** (2 diff-with-bugs × 15 candidates) — recall scoring; composer Q8 kept

See `topics/bench-methodology.md` for the full pipeline rationale.