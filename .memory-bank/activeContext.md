# Active Context
- 2026-07-08: New model bench complete. Openclaw/DeltaCoder/OmniCoder are new champions.

## Current Objective
- **Task**: Rewire consumer projects to match new RANKING.md champions
- **Phase**: Ship (config + RANKING done; consumer repos pending)
- **Next**: Update prompt-improve, smart-trim, web-research, diff-review with new model defaults; then commit + push all repos

## Verified This Session
- 14-model deep --strip bench completed (results_current_models_strip_deep_20260708.tsv)
- 12-model tool-call bench (still saturated, top-7 within 0.02)
- 10-model pdf-ocr bench (Unlimited-OCR #1, lift #3, general models fail)
- 10-model pdf-extract bench (near-saturated, Openclaw #1 by 0.05)
- 11-model bug-finding bench (DeltaCoder #1, 14.06)
- 185/185 tests pass
- config.py updated: improve→OmniCoder, smart_trim→Openclaw, web_synth→DeltaCoder, code_gen→Openclaw, bug_finding→DeltaCoder, pdf_ocr fallback→lift
- RANKING.md fully rewritten with 2026-07-08 results
- .tags added to .gitignore

## Key Decisions
- Openclaw is the new smart_trim/code_gen champion (+0.28/+0.00 over old)
- DeltaCoder is the new web_synth/bug_finding champion
- OmniCoder is the new improve champion (+0.41 over old SetneufPT)
- DeepSeek-V4-Flash kept installed but NOT recommended (strippable but quality-degraded)
- lift added as pdf_ocr fallback (OCR specialist, 112 tok/s)
- Near-saturated tasks (tool_call, browser_tool, pdf_extract) keep existing wiring

## Preserved Negative Constraints
- DO NOT pull Q5/Q6/Q8 variants of existing Q4 winners
- DO NOT rewire harness based on combined-rank when one pass saturates
- DO NOT install models >10GB (RTX 5080 16GB constraint)
- DO NOT discard strippable models solely for thinking leaks

## Live-env drift
- `CODEQ_SUMMARY_MODEL` + `OLLAMA_SYNTH_MODEL` exported in `~/.zshrc`. Live Claude Code sessions don't re-source zshrc → stale export wins until relaunch. Source files correct; drift is live-env only.
