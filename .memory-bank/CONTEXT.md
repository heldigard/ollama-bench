# Context
> Current state of ollama-bench as of 2026-07-04 (re-bench on Ollama 0.31.1)

## Status: v0.1.0 — re-bench complete on unified Ollama 0.31.1

72 tests passing. 10 CLI sub-commands. GitHub: github.com/heldigard/ollama-bench.
Final lineup: 16 LLM winners + 2 embeddings = 18 models (76 GB).

## Active subcommands

| cmd | purpose |
|---|---|
| `list` | enumerate installed models + flag leaky LFM family |
| `smoke` | 1-prompt leak gate (now skips embeddings) |
| `deep` | 5-task × N model bench |
| `tie-break` | re-bench tied candidates with harder prompts |
| `bug-finding` | diff-review task (count bugs found) — NEW |
| `lfm-variant` | codeq summary tie-break for LFM family (think-strip) |
| `multi-domain` | legacy 4-domain bench |
| `judge` | LLM-as-judge helpers |
| `embedding` | embedding model evaluation |
| `report` | markdown ranking generation |

## Re-bench 2026-07-04 results (Ollama 0.31.1, after server unification)

Per-task top-2 (wired into harness):

| task | #1 | #2 |
|---|---|---|
| improve | hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl | Librellama/gemma4:e2b-Uncensored |
| codeq_sum | batiai/gemma4-e4b:q4 | SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU |
| smart_trim | SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU | fredrezones55/Qwopus3.5:9b |
| web_synth | batiai/gemma4-e4b:q4 | batiai/gemma4-12b:iq3 |
| code_gen | fredrezones55/Qwopus3.5:9b | aratan/gemma-4-E4B-it-heretic:Q6_K |
| bug_finding | cryptidbleh/gemma4-claude-sonnet-4.6 | SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU |

See `topics/local-ollama-lineup.md` for full top-5 + the 16 winner rationale.

## Key correction from earlier bench (Ollama 0.23.2)

The earlier "DEAD" verdicts on Mobius + SetneufPT were a stale-binary artifact
(dual Windows+WSL Ollama servers, WSL stuck at 0.23.2). On 0.31.1 both load
fine. SetneufPT went on to WIN smart_trim #1. Mobius ranks low now (deleted).
See `topics/ollama-0.23.2-gemma4-q4_0-incompat.md`.

## Harness wiring (top-2 → scripts)

- `~/.claude/hooks/ollama-warmup.sh` → pegasus912 (improve #1)
- `~/.claude/scripts/agent_browser_subagent.py` PRIMARY → pegasus912 (improve winner as browser proxy)
- `~/.claude/scripts/diff-review.py` CODE_MODEL → cryptidbleh sonnet (bug_finding #1)
- `~/.claude/scripts/pdf-extract-structured.py` DEFAULT_MODEL → pegasus912
- `~/.claude/scripts/project-memory.py` _OLLAMA_MAINT_MODEL → batiai/gemma4-e4b:q4 (codeq_sum #1)
- `~/.zshrc` CODEQ_SUMMARY_MODEL → batiai/gemma4-e4b:q4
- `~/.claude/scripts/web_research/config.py` OLLAMA_SYNTH_MODEL → batiai/gemma4-e4b:q4 (web_synth #1)
- `~/prompt-improve/.../config.py` _DEFAULT_IMPROVE_CHAIN → pegasus912 → Librellama → qwen3.5:4b

## Critical caveats

- **`think` is TOP-LEVEL** in Ollama API (not inside `options`). Putting it inside options is silently ignored.
- **LFM2.5-8B-A1B** leaks thinking on EVERY Ollama version (model-inherent, not binary). Not a candidate.
- **Score saturation**: deep bench caps at 7.0; re-bench with `tie-break` for discrimination.