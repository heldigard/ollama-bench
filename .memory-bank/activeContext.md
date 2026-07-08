# Active Context
- 2026-07-08: Bench methodology improvements complete. Ecosystem verified.

## Current Objective
- **Task**: Improve bench discrimination + verify ecosystem alignment
- **Phase**: Ship (all changes done, tests pass, pushed)
- **Next**: Run new bench with improved prompts to validate discrimination

## Verified This Session
- 187/187 tests pass (was 185 before adding new cases)
- All consumer repos pass: prompt-improve (116), smart-trim (158), web-research (65)
- diff-review.py --help works
- All configs already point to new champions
- env vars in ~/.zshrc correct: CODEQ_SUMMARY_MODEL=crow:9b
- ollama-bench pushed (84ae2d1)
- Consumer repos already pushed by previous agent

## Bench Improvements Made
- Split canonical_tasks.py → prompts.py (data) + canonical_tasks.py (scoring)
- Added 15 new edge-case prompts across 5 canonical tasks (each task now 6-7 regular + 3 hard)
- Redesigned HARD_PROMPTS: genuine hard scenarios instead of concatenated cases
- Improved all 5 task scorers: gradated scoring, conflict-flagging, source utilization
- Added depth scoring to _hygiene: specificity bonus, verbosity penalty
- Added 4 harder tool_call cases (ambiguous, enum, missing optional, implicit date)
- Added 2 harder bug_finding diffs (async/concurrency, type confusion)
- Updated tie_break/command.py to use iter_hard_cases

## Key Decisions
- Hard prompts are NOT just concatenated regular cases — they're genuinely harder scenarios
- Scorer improvements focus on discrimination, not just correctness
- prompts.py split keeps files under 500 LOC limit
- Openclaw is the new smart_trim/code_gen champion
- DeltaCoder is the new web_synth/bug_finding champion
- OmniCoder is the new improve champion

## Preserved Negative Constraints
- DO NOT pull Q5/Q6/Q8 variants of existing Q4 winners
- DO NOT rewire harness based on combined-rank when one pass saturates
- DO NOT install models >10GB (RTX 5080 16GB constraint)
- DO NOT discard strippable models solely for thinking leaks

## Live-env drift
- `CODEQ_SUMMARY_MODEL` exported in `~/.zshrc` as `crow:9b`. Live Claude Code sessions don't re-source zshrc → stale export wins until relaunch.
- 2026-07-08: continuaremos maniana, de momento debes diseniar los bench para que hayan pausas entre prueba y prueba para permitir mantener una temperatura baja, y lo mas no perder los resultados queriendo reiniciar siempre todo el progreso completo
- 2026-07-08: continuaremos maniana, de momento debes diseniar los bench para que hayan pausas entre prueba y prueba para permitir mantener una temperatura baja, y lo mas no perder los resultados queriendo reiniciar siempre todo el progreso completo
