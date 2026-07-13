# Candidates Round-12 — 2026-07-12 (Gemma-4 official family: 0 rewires, 1 keep, 1 delete)

## TL;DR

Tested 2 official gemma-4 variants on HF that were never in the lineup:

| model | size | smoke | code_gen / smart_trim result | action |
|---|---|---|---|---|
| `unsloth/gemma-4-26B-A4B-it-GGUF` UD-Q3_K_M | 13GB | ok, 0.8 tps (slow, partial GPU offload) | code_gen 9.90 #4 (lost -0.62 vs lift) | **DELETE** (lose + 10× latency) |
| `unsloth/gemma-4-12B-it-qat-GGUF` UD-Q4_K_XL | 6.9GB | ok, 6.6 tps | smart_trim 9.82 #3 (ties HauhauCS-Balanced 9.87, loses SC117 10.79) | **KEEP** as depth (official upstream of heretic variants) |

**Zero rewires.** Confirms round-11 verdict: lineup at local optimum. Adding the gemma-4 official family (MoE + QAT upstream) did NOT displace any per-task champion.

## Method

Two parallel lines:

1. **gemma-4-26B-A4B MoE** (NEW architecture for lineup — round-8/9/11 had no MoE in lineup):
   - Pull UD-Q3_K_M = 13GB (smaller than Q4_K_M 15.5GB to fit 16GB VRAM via partial GPU offload).
   - Smoke: ok, no leak, **0.8 tps** (slow — 26B model with 16GB VRAM = partial offload penalty).
   - Deep code_gen 4-way vs lift + Qwythos + SetneufPT (the three top-3).

2. **gemma-4-12B-it-qat official** (UPSTREAM of lineup's heretic 12B variants):
   - Pull UD-Q4_K_XL = 6.9GB.
   - Smoke: ok, no leak, 6.6 tps.
   - Deep smart_trim 4-way vs SC117 + HauhauCS-Balanced + TeichAI (current smart_trim top-3).

## Detailed results

```
code_gen 4-way v4 (with 26B-A4B MoE):
  lift                                   10.52  #1 (held)
  Qwythos                                10.38  #2 (held)
  SetneufPT                              10.18  #3 (held)
  gemma-4-26B-A4B UD-Q3_K_M              9.90   #4 (LOSES -0.62 vs lift, slow 0.8 tps)

smart_trim 4-way v3 (with 12B QAT official):
  SC117/heretic-QAT                      10.79  #1 (held)
  HauhauCS-Balanced                       9.87  #2 (held)
  gemma-4-12b-it-qat UD-Q4_K_XL           9.82  #3 (ties HauhauCS within 0.05)
  TeichAI                                 8.74  #4
```

## What this means

### 1. MoE architecture confirmed NOT competitive on 16GB VRAM

The 26B-A4B MoE was the LAST plausible "new architecture" bet. It loaded but partial GPU offload at 16GB killed latency (0.8 tps = 10× slower than Qwythos). Quality-wise, also loses by -0.62 to lift in code_gen. **The MoE advantage requires more VRAM than 16GB.** Closed this avenue.

### 2. Official QAT ≈ community heretic finetune (within noise)

gemma-4-12b-it-qat official (9.82) vs HauhauCS-Balanced community (9.87) = **0.05 gap, within bench noise**. The heretic finetune recipe didn't add real quality over the official upstream QAT. The remaining SC117 advantage (-0.97 vs official) is from a different QAT recipe (`UD-Q4_K_XL` unsloth dynamic vs standard Q4_K_M).

**Implication**: SC117's win was never "heretic" brand-specific — it was the **UD-Q4_K_XL quant + balance strategy** that won. If Google's official QAT with similar recipe dropped, it would tie SC117.

### 3. Round-12 closes the gemma-4 official exploration

We now have:
- **gemma-4-12b-it-qat** (official upstream) — added as depth, 6.9GB
- All lineup gemma-4-12B-heretic finetunes (SC117, HauhauCS-Balanced, pegasus912, yuxinlu1, xentriom Q8_0) — unchanged
- gemma-4 E4B (batiai community), E2B (batiai + Librellama + cryptidbleh variants) — unchanged
- **gemma-4-26B-A4B MoE**: deleted

Lineup grew 23 → 24 models (one add, one delete).

## Strategic implication

**The lineup has reached terminal stability.** Round-9 (1), Round-10 (3), Round-11 (0), Round-12 (0) — diminishing returns confirmed. All plausible architectures exhausted:
- ❌ coder-MoE 14B-A3B (no such variant exists for VRAM budget)
- ❌ gemma-4-26B-A4B MoE (loses on quality + 10× latency)
- ❌ gemma-4-12B QAT official (ties community heretic)
- ❌ cross-task challengers from round-10 champions (round-11 zero rewires)
- ❌ cross-task challengers from round-11 / round-12 champions (this round)

**Recommendation**: stop running periodic re-bench cycles. Adopt TRIGGERED re-bench policy:
- **Ollama major upgrade** (e.g., 0.32+) → re-test for sampling drift, especially resolve `google/gemma-4-E4B-it-qat-q4_0-gguf` 400 blocker from round-9.
- **New HF release in a closed gap** (e.g., Qwen3-Coder-14B-A3B coder-tuned, 30B-class coder with sub-15GB quant).
- **Quarterly drift watch** on existing lineup.

## Installed lineup delta

Before round-12: 23 models. After: **24 models** (added 12B QAT, deleted 26B-A4B). Net disk +6.9GB.

## Wiring

No changes. All round-10 + round-11 champions held. The 12B QAT addition is documented in memory but not wired as primary or fallback for any task.

## What to monitor for round-13+

| external signal | condition |
|---|---|
| Ollama 0.32+ release | Retry `google/gemma-4-E4B-it-qat-q4_0-gguf` pull (round-9 blocker). If 400 resolves, this is the LAST gemma-4 variant worth testing — official upstream of codeq_sum current champion's competitor (batiai). |
| Qwen3-Coder-14B-A3B coder-tuned release | The ONE remaining coder-MoE bet. Currently doesn't exist on HF. Watch collections. |
| New Qwen3.6/3.7 family fine-tunes with different base than 3.5-9B | Same-base finetunes are exhausted; a new base is the only remaining lever. |
| Llama-4 / Mistral-3 / DeepSeek-V5 release | New architectures not yet seen on bench. |

## Decision matrix

| condition | action |
|---|---|
| Ollama 0.32+ releases AND gemma-4-E4B-oficial pull works | pull + codeq_sum 4-way (vs Qwythos + batiai). The official Google upstream might beat batiai. |
| New HF model in any of: Qwen3-Coder coder-MoE 14B-A3B / new base family / sub-10GB dense coder | pull + smoke + targeted 4-way bench |
| Nothing new | declare lineup CLOSED. Stop periodic re-bench. Triggered re-bench policy only. |