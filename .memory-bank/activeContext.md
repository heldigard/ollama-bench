# Active Context
- 2026-07-05: Round-5 full re-bench landed. e4b demoted (codeq_sum + web_synth); SetneufPT + crow:9b new #1.

## Current Objective (from current-objective.json)
- **Task**: more tests + re-bench all winners + update consumers + memory + commit
- **Phase**: Ship (commit + push pending across 3 repos + zshrc)
- **Next**: commit ollama-bench (tests + config + RANKING + topics); then codeq, web-research, zshrc
- **Files**: src/ollama_bench/shared/config.py, RANKING.md, tests/test_*.py (5 new), .memory-bank/topics/candidates-round-5-2026-07-05.md, ~/codeq/..., ~/web-research/..., ~/.zshrc

## Preserved Negative Constraints
- **DO NOT** pull Q5/Q6/Q8 variants of existing Q4 winners — see `topics/quant-comparison-2026-07-04.md`
- **DO NOT** rewire harness based on combined-rank when one pass saturates — weight tb higher (improve r5 lesson: Grug tb 8.35 >> SetneufPT 4.27 despite combined-rank inversion). See `topics/candidates-round-5-2026-07-05.md` §Methodology lesson.
- **DO NOT** trust smart_trim/code_gen r5 ordering — both fully saturated (tb 10.50 / 16.00 × all); maintain incumbents.

## Live-env drift (carry from round-3)
- `CODEQ_SUMMARY_MODEL` + `OLLAMA_SYNTH_MODEL` exported in `~/.zshrc`. Live Claude Code sessions don't re-source zshrc → stale export wins until relaunch. Source files correct; drift is live-env only.

## Round-5 artifacts
- `~/.cache/ollama-bench/results/{smoke_all,deep_r5.tiebreak_r5}.{tsv,md}`
