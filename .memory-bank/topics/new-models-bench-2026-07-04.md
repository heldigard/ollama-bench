# New-Models Bench (2026-07-04) — 4 HF candidates vs incumbents

> 4 HuggingFace candidates pulled + benched against the current RANKING
> incumbents. Deep scores are first-pass (saturate at 7.0); bug_finding +
> tool_call are ground-truth slices (directly comparable across models).

## Smoke (leak gate)

| model | status | strippable | tps | note |
|---|---|---|---|---|
| `kwangsuklee/...Reasoning-Distilled:latest` | leak:think_tag_close,thinking_prefix | **1** | 11.8 | reasoning model; salvageable via `--strip` |
| `hf.co/yuxinlu1/...Claude-4.6-4.8-Opus:Q4_K_M` | ok | 0 | 5.7 | clean |
| `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` | ok | 0 | 3.1 | clean |
| `hf.co/DuoNeural/OpenYourMind-Gemma4-12B-IT-Abliterated:Q4_K_M` | ok | 0 | 3.0 | clean |

## Deep (clean, first-pass 0–7) vs incumbent primaries

| task | incumbent #1 (score) | best new (score) | verdict |
|---|---|---|---|
| improve | pegasus912 (3.44) | kwangsuklee (0.75) | incumbent holds |
| codeq_sum | batiai/gemma4-e4b:q4 (6.52) | huihui (5.98) | incumbent holds |
| smart_trim | SetneufPT/Qwopus3.5-4B (7.0) | huihui (7.0 sat) | tie — needs tie-break |
| web_synth | batiai/gemma4-e4b:q4 (7.0) | huihui (7.0 sat) | tie — needs tie-break |
| code_gen | fredrezones55/Qwopus3.5:9b (6.0) | huihui (5.83) | incumbent holds |

## Bug-finding (ground-truth, directly comparable) — 🏆 UPSET

| # | score | model |
|---|---|---|
| **1** | **17.98** | **`huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K`** ← NEW #1 |
| 2 | 15.00 | kwangsuklee reasoning-distilled |
| 3 | 13.48 | yuxinlu1 Opus 4.8 |
| 4 | 11.66 | DuoNeural abliterated |
| — | 15.21 | *(incumbent cryptidbleh/gemma4-claude-sonnet-4.6 — RANKING)* |

**huihui BEATS the incumbent bug_finding #1 (cryptidbleh 15.21) by +2.77.**
This is the clearest win: a Qwen3.5-9B + Opus abliterated merge out-bug-hunts
the Gemma4-Claude-Sonnet merge. Recommend rewiring `diff-review.py` CODE_MODEL
→ huihui (with cryptidbleh as fallback).

## Tool-call (new slice, ground-truth, 0–~11)

| # | score | model |
|---|---|---|
| 1 | 9.82 | huihui |
| 2 | 8.74 | kwangsuklee |
| 3 | 8.30 | yuxinlu1 / DuoNeural (tie) |

All 4 emit valid JSON + correct tool+args. huihui strongest. (No incumbent
comparison — tool_call is a new slice; the existing lineup wasn't benched on it
yet. Re-benching incumbents on tool_call is a documented next step.)

## Decisions

### KEEP
- **`huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K`** — new bug_finding
  #1 (17.98 > 15.21), saturated smart_trim/web_synth (tie-break candidate),
  top tool_call. Strong all-rounder. **Rewire bug_finding primary.**
- **`kwangsuklee/...Reasoning-Distilled:latest`** — bug_finding 15.00 (parity
  with incumbent), tool_call 8.74, and the live demonstrator of the `--strip`
  path (leaks `<think>`, strippable=1). Useful for analysis tasks + reasoning
  diversity.

### DROP (below incumbents everywhere; free ~15 GB)
- `hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus:Q4_K_M` — weak on all 5
  deep tasks (best 2.59), bug_finding 13.48 < incumbent. Opus 4.8 style didn't
  translate to bench wins. (Had one high tool_call 9.93 in a 2-model spot-test,
  but 8.30 in the full run — variance; not enough to keep.)
- `hf.co/DuoNeural/OpenYourMind-Gemma4-12B-IT-Abliterated:Q4_K_M` — weak across
  the board, lowest bug_finding (11.66). Incremental over the existing
  heretic/abliterated Gemma4-12B models (SC117, pegasus912) already installed.

## Caveats

- Deep scores are first-pass (saturate 7.0). The saturated ties (smart_trim,
  web_synth) need a tie-break run to discriminate huihui vs incumbents —
  documented as the next step.
- `--strip` mode on kwangsuklee improved the codeq_sum score monotonically with
  budget (-5.3 raw → -4.0 strip@200 → -3.0 strip@600) but stayed negative: the
  reasoning trace is long + the cleaned answer is still verbose for the 30-word
  codeq_sum budget. Strip is mechanically correct; the model just isn't a great
  codeq_sum fit. Confirms strip WORKS, not that every leaky model wins.
- seed=42 now pinned → these numbers are reproducible.

## Round-2 additions (2026-07-04)

### bge-m3 (embedding) — INSTALLED, dimension caveat
- Pulled + functional (`/api/embeddings` returns dim=**1024**).
- Multilingual MTEB #1 (dense+sparse+multi-vector).
- **CAVEAT**: host's embeddinggemma + nomic-embed-text are **768-d**; the
  memory-semantic index (`~/.claude/scripts/memory-semantic.py`, semindex) is
  768-d. bge-m3 CANNOT drop-in swap — it needs a separate index OR a full
  re-index. Decision deferred to the embedding_retrieval bench (P0 roadmap):
  bench bge-m3 vs embeddinggemma on the bilingual retrieval set, then decide
  whether the multilingual quality justifies the re-index.
- nomic-embed-text stays the universal embed fallback for now.

### yuxinlu1 composer v2-3.5x-tau2 (Gemma4-12B agentic fable5+composer2.5)
- Newest composer/fable blend (distinct from the installed xentriom Q8_0 v2).
- Smoke clean (ok, 4.49s, tps 6.7). Benched: see results below.

### Embed decision (resolved 2026-07-04 via embedding-retrieval slice)
| model | MRR | recall@5 |
|---|---|---|
| bge-m3 | 1.000 | 1.000 |
| embeddinggemma | 1.000 | 1.000 |
| nomic-embed-text | 0.875 | 1.000 |

bge-m3 TIES embeddinggemma (both perfect on the 8-case bilingual set). Since
embeddinggemma is already installed + 768-d (matches the memory-semantic index)
and bge-m3 is 1024-d (would need a full reindex), there is NO reason to switch.
**Decision: embeddinggemma stays primary; bge-m3 kept as a multilingual
alternative only. No reindex.** (The bench is low-discrimination — gold is
clearly distinct in all 8 cases; a harder set with near-duplicate distractors
would be needed to pick a true winner. Documented as future work.)
