# Context
> Current state of ollama-bench as of 2026-07-04

## Status: v0.1.0 — initial vertical-slice split (graduate from ~/bench/ollama/)

46 tests passing. CLI live with 9 sub-commands. GitHub repo not yet pushed.

## Active subcommands

| cmd | purpose | entry point |
|---|---|---|
| `list` | enumerate installed models + flag incompat | features/list/command.py |
| `smoke` | 1-prompt leak gate per model | features/smoke/command.py |
| `deep` | 5-task × N model bench | features/deep/command.py |
| `tie-break` | re-bench tied candidates with harder prompts | features/tie_break/command.py |
| `lfm-variant` | codeq summary tie-break for LFM family (think-strip) | features/lfm_variant/command.py |
| `multi-domain` | legacy 4-domain bench (improve/compact/code/reason) | features/multi_domain/command.py |
| `judge` | LLM-as-judge helpers | features/judge/command.py |
| `embedding` | embedding model evaluation | features/embedding/command.py |
| `report` | markdown ranking generation from TSV | features/report/command.py |

## Bench results snapshot (2026-07-04)

- 63+ models installed
- 3 truly DEAD on Ollama 0.23.2: Mobius (gemma4 Q4_0), SetneufPT (qwen3next MTP), VladimirGav (worked after re-pull)
- 9 LFM variants all leak thinking (known broken)
- 16 http_error non-winner gemma4-12B variants (recoverable via re-pull)
- Combined-rank winners per task (avg of first-pass + tie-break):
  - **improve**: fredrezones55/Qwopus3.5:9b (6.5GB, fast)
  - **codeq_sum**: batiai/gemma4-12b:q2 (4.5GB)
  - **smart_trim**: qwen3.5:4b + fredrezones55/Qwopus3.5:9b (tied)
  - **web_synth**: batiai/gemma4-e2b:q6 (3.8GB)
  - **code_gen**: cryptidbleh/gemma4-claude-opus-4.6 (3.4GB)

See `topics/local-ollama-lineup.md` for full table.

## Critical caveats

- **`think` is TOP-LEVEL** in Ollama API (not inside `options`). Putting it inside options is silently ignored — qwen3.x + gemma4 still emit the thinking trace.
- **Ollama 0.23.2 incompat** with gemma4 Q4_0 + qwen3next MTP. See topics/ollama-0.23.2-gemma4-q4_0-incompat.md.
- **LFM2.5-8B-A1B** leaks thinking despite think=False. Not a codeq summary candidate.

## Open items

- [ ] Push to GitHub (gh repo create heldigard/ollama-bench)
- [ ] Add GitHub Actions pytest workflow
- [ ] Re-run bench against the final lineup to verify scores
- [ ] Decide what to do with 16 broken http_error models (re-pull vs delete)