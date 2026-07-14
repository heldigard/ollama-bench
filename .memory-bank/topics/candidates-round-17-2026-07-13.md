# Candidates Round 17 (2026-07-13) — Improve Re-bench After Round-10 Blind Spot

## TL;DR

Fresh 5-way deep re-bench of the improve task dethroned the round-10 champion
with the chain-tail model that round-10 never included:

| rank | model | fresh score | prior |
|------|-------|-------------|-------|
| **1** | `cryptidbleh/gemma4-claude-opus-4.6:latest` | **2.97** | round-17 NEW #1 (was chain tail) |
| **2** | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` | 2.46 | round-10 #1 (now demoted) |
| 3 | `hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M` | 2.03 | round-7 held (fallback unchanged) |
| 4 | `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest` | 1.68 | round-17 bench-validated (was untested in improve) |
| 5 | `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | 0.93 | round-10 (demoted) |

**One primary dethrone:** cryptidbleh promotes to improve #1. TeichAI demoted to
fallback. Negentropy-9B held at #3. SetneufPT now bench-validated. OmniCoder
held lowest (already demoted).

## Methodology

- Bench command: `ollama-bench deep -t improve -c <5 models> --cooldown 30 --strip -o /tmp/improve_revalidation_2026-07-13.tsv`
- 11 prompts × 5 candidates, seed=42, smoke-OK only (all 5 passed leak gate)
- Rubric: `canonical_tasks.py::_score_improve` (no cap, structural, evidence penalty up to -8)
- GPU temp stayed 55-67°C across the run

## Why round-10 missed this

Round-10 4-way validation only included:

1. TeichAI/Fable-5-v1 (defender)
2. Negentropy-9B (incumbent #2)
3. OmniCoder (incumbent #3 / depth)
4. HauhauCS-Balanced (cross-task smart_trim challenger)

Cryptidbleh was the **chain tail** (legacy 2026-07-09 #1, smart_trim round-15 #2)
and was NOT included. Per bench-methodology Step 6: "the champion listed in
RANKING.md is only as good as the challengers it was tested against. Tie-break
vs a single champion is misleading because that champion may not be the
strongest in the task — it was just the one whose flaws were the loudest."

Round-17's lesson: **never trust a chain-tail to be weaker than the head**.
The tail should be re-validated when re-promoting the head, even if its other
tasks (smart_trim) are stable.

## Rewire actions applied

| repo | file | change |
|------|------|--------|
| `~/prompt-improve` | `src/prompt_improve/shared/config.py` `_DEFAULT_IMPROVE_CHAIN` | cryptidbleh → TeichAI → Negentropy-9B → SetneufPT |
| `~/prompt-improve` | `tests/test_improve.py` (5 tests) | assertions + fixtures swapped to cryptidbleh primary |
| `~/prompt-improve` | `README.md`, `CLAUDE.md` | chain description updated |
| `~/prompt-improve` | `scripts/ollama-warmup.sh` | `OLLAMA_IMPROVE_WARM_MODEL` default → cryptidbleh |
| `~/prompt-improve` | `.memory-bank/REFERENCE.md` | chain + round-17 entry |
| `~/ollama-bench` | `src/ollama_bench/shared/config.py` `TASKS["improve"]` | primary → cryptidbleh, fallback → TeichAI |
| `~/ollama-bench` | `RANKING.md` (4 sections) | improve table + per-task table + validation table + runtime notes |
| `~/ollama-bench` | `.memory-bank/topics/local-ollama-lineup.md` | round-17 header + improve row |
| `~/ollama-bench` | `.memory-bank/topics/harness-wiring-2026-07-04.md` | prompt-improve row + web-research dual-role note |
| `~/ollama-bench` | `.memory-bank/topics/candidates-round-17-2026-07-13.md` | this file |

## Validation

- prompt-improve tests: 199/199 pass (2 pre-existing env-dependent `test_target.py` failures unrelated — `ANTHROPIC_MODEL=*` + `CLAUDECODE=1` requires unset env)
- ollama-bench tests: 242/242 pass (full suite)
- ruff: clean in both repos
- mypy: clean in both repos
- py_compile: OK
- shellcheck on `ollama-warmup.sh`: clean

## Cost

5 candidates × 11 prompts × ~3min/prompt = ~16min GPU + 4×30s cooldowns = ~18min wall.

## Outstanding items

- smart_trim, codeq_sum, code_gen, bug_finding chains NOT yet re-validated against
  their chain tails. Round-17 only covered improve. Round-18+ planned for those
  four (in-progress).