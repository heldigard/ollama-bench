# Current Task
> Phase 5 of 7: memory bank setup (in progress)

## Remaining phases

- Phase 6: move old bench scripts from `~/bench/ollama/` to `~/ollama-bench/docs/history/`
- Phase 7: `git init`, `gh repo create heldigard/ollama-bench --public`, push main, add `.github/workflows/test.yml`

## Acceptance for current phase

- `~/.cache/ollama-bench/{results,logs}/` populated on real run (smoke + deep + tie-break + report)
- All tests pass: `python3 -m pytest tests/ -q` → 46 passed
- `ollama-bench --help` lists 9 sub-commands
- Layout gate enforces: each features/<slice>/ has command.py with cmd_<slice>, shared/ doesn't import features/, no cross-feature imports