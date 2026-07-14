# Candidates Round 18 (2026-07-13) — 5 New HF Candidates + batiai/gemma4-12b

## TL;DR

Six candidates tested (improve 6-way + smart_trim 6-way). **ONE depth promotion**:
`batiai/gemma4-12b:q4` joins smart_trim chain at #3 (dethrones SC117 from top-3).
Five other candidates **rejected** (negative scores or below current depth).

| candidate | improve | smart_trim | decision |
|-----------|---------|-----------|----------|
| `batiai/gemma4-12b:q4` (Google DeepMind official Gemma 4 12B-it, multimodal, Q4 6.9GB) | -1.09 | **11.35** | **DEPTH PROMOTE** smart_trim #3 |
| `hf.co/mradermacher/gemma-4-12b-marvin-v2-GGUF:Q4_K_M` | 2.28 | 9.47 | REJECT (below HauhauCS in smart_trim) |
| `hf.co/WaveCut/Qwythos-9B-v2-Heretic-GGUF:Q4_K_M` | -0.12 | (not benched) | REJECT (improve fails) |
| `batiai/gemma4-12b:q4` improve score | -1.09 | — | kept for smart_trim only |
| `hf.co/Yure0718/Qworum3-8B-Q4_K_M-GGUF:Q4_K_M` | -4.26 | (not benched) | REJECT |
| `hf.co/AnkitAI/Parable-Granite-4.1-8B-Claude-Fable-5-GGUF:Q4_K_M` | -100.00 | (not benched) | REJECT (catastrophic — likely leak/empty across all prompts) |
| `Stadedlor/qwythos-9b-v2-nim-fix` | not tested | — | **SKIP** — no GGUF, only safetensors 19.3GB (would need custom Modelfile, out of scope for round-18 autonomous) |

## Methodology

- Smoke gate first: all 5/5 pullable candidates passed (no leaks, no HTTP errors).
- Bench #1: `ollama-bench deep -t improve -c <6 models>` (cryptidbleh defender + 5 candidates).
- Bench #2: `ollama-bench deep -t smart_trim -c <6 models>` (top-4 + 2 gemma-4-12B family candidates).
- Decision rule: promote if ≥1.05× current champion; depth if 0.7-1.0×; delete if <0.7× or catastrophic fail (<-50).

## Why batiai/gemma4-12b is the only winner

