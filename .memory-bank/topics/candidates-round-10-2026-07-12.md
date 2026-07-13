# Candidates Round-10 — 2026-07-12 (Cross-Task Champions Dethrone Specialists)

## TL;DR — **MAJOR REWIRE: 3 PRIMARY CHANGES**

The learning from round-9 (tie-break vs OmniCoder was misleading on web_synth because OmniCoder is NOT the champion there) generalized: **stale champions across ALL tasks were vulnerable to cross-task challengers** that had never been tested against them.

| task | OLD champion (round-7/8/9) | NEW champion (round-10) | delta | challenger source |
|---|---|---|---|---|
| **improve** | OmniCoder (round-7) | **TeichAI/Fable-5-v1** | +1.53 (2.46 vs 0.93) | web_synth #1 |
| **smart_trim** | HauhauCS-Balanced (round-7) | **SC117/heretic-QAT** | +0.92 (10.79 vs 9.87) | smart_trim #2 fallback |
| **bug_finding** | OmniCoder (round-7) | **xentriom Q8_0** | +0.48 (14.97 vs 14.49) | web_synth #2 (cross-task) |
| tool_call | SetneufPT | SetneufPT (held) | +0.03 | — |
| pdf_extract | SetneufPT | SetneufPT (held) | +0.05 | OmniCoder promoted to #2 fallback |
| codeq_sum | Qwythos | Qwythos (held, round-9) | +0.22 | Librellama tested, no displace |
| web_synth | TeichAI | TeichAI (held) | +0.12 | HauhauCS tested, #4 |
| code_gen | lift | lift (held) | +0.14 | TeichAI tested, #4 |

## Method — Cross-Task 4-Way Validation

For each canonical task, run a 4-way deep bench with the **current champion + its top-3 fallback + cross-task challengers**. The hypothesis: a champion from another task might be a latent winner in this task.

Total: 8 runs × 4 models × ~3min = ~1.5h GPU. Plus 1 additional bug_finding 5-way after TeichAI proved itself in improve.

## Per-task results (4-way unless noted)

```
bug_finding (5-way, with TeichAI added after improve upset):
  xentriom Q8_0           14.97  #1 NEW (cross-task: web_synth #2)
  pegasus912/heretic       14.70  #2 NEW (was bug_finding depth)
  SC117/heretic-QAT        14.68  #3
  OmniCoder                14.49  #4 (was #1 champion)
  TeichAI                  14.06  #5 (no displace)

tool_call:
  SetneufPT                10.10  #1 (held)
  yuxinlu1/gemma-4-12B     10.07  #2 (held)
  HauhauCS-Balanced         9.78  #3
  OmniCoder                 9.48  #4

pdf_extract:
  SetneufPT                12.05  #1 (held)
  OmniCoder                12.00  #2 (UP from #4 — promoted to fallback)
  ykarout/Openclaw         11.97  #3 (down from #2 fallback)
  HauhauCS-Balanced        11.80  #4

improve (cross-task challengers):
  TeichAI/Fable-5-v1        2.46  #1 NEW (web_synth champ)
  Negentropy-9B             2.03  #2 (held as fallback)
  HauhauCS-Balanced         1.50  #3
  OmniCoder                 0.93  #4 (was #1 champion)

codeq_sum v2 (with Librellama):
  Qwythos                   9.40  #1 (held from round-9)
  batiai/e4b:q4             9.18  #2
  SetneufPT                 8.99  #3
  Librellama/gemma4-e2b     8.73  #4 (no displace)

smart_trim (cross-task challengers):
  SC117/heretic-QAT        10.79  #1 NEW (was #2 fallback; gemma-4-12B-heretic rotation)
  HauhauCS-Balanced         9.87  #2 (was #1 champion; same family as SC117)
  TeichAI                   8.74  #3
  OmniCoder                 7.23  #4

web_synth v2 (with HauhauCS added):
  xentriom Q8_0            10.20  #1 (held)
  cryptidbleh              10.08  #2
  TeichAI                   9.92  #3 (was #1 round-7 combined; demoted)
  HauhauCS-Balanced         9.83  #4

code_gen v2 (with TeichAI added):
  lift                     10.52  #1 (held)
  Qwythos                  10.38  #2 (held from round-9)
  SetneufPT                10.18  #3
  TeichAI                  10.05  #4 (no displace)
```

## Key insights

### 1. The "round-7 stale champion" pattern

Round-7's combined-rank #1 was never re-tested against champions from OTHER tasks. This created an assumption bias:

