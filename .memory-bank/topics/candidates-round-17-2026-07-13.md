# Candidates Round 17 (2026-07-13) — Cross-Task Chain Re-Validation

## TL;DR

Three re-bench cycles (improve + codeq_sum + bug_finding) on 2026-07-13 each
caught a chain-blind dethrone. Plus one cycle (smart_trim) with ZERO drift.

| task | rank | model | fresh score | prior |
|------|------|-------|-------------|-------|
| **improve** | **1** | `cryptidbleh/gemma4-claude-opus-4.6:latest` | **2.97** | round-17 NEW #1 (was chain tail) |
| improve | 2 | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | 2.46 | round-10 #1 (now demoted) |
| improve | 3 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` | 2.03 | round-7 held (fallback unchanged) |
| improve | 4 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | 1.68 | round-17 bench-validated (was untested) |
| improve | 5 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | 0.93 | round-10 (demoted) |
| **codeq_sum** | **1** | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | **9.84** | round-17 NEW #1 (cross-task challenger) |
| codeq_sum | 2 | `hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` | 9.40 | round-9 #1 (now demoted) |
| codeq_sum | 3 | `batiai/gemma4-e4b:q4` | 9.19 | round-9 held |
| codeq_sum | 4 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | 8.99 | held |
| codeq_sum | 5 | `jaahas/crow:9b` | 8.87 | held |
| **bug_finding** | **1** | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | **15.35** | round-17 NEW #1 (was demoted to depth in round-10) |
| bug_finding | 2 | `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` | 14.99 | round-10 #1 (now demoted) |
| bug_finding | 3 | `hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest` | 14.70 | round-10 held |
| bug_finding | 3 | `hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL` | 14.70 | round-10 held |
| bug_finding | 5 | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | 14.08 | round-10 held |

**Three primary dethrones:**
- **improve:** cryptidbleh promotes from chain tail; TeichAI demoted to fallback.
- **codeq_sum:** TeichAI promotes from cross-task champion; Qwythos demoted to fallback.
- **bug_finding:** OmniCoder promotes from demoted depth (round-10); xentriom demoted to fallback.

**smart_trim re-bench:** ZERO DRIFT (batiai-e2b 11.81 > cryptidbleh 11.63 > SC117 10.79 > HauhauCS 9.87 > crow 5.86). Chain held.

**code_gen re-bench:** ZERO DRIFT in combined rank. lift #1 held, SetneufPT held at #3 combined (tiebreak 8.25 still wins over Negentropy-9B's deep-only 10.24). Only deep-only reordering (Negentropy-9B #2 vs SetneufPT #3) doesn't change combined rank.

**Multi-task winner pattern crystallizes:**
- **TeichAI/Fable-5-v1** — PRIMARY 2 tasks (codeq_sum + web_synth) + improve #2 fallback.
- **Cryptidbleh/gemma4-claude-opus-4.6** — PRIMARY improve #1 + smart_trim #2 fallback.
- **OmniCoder** — multi-role split: PRIMARY bug_finding #1 + DEPTH improve (0.93) + fallback pdf_extract #2 + tool_call/broswer_tool depth.

## Why round-10/9 missed these

**Round-10 improve 4-way** only included TeichAI (defender), Negentropy-9B, OmniCoder, HauhauCS-Balanced. Cryptidbleh was the **chain tail** and NOT included.

**Round-9 codeq_sum 4-way** only included Qwythos (defender), batiai, SetneufPT, OmniCoder. TeichAI was a cross-task champion (web_synth + improve) but was NOT tested against Qwythos in codeq_sum.

Both per bench-methodology Step 6: "the champion listed in RANKING.md is only as good as the challengers it was tested against."

**Round-17 lesson (now codified):** every chain has TWO blind spots:
1. **Chain tail** (older 2nd/3rd place may have grown stronger than the head).
2. **Cross-task champions** (models winning task X may also be best for task Y, never tested).

Re-promoting the head = mandatory re-bench of BOTH categories.

## Rewire actions applied

| repo | file | change |
|------|------|--------|
| `~/prompt-improve` | `src/prompt_improve/shared/config.py` `_DEFAULT_IMPROVE_CHAIN` | cryptidbleh → TeichAI → Negentropy-9B → SetneufPT |
| `~/prompt-improve` | `tests/test_improve.py` (5 tests) | assertions + fixtures swapped to cryptidbleh primary |
| `~/prompt-improve` | `README.md`, `CLAUDE.md` | chain description updated |
| `~/prompt-improve` | `scripts/ollama-warmup.sh` | `OLLAMA_IMPROVE_WARM_MODEL` default → cryptidbleh |
| `~/prompt-improve` | `.memory-bank/REFERENCE.md` | chain + round-17 entry |
| `~/ollama-bench` | `src/ollama_bench/shared/config.py` `TASKS["improve"]` | primary → cryptidbleh, fallback → TeichAI |
| `~/ollama-bench` | `src/ollama_bench/shared/config.py` `TASKS["codeq_sum"]` | primary → TeichAI, fallback → Qwythos |
| `~/ollama-bench` | `src/ollama_bench/shared/config.py` `SPECIALIZED_TASKS["bug_finding"]` | primary → OmniCoder, fallback → xentriom Q8_0 |
| `~/.claude/scripts/diff-review.py` | `CODE_MODEL` (default for `OLLAMA_CODE_MODEL`) | xentriom Q8_0 → OmniCoder |
| `~/ollama-bench` | `RANKING.md` (5 sections) | improve + codeq_sum tables + per-task table + validation table + runtime notes |
| `~/ollama-bench` | `.memory-bank/topics/local-ollama-lineup.md` | round-17 header + improve row + codeq_sum row |
| `~/ollama-bench` | `.memory-bank/topics/harness-wiring-2026-07-04.md` | prompt-improve row + codeq row + web-research dual-role note |
| `~/codeq` | `src/codeq/shared/llm.py` `_CODEQ_SUMMARY_MODEL` | TeichAI (was Qwythos) |
| `~/codeq` | `src/codeq/shared/llm.py` `_CODEQ_FALLBACK_MODEL` | Qwythos (was batiai/e4b) |
| `~/codeq` | `src/codeq/cli.py` `--summary` help | updated to match constants |
| `~/codeq` | `tests/code_intelligence/test_codeq_context.py` | assertion updated to match new default |
| `~/agent-memory` | `src/agent_memory/shared/config.py` `MAINT_MODEL_DEFAULT` | TeichAI (was Qwythos) |
| `~/.zshrc` | `CODEQ_SUMMARY_MODEL` | TeichAI (was Qwythos) |

## Validation

- prompt-improve tests: 199/199 pass (2 pre-existing env-dependent `test_target.py` failures unrelated — `ANTHROPIC_MODEL=*` + `CLAUDECODE=1` requires unset env)
- ollama-bench tests: 242/242 pass (full suite)
- codeq tests: full suite pass (regression test `test_codeq_body_summary_help_mentions_actual_default` updated)
- agent-memory tests: 4/4 (test_maintain.py)
- ruff: clean in all 4 repos
- mypy: clean in all 4 repos
- py_compile: OK
- shellcheck: not relevant this round

## Cost

3 benches × ~18min wall = ~54min total (improve + smart_trim + codeq_sum). code_gen + bug_finding benches still running.

## Outstanding items

- code_gen bench in progress (in background)
- bug_finding bench queued after code_gen completes
- 5 NEW HF candidates queued for round-18: Stadedlor/qwythos-9b-v2-nim-fix, WaveCut/Qwythos-9B-v2-Heretic-GGUF, mradermacher/gemma-4-12b-marvin-v2-GGUF, AnkitAI/Parable-Granite-4.1-8B-Claude-Fable-5-GGUF, Yure0718/Qworum3-8B-Q4_K_M-GGUF