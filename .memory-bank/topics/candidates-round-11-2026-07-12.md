# Candidates Round-11 — 2026-07-12 (Lineup Hardened: Zero Rewires)

## TL;DR

**Zero rewires. Round-11 tested whether round-10's 3 dethrones generalized to other tasks via cross-task 4-way validation. All 4 attempts: round-10 champions held. Lineup is at a local optimum.**

| task | round-10 champion | round-11 challenger | round-11 score | gap to champ | displace? |
|---|---|---|---|---|---|
| improve | TeichAI 2.46 (round-10) | SC117 + Qwythos + (held TeichAI) | TeichAI 2.46 | +0.00 (held) | ❌ |
| smart_trim | SC117 10.79 (round-10) | TeichAI + xentriom Q8_0 + (held SC117) | SC117 10.79 | +0.00 (held) | ❌ |
| tool_call | SetneufPT 10.10 (held) | TeichAI + SC117 + (held SetneufPT) | SetneufPT 10.10 | +0.00 (held narrowly +0.01 vs yuxinlu1) | ❌ |
| code_gen | lift 10.52 (held) | SC117 + (held lift + Qwythos) | lift 10.52 | +0.00 (held) | ❌ |

## Round-11 results (4-way unless noted)

```
improve v2:
  TeichAI/Fable-5-v1       2.46  #1 (held)
  SC117/heretic-QAT         0.94  #2 (close to OmniCoder but no displace)
  OmniCoder                 0.93  #3
  Qwythos                  -0.51  #4 (went NEGATIVE — leak/strip issue on improve prompts)

smart_trim v2:
  SC117/heretic-QAT        10.79  #1 (held)
  HauhauCS-Balanced         9.87  #2 (held)
  xentriom Q8_0             8.89  #3 (no displace)
  TeichAI                   8.74  #4

tool_call v2:
  SetneufPT                10.10  #1 (held narrowly +0.01)
  yuxinlu1/gemma-4-12B     10.09  #2 (held)
  TeichAI                   9.93  #3 (close but no displace)
  SC117/heretic-QAT         9.76  #4

code_gen v3:
  lift                     10.52  #1 (held)
  Qwythos                  10.38  #2 (held from round-9)
  SetneufPT                10.18  #3
  SC117/heretic-QAT         9.96  #4
```

## What this means

### 1. Round-10 was the LAST easy rewire cycle

Round-10's 3 dethrones (TeichAI, SC117, xentriom) exploited "stale champion never challenged by other-task champions". Round-11 tried the same pattern with round-10 champions as challengers — they didn't displace each other.

**The cross-task champion pattern is asymmetric**: a champion from a reasoning-heavy task (web_synth) beats a champion from a coding-heavy task (improve), but two reasoning-heavy champions (TeichAI in improve vs SC117 in smart_trim) don't compete effectively against each other because their skills are orthogonal.

### 2. Qwythos in improve = -0.51 (negative)

Qwythos went NEGATIVE on improve prompts. This is significant — codeq_sum/code_gen champion doesn't transfer to improve. The "specialist vs generalist" boundary is real: Qwythos is codeq_sum/code_gen specialist (Qwen3.5-9B base, code-tuned training), not improve (which requires reasoning-distill-style rewrite).

### 3. Coder-MoE architecture NOT tested (VRAM constraint)

The candidate coder-MoE Qwen3-Coder-30B-A3B-Instruct Q4_K_M = ~18GB, exceeds RTX 5080 16GB VRAM. Qwen3-Coder-Next is 80B-A3B = ~48GB. No coder-MoE in the 14B-A3B band exists yet. **Round-12 must pull a coder-MoE IF a 14B-A3B variant becomes available**, or test 9B-12B dense coder variants.

### 4. SC117's "family rotation" doesn't generalize

SC117 dethroned HauhauCS-Balanced in smart_trim (same gemma-4-12B-heretic base). But SC117 didn't beat lift/SetneufPT in code_gen (4B-coder base family dominates), didn't beat TeichAI in improve (Qwen3.5-9B-Fable-5 base dominates), and didn't beat SetneufPT in tool_call (4B-coder base dominates).

