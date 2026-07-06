# Candidates Round 3 (2026-07-05) — 3 HF candidates vs incumbents

> Tier-S + Tier-A sweep after the 2026-07-04 re-bench. Goal: surface an upset
> on the slots where the current champion is contested or already saturated
> (improve, code_gen). Bench: smoke → deep → tie-break → bug_finding → tool_call.

## Candidates (3 pulled, 1 leak-disqualified)

| candidate | HF repo | size | why pulled | verdict |
|---|---|---|---|---|
| `Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF` | [HF](https://huggingface.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF) | 6.6 GB Q4_K_M | DeepSeek-V4 distill (not Opus) on Qwen3.5-9B base; reasoning chain-of-thought | **LEAK** at smoke (`thinking_process`, strippable=1). Reasoning-distilled pattern leakes per kwangsuklee precedent; `--strip` doesn't save. **DELETED** (freed 6.6 GB) |
| `kai-os/Grug-12B-GGUF` | [HF](https://huggingface.co/kai-os/Grug-12B-GGUF) | 7.4 GB Q4_K_M | "Compact-reasoning" fine-tune of gemma4-12B-it: ~70% fewer thinking tokens vs base, within ~2% of base capability. QLoRA merge. | **PASS smoke** (ok, 11.6s, 2.5 tps). **WINNER** — see below. |
| `HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced` | [HF](https://huggingface.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced) | 7.6 GB Q4_K_M | "Balanced" uncensored variant of gemma4-12B QAT (matches incumbent pegasus912 arch). 81K pulls = community-validated. | **PASS smoke** (ok, 11.85s, 2.2 tps). **KEEP** as code_gen tie-break contender. |

## Smoke gate (leak detection)

| model | status | strippable | dt_s | tps | etoks | len |
|---|---|---|---|---|---|---|
| DeepSeek-V4-Flash | `leak:thinking_process` | 1 | 5.33 | 15.0 | 80 | 319 |
| Grug-12B | `ok` | 0 | 11.64 | 2.5 | 29 | 144 |
| HauhauCS Balanced | `ok` | 0 | 11.85 | 2.2 | 26 | 129 |

## Deep bench (5 tasks, 0–7 scale, saturated scores)

| task | Grug-12B | HauhauCS Balanced | incumbent #1 | deep incumbent |
|---|---|---|---|---|
| codeq_sum | 2.16 | 3.33 | batiai/gemma4-e4b:q4 | 6.52 |
| smart_trim | 2.58 | **7.00 SAT** | SetneufPT/Qwopus3.5-4B-Coder-MTP | 7.00 SAT |
| web_synth | 1.18 | **7.00 SAT** | batiai/gemma4-e4b:q4 | 7.00 SAT |
| improve | **3.54** | 0.12 | pegasus912/gemma-4-12b-heretic | 3.44 |
| code_gen | **6.00** | 1.81 | fredrezones55/Qwopus3.5:9b | 6.00 |

Reads: Grug beats incumbents on improve (+0.10 marginal, in noise). Both lose codeq_sum clearly.

## Tie-break (hard prompts, structural scoring, no 7.0 cap) — **discriminates**

Re-run on 2 candidates + 4 incumbents (2026-07-05). Range -5 to +15. **Higher = better.**

### Improve (HARD PROMPT — the decisive slice)

| # | Score | Model | Δ vs incumbent (pegasus912) |
|---|---|---|---|
| **1** | **8.39** | **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** ← **NEW #1** | **+4.24 (2× incumbent)** |
| 2 | 5.08 | fredrezones55/Qwopus3.5:9b | +0.93 |
| **3** | **4.15** | pegasus912 incumbent | 0 (baseline) |
| 4 | 3.69 | HauhauCS Balanced | -0.46 |
| 5 | 3.67 | SetneufPT/Qwopus3.5-4B-Coder-MTP | -0.48 |
| 6 | 1.87 | batiai/gemma4-e4b:q4 | -2.28 |

**Reproduce confirm**: re-ran Grug vs pegasus912-only tie-break → Grug **8.53**, pegasus912 **4.37** (delta +4.16). Wins consistently despite seed-level noise (~0.2).

### Other tasks tie-break (for completeness, not changes)

| task | Grug | HauhauCS | top incumbent | verdict |
|---|---|---|---|---|
| codeq_sum | 8.09 | 6.08 | fredrezones55 13.00 | Loses both — incumbent holds |
| smart_trim | 10.50 | 7.73 | (multiple 10.50) | Grug ties at top (saturated inconclusive) |
| web_synth | 10.50 | 7.87 | (multiple 10.50) | Grug ties at top (saturated inconclusive) |
| code_gen | 16.00 (ties 3-way) | **16.00** (ties 3-way) | multiple at 16 | HauhauCS saturates with batiai/SetneufPT — keeps as tie-break contender |

## Hero benched (ground-truth, directly comparable)

### Bug-finding (recap of earlier + new)

| # | Score | Model |
|---|---|---|
| 1 | 18.50 | huihui_ai (incumbent #1, unchanged) |
| 2 | 15.35 | cryptidbleh (incumbent #2, unchanged) |
| **3** | **15.09** | **Grug-12B** ← new contender |
| 4 | 14.37 | HauhauCS Balanced |
| 5 | 12.15 | SetneufPT incumbent |

Grug-12B is **#3**, just 0.26 below cryptidbleh #2. Competitive fallback option.

### Tool-call

| # | Score | Model |
|---|---|---|
| 1 | 9.82 | huihui_ai (incumbent, unchanged) |
| **2** | **9.81** | **Grug-12B** ← ties incumbent within noise (0.01) |
| 2 | 9.81 | slyfox functiongemma |
| 4 | 9.02 | HauhauCS Balanced |
| 5 | 8.67 | kwangsuklee |

Grug-12B at 9.81 is **statistically tied** with huihui 9.82 — within tps-bonus noise.

## Decisions

### KEEP — install permanently
1. **`hf.co/kai-os/Grug-12B-GGUF:Q4_K_M`** (7.4 GB)
   - **NEW improve PRIMARY** (2× incumbent pegasus912 on hard prompts)
   - Competitive on tool_call (#2, 9.81, statistical tie with huihui 9.82)
   - Bug_finding #3 (15.09, near incumbent #2 15.35)
   - Code_gen tie at 16.00 (saturated, but tied with the top)
   - WP claim ("compact reasoning") confirmed in benchmark: Grug wins improve by exactly the mechanism — less verbose thinking = better structured rewrites.
2. **`hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M`** (7.6 GB)
   - Code_gen saturated tier (16.00 ties with batiai/SetneufPT/fredrezones55)
   - Useful as diversity option for the codebase gemma4-12B arch family
   - Loses improve to both Grug and pegasus912 — not a rewire candidate

### DROP — leaked at smoke
- **`hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M`** — deleted (6.6 GB freed). Reasoning-distilled models on Qwen3.5-9B base consistently leak thinking despite `think=False` (same pattern as `kwangsuklee`).

## Caveats

- **Tie-break variance**: tie-break is single-prompt per task, deterministic-by-seed BUT we observe ~0.2 score variation between identical runs (presumably ollama prompt-cache timing or stream-chunk evaluation). The 8.39 vs 4.15 (or 8.53 vs 4.37) gap is large enough (delta 4.0+ on a -5..+15 scale) to be safely outside noise. Confirm with a third run if wanted.
- **Bug-finding is not in the deep → tie-break pipeline** by default. We added it ad hoc per candidate because the user asked for hero slices.
- **Smart_trim and web_synth tie-break still saturate 10.50** at the top — neither Grug nor any incumbent clearly beats the others on these. The structural-scoring formula needs an upper bound increase to discriminate further, OR a new harder prompt set is needed.
- **Codeq_sum incumbent holds** — neither new candidate is competitive.

## Recommended harness rewires (next user action)

| tool | role | old model | new model | delta |
|---|---|---|---|---|
| prompt-improve | improve | `pegasus912/gemma-4-12b-heretic` | `kai-os/Grug-12B-GGUF` | +4.0 on hard prompts |
| diff-review | bug_finding | `huihui_ai/qwen3.5-9b-Opus` | unchanged (huihui still #1 18.50) | Grug available as #3 fallback |
| ollama_client tool_call fallback | tool_call | (none) | `kai-os/Grug-12B-GGUF` as #2 | Grug within 0.01 of huihui |

## Rewires DONE (2026-07-05, this session)

✅ **`~/ollama-bench/src/ollama_bench/shared/config.py::TASKS["improve"]`** — primary swapped pegasus912 → Grug-12B; fallback demoted to pegasus912. Verified: `python3 -m py_compile`, `ruff check`, dict lookup, `pytest tests/test_layout.py tests/test_list.py -q` (9/9).

✅ **`~/prompt-improve/src/prompt_improve/shared/config.py::_DEFAULT_IMPROVE_CHAIN`** — Grug-12B prepended (chain 3 → 4). Verified: `python3 -m py_compile`, `ruff check`, dict lookup, full `pytest tests/` (102/102 pass).

✅ **`~/prompt-improve/tests/test_improve_prompt.py::test_role_model_map_prefers_gemma4`** — assertion updated from name-substring (`"gemma" in name`) to ollama `details.family` check. Same gemma4-arch property, robust to future fine-tunes that don't have "gemma" in the tag.

✅ **`~/prompt-improve/scripts/ollama-warmup.sh`** — default `OLLAMA_IMPROVE_WARM_MODEL` swapped pegasus912 → Grug-12B. Verified: `shellcheck -S warning` clean.

✅ **`~/prompt-improve/.memory-bank/REFERENCE.md`** — docs updated to reflect new chain + #1/#2/#3 ranks.

## KEEP (no rewire — bench-validated, not proxy)

- **`~/cli-orchestration/src/cli_orchestration/browser/{subagent.py,_subagent_call.py}`** — pegasus912 is the **browser-tool bench FALLBACK** (browser-tool #5 9.70 per harness-wiring-2026-07-04.md), NOT an improve proxy. Different rationale (gemma4-family diversity vs qwen3.5 PRIMARY functiongemma). Keep — re-benching browser-tool with Grug-12B is a future task.
- **`~/ollama-bench/src/ollama_bench/features/pdf_extract/command.py`** — pegasus912 is pdf_extract tied-#1 (11.14 per 2026-07-04 round). Different bench slice, no proxy. Keep.

## Round-4 candidates to consider (next session)

- `HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive` (501K pulls) — uncensored Qwen3.5-9B, likely bug_finding contender (huihui is similar arch)
- `DavidAU/Qwen3.5-9B-Claude-4.6-HighIQ-THINKING-HERETIC` (54K) — reasoning+heretic, but high leak risk
- `lmstudio-community/Phi-4-mini-reasoning-GGUF` — Phi family diversity, code/bug_finding potential
- `Mia-AiLab/Gemmable-4-12B-MTP-GGUF` (194K) — gemma4 MTP; potential smart_trim candidate

## Known false-positive (verbatim)

`HammerAI/gemma-4-12b-heretic` and `baytout3/ultragemma4-12b-heretic-uncensored` both appeared in Ollama search results (5-day / 1-week old releases). Not benched this round — judged low upside vs the 3 we already pulled (no time budget). Documented for round 4 if user wants fresh heretic coverage.
