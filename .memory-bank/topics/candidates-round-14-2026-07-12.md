# Candidates Round-14 — 2026-07-12 (Llama-4 blocked, Codestral loses)

## TL;DR

Two new-family attempts to break the lineup terminal stability:

| model | size | smoke | code_gen | action |
|---|---|---|---|---|
| `unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF` Q3_K_S | 48GB | ok, **0.5 tps** (partial GPU offload) | NOT benched (tps veto) | **DELETE** |
| `bartowski/Codestral-22B-v0.1-GGUF` Q4_K_M | 13GB | ok, 1.8 tps | 8.67 #4 (-1.85 vs lift) | **DELETE** |

**Zero rewires.** Both new families fail to displace on 16GB VRAM.

## Method

After 4 rounds (9-12) of cross-task validation that confirmed lineup terminal stability, attempted to introduce two genuinely NEW families:

1. **Llama-4-Scout-17B-16E-Instruct** (Meta, 109B MoE / 17B active) — first Llama-4 in lineup. New inductive bias.
2. **Codestral-22B** (Mistral, dense 22B) — first Mistral in lineup. Coder-tuned base.

## Llama-4-Scout attempt

- Pulled `hf.co/unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_M` → **400 sharded GGUF error** (Ollama issue #5245).
- Pivoted to `Q3_K_S` (smaller, single file) → 48GB on disk.
- **Smoke**: ok, no leak, **0.5 tps** (87s for 45 etoks).
- Decision: **DELETE without bench.** Same pattern as round-12 gemma-4-26B-A4B (0.8 tps): partial GPU offload at 16GB VRAM = 12-24× slower than current champions (lift/SetneufPT 10-15 tps). Even if quality wins, latency makes it production-unusable.
- 48GB disk freed.

## Codestral-22B attempt

- Pulled `hf.co/bartowski/Codestral-22B-v0.1-GGUF:Q4_K_M` → 13GB. Fits 16GB VRAM.
- **Smoke**: ok, no leak, 1.8 tps. Output: clean Python list vs tuple answer.
- **code_gen 4-way**:

```
code_gen:
  lift                                 10.52  #1 (held)
  Qwythos                              10.38  #2 (held)
  SetneufPT                            10.18  #3 (held)
  Codestral-22B                         8.67  #4 (LOSES -1.85 vs lift)
```

- Decision: **DELETE.** -1.85 vs lift is the biggest gap of any challenger this session. The lineup's code_gen champion set is hardened against new families too.
- 13GB disk freed.

## Strategic implications

### 1. The lineup is at deeper-than-expected terminal stability

Round-13 already confirmed "all plausible architectures exhausted":
- ❌ coder-MoE 14B-A3B (no such variant on HF)
- ❌ gemma-4-26B-A4B MoE (loses on quality + 10× latency)
- ❌ gemma-4-12B QAT official (ties within noise)
- ❌ cross-task challengers (rounds 11/12 zero rewires)

Round-14 confirms the next axis (NEW FAMILIES) is also exhausted:
- ❌ Llama-4 (latency veto from partial GPU offload at 16GB)
- ❌ Mistral Codestral-22B (quality gap -1.85 in code_gen + 1.8 tps)

The lineup has proven robust across:
- 4 rounds of cross-task 4-way validation (rounds 10/11/12/13/14)
- 2 new-family attempts (Llama-4, Mistral)
- All plausible architectures (MoE, QAT, dense, reasoning-distill, coder-tuned)

### 2. The 16GB VRAM constraint is the binding limit

Models requiring partial GPU offload (Llama-4-Scout, gemma-4-26B-A4B) are immediately vetoed regardless of quality. Models that fit 16GB (Codestral-22B at 13GB) still lose to Qwen/gemma finetunes. The lineup's 5-8GB size band (Q4_K_M models) is the sweet spot for 16GB VRAM.

### 3. Strategic recommendation escalates

**Stop ALL test-the-limits work.** The next re-bench only triggers if:
- Ollama major upgrade enables larger model residency on 16GB (unlikely without hardware change)
- A genuinely new FAMILY appears at the 5-8GB sweet spot (Qwen3.6-9B-Inst? Llama-3.3-8B? Mistral-7B-v3?)
- Quarterly drift watch on existing lineup

If none of those fire in 6 months, lineup is "frozen at 22 models" indefinitely. Adopting this is fine — the lineup serves its purpose (per-task quality + latency).

## Installed lineup delta

Before round-14: 22 models (post round-13 purge).
Round-14: 0 changes. Both Llama-4 + Codestral deleted, no additions.
After: 22 models unchanged.

## Wiring

No changes. All round-10/11/12/13 champions held across all 6 rounds.

## Decision matrix for round-15+

| condition | action |
|---|---|
| 5-8GB sweet-spot candidate from new family | pull + targeted 4-way |
| Ollama 0.32+ resolves the gemma-4-E4B-oficial 400 blocker | retry + codeq_sum 4-way |
| Nothing new in 6 months | declare lineup FROZEN, retire cross-task validation cadence entirely |
| Existing model from lineup shows quality drift (e.g., upstream update) | targeted re-bench on that model only |

## Cumulative purge history this session (rounds 12-14)

| model | reason |
|---|---|
| `gemma-4-26B-A4B MoE` (round-12) | loses code_gen + 0.8 tps latency |
| `Librellama/gemma4:e2b-Uncensored` (round-13) | not in any top-5 |
| `gemma-4-12B QAT official` (round-13) | not in any top-5 |
| `Llama-4-Scout-17B-16E Q3_K_S` (round-14) | 0.5 tps partial offload |
| `Codestral-22B Q4_K_M` (round-14) | loses code_gen -1.85 + 1.8 tps |

**Total disk freed**: 13 + 3.4 + 6.9 + 48 + 13 = **84.3 GB**.
**Net model adds kept**: 1 (Qwythos round-9).
**Net model deletes**: 5 (above).
**Lineup evolution**: 23 → 22 over 5 rounds (post-purge).