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

## Critical invariants

1. **`think: false` is TOP-LEVEL** in the Ollama API body. Putting it inside `options` is silently ignored.
2. **Leak gate is HARD-DISQUALIFICATION** for the task it leaked on. A model that leaks thinking on `codeq_sum` is removed from the codeq summary ranking entirely.
3. **Scoring is deterministic**: same input → same output. Tests mock the HTTP layer.
4. **Outputs are regenerable**: cache to `~/.cache/ollama-bench/`, not git-tracked.

## What this methodology does NOT cover

- **Multi-turn conversation quality**. Single-prompt smoke doesn't simulate a full chat session.
- **Tool calling**. Use `ollama-bench` browser subagent for that (separate package).
- **Reasoning depth**. Use the `reason` prompts in multi-domain for that (legacy).
- **Embedding quality**. Use `ollama-bench embedding eval` for that (separate slice).

For these, see:
- `~/.claude/hooks/agent_browser_subagent.py` (browser tool calling)
- `~/.claude/scripts/diff-review.py` (code review)
- `~/.claude/scripts/cheap_bench.py` (cloud cascade)