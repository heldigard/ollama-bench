# Active Context
> 2026-07-18 — memory correction (no bench run)

## Task
Prevent future agents from treating the installed Ollama winner library as prune candidates.

## Verified
- `RANKING.md` is SoT for PRIMARY/FALLBACK (round-17: cryptidbleh improve #1; TeichAI codeq_sum #1).
- Host maps: `~/.config/dev/ollama-roles.json`, home `topics/local-ollama-lineup.md`.
- All RANKING PRIMARY/FALLBACK tags present in `ollama list` (~23 / ~109 GiB).

## Decisions
- Keep full installed lineup. Prune only via bench history, never ecosystem “disk cleanup.”

## Next
- None for lineup. New models → full ollama-bench pipeline before any delete.