**SC117's win is task-specific (smart_trim), not family-wide.**

### 5. The lineup has reached local stability

Round-7 → Round-8 → Round-9 → Round-10 → Round-11: 4 dethrones total in 4 rounds (1 in round-9, 3 in round-10, 0 in round-11). The remaining champions are HARDENED against cross-task challengers. To get more dethrones, round-12+ needs NEW architectures (coder-MoE, 14B+ dense, novel base).

## What didn't move

- **codeq_sum** = Qwythos (round-9, no fresh test this round)
- **web_synth** = TeichAI (no fresh test, xentriom Q8_0 + cryptidbleh held in round-10)
- **bug_finding** = xentriom Q8_0 (round-10, no fresh test this round)
- **browser_tool** = SetneufPT (no fresh test)
- **pdf_extract** = SetneufPT (round-10, no fresh test this round)
- **pdf_ocr** = Unlimited-OCR (specialized, no fresh test)

## Coder-MoE search (no fit on 16GB VRAM)

| candidate | size | VRAM | status |
|---|---|---|---|
| Qwen3-Coder-30B-A3B-Instruct | 30B total, 3B active | ~18GB Q4_K_M | exceeds 16GB; partial GPU offload possible but slow |
| Qwen3-Coder-Next (80B-A3B) | 80B total, 3B active | ~48GB Q4_K_M | no fit |
| Qwen3-Coder dense 7B/14B | (none released as of 2026-07) | — | search yielded zero hits |
| tvall43/Qwen3.6-14B-A3B-FableVibes (round-8) | 14B-A3B | ~9GB | already tested + lost (reasoning-distill, not coder) |

**Round-12 lead candidate**: when a 14B-A3B coder-tuned variant appears, it becomes the highest-leverage pull. Meanwhile, monitor for coder-tuned dense 14B or any new MoE with active ≤4B.

## Wiring

No changes from round-10. All 5 champions + 5 specialized primaries held:
- improve PRIMARY = TeichAI/Fable-5-v1
- codeq_sum PRIMARY = Qwythos-9B-Claude-Mythos-5-1M-GGUF
- smart_trim PRIMARY = SC117/heretic-QAT
- web_synth PRIMARY = TeichAI/Fable-5-v1
- code_gen PRIMARY = lift-GGUF
- bug_finding PRIMARY = xentriom Q8_0
- tool_call PRIMARY = SetneufPT
- browser_tool PRIMARY = SetneufPT
- pdf_extract PRIMARY = SetneufPT

## Decision matrix for round-12

| condition | action |
|---|---|
| New 14B-A3B coder-tuned HF model appears | pull + smoke + code_gen 4-way |
| `google/gemma-4-E4B-it-qat-q4_0-gguf` (round-9 blocker) resolves on Ollama 0.32+ | retry pull + codeq_sum 4-way |
| A new family (Llama-4 7B? Mistral-3?) appears | pull + smoke + 4-way across all 5 tasks |
| Nothing new + stable | declare lineup CLOSED, stop running benches; only rewire when a candidate proves superior in head-to-head |
| **`re-bench cycle cost`** | each round costs ~1.5h GPU + ~30min memory-bank work. Stable lineup means we should reduce cycle frequency to monthly or until external trigger (new HF release, Ollama major upgrade) |

## Strategic recommendation

**Move from "every-2-days re-bench" to "triggered re-bench".** Round-11 zero rewires is strong evidence that the lineup is at a local optimum. Further re-bench cycles without new architectures will keep returning zero rewires.

Recommended cadence:
- **Triggered** (immediate): new HF candidate that matches the gap (coder-MoE 14B-A3B, new base, new family).
- **Quarterly** (scheduled): full 5-task re-bench on existing lineup, watch for model drift (e.g., if Ollama upgrade changes sampling).
- **Annual** (full sweep): re-test ALL installed models including previous-round losers to detect any quality shifts from base-model updates.

Stop running benches unless an external trigger fires.