- **improve** assumed coder-tuned models win; web_synth-style reasoning-distill actually wins.
- **smart_trim** assumed HauhauCS-Balanced was the best heretic-12B; SC117 sibling was actually stronger.
- **bug_finding** assumed OmniCoder (coder-tuned) was the recall champion; xentriom (web_synth/web-research base) was stronger.

### 2. Web_synth champion is multi-task

TeichAI/Qwen3.5-9B-Fable-5-v1 won:
- web_synth combined #1 (round-7)
- improve #1 NEW (round-10)

xentriom Q8_0 won:
- web_synth combined #2 (round-7), #1 in 4-way deep (round-9)
- bug_finding #1 NEW (round-10)

These two are the "broad generalists" of the lineup. Their reasoning-distill/agentic training transfers across tasks.

### 3. Coder-tuned models are narrower than expected

OmniCoder (coder-tuned) won improve + bug_finding in round-7, but loses both when challenged by reasoning-distill champions. It held:
- tool_call #4 (still competitive; SetneufPT holds #1)
- pdf_extract #2 NEW (12.00, gap 0.05 to SetneufPT)

So OmniCoder is now a STRUCTURED-OUTPUT specialist (json tool-call, schema pdf-extract), not a "coder" generalist.

### 4. SC117 vs HauhauCS: same base, different QAT

Both are gemma-4-12B-heretic family. SC117 (UD-Q4_K_XL) beats HauhauCS-Balanced (Q4_K_M) in smart_trim by +0.92. The "balanced" suffix on HauhauCS doesn't beat SC117's QAT recipe. **Implication**: for the same base, the right QAT recipe matters more than the brand prefix.

## Wiring updates applied (round-10)

- `src/ollama_bench/shared/config.py` — 3 PRIMARY changes (improve, smart_trim, bug_finding) + 1 FALLBACK swap (pdf_extract ykarout→OmniCoder)
- `RANKING.md` — 4 task sections updated (`## improve`, `## smart_trim`, `## bug_finding`, `## pdf_extract`) + 3 table rows (wiring table, Per-task PRIMARY)
- `~/.claude/scripts/diff-review.py` — `OLLAMA_CODE_MODEL` default → xentriom Q8_0 (was OmniCoder); added 12GB-VRAM warning + OmniCoder override note
- NO zshrc changes needed — `CODEQ_SUMMARY_MODEL` unchanged (Qwythos round-9)

## Installed lineup delta

Before round-10: 23 models. After: 23 (no deletions, no adds). Reorganized roles:

- **TeichAI/Fable-5-v1** now: improve #1 + web_synth #1 (multi-task)
- **xentriom Q8_0** now: bug_finding #1 + web_synth fallback (multi-task; 12GB heavy)
- **SC117/heretic-QAT** now: smart_trim #1 (was #2 fallback)
- **HauhauCS-Balanced** now: smart_trim fallback (was #1 champion; demoted)
- **OmniCoder** now: tool_call #4 + browser_tool #4 + pdf_extract #2 + bug_finding fallback (depth only, was multi-primary)

## What the next round should test

| hypothesis | bench |
|---|---|
| TeichAI also wins pdf_extract or tool_call (multi-task depth) | 4-way each with TeichAI added |
| SC117/heretic-QAT also wins improve or bug_finding (same pattern as smart_trim upset) | 4-way each |
| xentriom Q8_0 also wins tool_call (cross-task from web_synth + bug_finding) | 4-way |
| A coder-tuned 14B-A3B MoE breaks code_gen ceiling (Qwen3.6/3.7 family) | NEW pull + smoke + deep code_gen 4-way |
| gemma-4-oficial (Google) ollama pull resolves on Ollama 0.32+ | retry pull, then 4-way codeq_sum |
| OmniCoder under Qwythos-as-leader (multi-Qwythos family?) — does Qwythos or TeichAI win tool_call when added? | 4-way tool_call with Qwythos added |

## Decision matrix

| condition | action |
|---|---|
| Round-11 confirms TeichAI multi-task champion (≥3 tasks) | promote TeichAI to "universal default"; consider qwen3.5-9B family as the canonical base for new pulls |
| Round-11 SC117 wins another task | consider full heretic-12B rotation across all gemma-4-12B roles |
| Round-11 14B-A3B MoE coder breaks lift | pull + rewire code_gen |
| Ollama 0.32+ releases | retry google/gemma-4-E4B-oficial pull, then 4-way codeq_sum |
| Cross-task challengers keep dethroning in round-11 | pattern suggests the lineup is fundamentally unstable; consider permanent 4-way bench as part of every re-bench cycle |