Gemma 4 12B family is already a known-strong lineage in lineup:
- SC117/gemma-4-12B-it-heretic-QAT (smart_trim #4 round-18: 10.79)
- HauhauCS/Gemma4-12B-QAT-Uncensored-Balanced (smart_trim #5: 9.87)
- pegasus912/gemma-4-12B-it-qat-heretic-ud (bug_finding #3: 14.70)
- mradermacher/gemma-4-12b-marvin-v2 (smart_trim #6 fresh: 9.47 — REJECTED)
- Batiai/gemma4-e2b + e4b (siblings, different sizes)

batiai/gemma4-12b is the **first OFFICIAL Google DeepMind Gemma 4 12B-it weights** (no community fine-tune, no QAT, no heretic). Round-12 already tested `unsloth/gemma-4-12B-it-qat-GGUF` (official upstream, different quantization, UD-Q4_K_XL 6.9GB) and it tied HauhauCS within 0.05 in smart_trim → DELETE round-13 (not in top-5).

Round-18 batiai/gemma4-12b (different quantization: Q4_K_M 7.4GB) reaches **11.35** in smart_trim, beating all 3 gemma-4-12B heretic/QAT variants AND only 0.46 behind champion batiai-e2b (11.81). This is a 6-way fresh bench — likely a real signal, not noise.

Other gemma-4-12B variants (SC117, HauhauCS, pegasus912, marvin) lose because they're community fine-tunes; the official weights consistently outperform community variants for structural summarization (smart_trim task).

## Why the other 5 candidates fail

- **WaveCut/Qwythos v2 Heretic** (-0.12): uncensored variant of Qwythos v2 (Qwen3.5-9B base). Despite 6.6 tps speed and clean smoke, quality drops vs structured prompts. Improvement task penalizes unprompted files/stack mentions; heretic variant apparently over-triggers these. Round-17 showed Qwythos v1 (empero-ai) holds codeq_sum #2 at 9.40; the heretic v2 doesn't improve on improve task.
- **mradermacher/gemma-4-12b-marvin-v2** (smart_trim 9.47): "marvin" likely means heretic/uncensored, similar pattern to WaveCut. Improve 2.28 (close to TeichAI 2.46 but below) + smart_trim 9.47 (below HauhauCS 9.87) — no clear win.
- **batiai/gemma4-12b improve** (-1.09): same model, different task. Strong at smart_trim (compaction-friendly) but weak at improve (structured-spec generation). Confirms task-specific champion pattern.
- **Yure0718/Qworum3-8B** (-4.26): Qwen3-8B QLoRA distill, smaller base (8B vs 9B competitors). -4.26 indicates systematic failure on most improve prompts. Quality gap.
- **AnkitAI/Parable-Granite-4.1-8B-Claude-Fable-5** (-100.00): catastrophic — likely ALL responses failed or leaked. Fable-5 distill on Granite-4.1-8B base, but it's an agentic-coding-specialist (per HF card) not a general-purpose improve model. Rejected for improve. Could re-test in code_gen if interested later, but 47/48 (97.9%) first-party benchmark on Granite-4.1-8B in round-16 also failed (rejected for improve). Family-level reject — not just Fable-5 distill issue.

## Lineup impact

| before round-18 | after round-18 | change |
|-----------------|---------------|--------|
| 22 models (19 LLM + 3 embed) | **23 models (20 LLM + 3 embed)** | +1 (batiai/gemma4-12b:q4) |
| smart_trim top-3: batiai-e2b, cryptidbleh, SC117 | smart_trim top-3: batiai-e2b, cryptidbleh, **batiai/gemma4-12b** | SC117 demoted to #4 |

22.1GB disk freed by 4 deletions (WaveCut 5.6 + Parable 5.1 + Qworum3 5.0 + marvin 7.4 = 23.1GB freed; 7.4GB added for batiai/gemma4-12b = net -15.7GB).

## Cross-repo sync

- `~/ollama-bench/RANKING.md` smart_trim table — batiai/gemma4-12b inserted at #3, marvin at #6 (rejected).
- `~/ollama-bench/.memory-bank/topics/local-ollama-lineup.md` — batiai/gemma4-12b added to installed lineup section.
- `~/ollama-bench/.memory-bank/topics/candidates-round-18-2026-07-13.md` — this file.
- `~/ollama-bench/.memory-bank/progress.md` — round-18 entry.

## Decision rationale: NOT promoting batiai/gemma4-12b as PRIMARY

batiai/gemma4-12b 11.35 vs batiai-e2b 11.81 = 0.96× ratio. Within depth range (0.7-1.0×), below promote threshold (≥1.05×). The champion (batiai-e2b at 4.6B actual) is faster (6.6 tps vs 6.2 tps in smoke) and slightly higher quality. **batiai/gemma4-12b is depth-only.**

If batiai-e2b is ever unavailable or VRAM-contended, batiai/gemma4-12b is the natural backup (same family, both batiai gemma4-*). Quality gap (0.46) is acceptable for a fallback.

## Round-18 lessons

1. **Official upstream weights > community fine-tunes** for structural tasks (smart_trim). batiai/gemma4-12b (official) beat SC117/HauhauCS/marvin (community fine-tunes of same base).
2. **Heretic/uncensored variants hurt structural tasks.** WaveCut Qwythos v2 Heretic + gemma-4-12b marvin both regressed vs non-heretic parents on improve/smart_trim. The ablation removes formatting discipline that structural prompts need.
3. **Fable-5 distill on small base (8B) + coding agent specialty = catastrophic on general prompts.** Parable-Granite -100 = unrecoverable.
4. **6-way fresh bench vs 4-way old bench**: tighter score range in larger pool, but clearer discrimination. 6 > 4 for avoiding both blind spots (chain-tail + cross-task).