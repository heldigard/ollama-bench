# Bench Methodology
> How ollama-bench measures model quality.

## Core principle: Leak gate first, multi-prompt second, tie-break on saturation.

### Step 1: Smoke (1 prompt × N models, ~3s/model)

Single short prompt that should elicit a clean 1-sentence answer:
> "Reply in ONE sentence: what is the difference between a Python list and a tuple?"

Scoring:
- `ok` — clean response, no leaks, within num_predict budget
- `leak:<tags>` — `<think>`, `Thinking Process:`, `As an AI`, `I cannot`, etc.
- `http_error` / `net_error` — Ollama failed to load the model

A model that fails smoke is removed from the deep bench candidates. Saves ~90s/model on average.

### Step 2: Deep (5 tasks × N candidates, ~90s/model)

Tasks: `improve`, `codeq_sum`, `smart_trim`, `web_synth`, `code_gen`.

Each task has 1-2 prompts. First-pass scoring (`shared/scorer.first_pass_score`):
- Leak penalty (-5 per leak tag)
- Length budget bonus (+2 if within budget, +1 if 1.5x)
- TPS bonus (capped at +5)
- Empty response penalty (-10)

**Range -10 to +10. Saturates at +7.0 for fast+clean responses.**

This is a problem when 20+ models all hit the saturation cap. Need step 3.

### Step 3: Tie-break (harder prompts + structural scoring)

For models that saturated at +7.0 in deep:
- Re-bench with **harder prompts** (ambiguous spec, complex function, contradicting sources)
- Score with **structural rubrics** (presence of `## GOAL`, `## STEPS`, etc.)
- No saturation cap

`shared/scorer.tie_break_score`:
- Leak penalty (-8 to -10)
- Structural score (0-10 from keyword presence)
- TPS bonus (capped at +3)

**Range -10 to +15.** Discriminates "excellent" from "good enough".

### Step 4: Combined ranking

For each task, compute combined rank:
```python
combined_rank = (first_pass_rank + tie_break_rank) / 2
```

Lower = better. Top 5 per task are the winners.

### Step 5: Report

`ollama-bench report build` reads the deep_bench TSV and renders a markdown ranking.

## Why two passes?

- Cost. Most models are eliminated by smoke (~3s/model).
- Survivors get deep (~90s/model).
- Survivors-on-deep that saturated get re-benched with hard prompts (~30s/model).
- Total cost: ~120s/model for a complete evaluation across 5 tasks.
- For 40 candidates: ~80 min total. Acceptable.

## Step 6: Cross-Task 4-Way Validation (mandatory after a rewire)

**Lesson from rounds 9-12 (2026-07-12):** the champion listed in `RANKING.md` is
only as good as the challengers it was tested against. Tie-break vs a single
champion is misleading because that champion may not be the strongest in the
task — it was just the one whose flaws were the loudest. After any round that
promotes a new primary, run a **cross-task 4-way deep** with:

1. The current primary (defender)
2. The current fallback (incumbent #2)
3. The current tertiary (incumbent #3, if defined)
4. A cross-task challenger — a current primary from a **different** task

This catches:

- **Round-9 (1 dethrone)**: TeichAI/Fable-5-v1 web_synth champion → codeq_sum beat
  batiai/e4b. Cross-task pattern first observed.
- **Round-10 (3 dethrones)**: stale round-7 champions never challenged by other-task
  champions. TeichAI → improve (+1.53), SC117/heretic-QAT → smart_trim (+0.92),
  xentriom Q8_0 → bug_finding (+0.48). All three were cross-task promotions.
- **Round-11 (0 dethrones)**: round-10 champions held against round-10 cross-task
  challengers. Pattern is asymmetric: reasoning-heavy beats coding-heavy, but
  two reasoning-heavy champions don't compete (orthogonal skills).
- **Round-12 (0 dethrones)**: gemma-4 official variants (MoE 26B-A4B + 12B QAT)
  tied or lost. Confirms lineup at local optimum under current architectures.

**Pattern validity check**: if a cross-task challenger wins, it's a real dethrone.
If not, the existing champion is hardened for the current installed lineup.

### When to run this

- After ANY round that promotes a new primary (round-9, round-10).
- After pulling a new HF candidate that could plausibly win multiple tasks
  (round-12 MoE exploration).
- NOT after rounds where no rewires happen (round-11) — it's wasted cycles.

### Cost

4-way deep × 5 tasks × ~3min/task = ~1.5h GPU. Plus smoke (~30s/model). Worth
it if it produces 1+ dethrone, wasteful if it produces 0 — but you only know
after running. Triggered by external signal (new candidate OR observed stale
champion), not periodic.

## Critical invariants

1. **`think: false` is TOP-LEVEL** in the Ollama API body. Putting it inside `options` is silently ignored.
2. **Leak gate** — see "Leak handling" below. Default = hard-disqualify; `--strip` = salvage thinking-trace leaks.
3. **Scoring is deterministic + reproducible**: `seed=42` pinned in `CallOpts` (added 2026-07-04). Same input → same output. Tests mock the HTTP layer.
4. **Outputs are regenerable**: cache to `~/.cache/ollama-bench/`, not git-tracked.

## Leak handling (revised 2026-07-04 — the think-strip unlock)

`shared/scorer.detect_leaks()` now covers 14 patterns across 3 classes:
- **Thinking-trace tags**: `<think>`, `</think>`, `<reasoning>`, `<reflection>`, `<output>`
- **Turn-token leaks**: `<|channel|>` (Gemma-4 abliterated merges, e.g. Huihui — the gap `~/prompt-improve` documented)
- **Visible thinking prefixes**: `thinking process:`, `let me think:`
- **Refusals**: `as an ai`, `as a language model`, `i cannot`, `i'm just an ai`, `i'm unable to`, `i am unable to`

`leaks_are_strippable(leaks)` returns True when EVERY leak is a thinking-trace tag
(no refusals). Such models are salvageable:

- **Smoke** tags them `strippable=1` (column in the TSV).
- **`deep --strip`** includes them in the candidate set AND applies `strip_reasoning()`
  to each response BEFORE scoring — so a thinking-leak model is judged on its
  CLEANED answer, not penalized for the trace.

This UNLOCKS a class of strong reasoning models previously hard-disqualified:
DeepSeek-R1 distills, Qwen3-thinking, GPT-OSS, LFM, Gemma-4 abliterated merges.
Refusals stay hard-disqualified (a refusal isn't fixed by stripping).

## What this methodology does NOT cover (yet)

- **Multi-turn conversation quality**. Single-prompt smoke doesn't simulate a full chat session.
- **Tool calling / structured JSON output**. P0 on the roadmap — see `topics/new-benchmarks-roadmap-2026-07-04.md`.
- **Classification accuracy** (prompt-router / error-classify role). P0 on the roadmap.
- **Reasoning depth**. Use the `reason` prompts in multi-domain for that (legacy).
- **Embedding quality** (proper MRR eval). P0 on the roadmap — promote the embedding slice.
- **Rerank quality** (web-research `--smart`). P0 on the roadmap.

For these, see:
- `topics/new-benchmarks-roadmap-2026-07-04.md` (the prioritized roadmap)
- `~/.claude/hooks/agent_browser_subagent.py` (browser tool calling)
- `~/.claude/scripts/diff-review.py` (code review)
- `~/.claude/scripts/cheap_bench.py` (cloud cascade)