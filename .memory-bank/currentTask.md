# Current Task
> 2026-07-08: New model bench complete. Consumer rewires pending.

## Completed (this session)
- Deep bench (14 models, --strip): results_current_models_strip_deep_20260708.tsv
- Specialized benches: tool_call, pdf_ocr, pdf_extract, bug_finding
- RANKING.md updated with new winners
- config.py updated (TASKS + SPECIALIZED_TASKS)
- Memory bank updated (local-ollama-lineup, harness-wiring)
- All 185 tests passing

## Pending consumer rewires
- ~/prompt-improve: improve chain → OmniCoder primary
- ~/smart-trim: smart_trim → Openclaw primary
- ~/web-research: web_synth → DeltaCoder primary
- ~/.claude/scripts/diff-review.py: bug_finding → DeltaCoder

## Latest Durable State
- New champions: Openclaw (smart_trim, code_gen), DeltaCoder (web_synth, bug_finding), OmniCoder (improve)
- SetneufPT demoted from improve #1 to #8; still codeq_sum #2
- DeepSeek-V4-Flash: strippable but last everywhere — not recommended
- lift: pdf_ocr fallback (11.12, 112 tok/s)

## When a new task surfaces
- **New fine-tune to evaluate** → `ollama-bench candidates <model...>` or `smoke` + `deep`.
- **New task type** → add `features/<slice>/` + register in `cli.py::_SLICES` + tests.
- **Ollama upgrade** → re-run `ollama-bench smoke` and at least canonical `deep`.
- **Reasoning leak model** → do not hard-drop if `strippable=1`; benchmark with cleaned output and record runtime handling.
