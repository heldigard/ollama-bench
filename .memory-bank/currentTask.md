# Current Task
> 2026-07-18: **IDLE** — lineup = bench winners (keep). Champions below supersede older “TeichAI improve / Qwythos codeq” lines in this file.

## Champions (RANKING.md round-17/18, authoritative)

- improve = **cryptidbleh**/gemma4-claude-opus-4.6 · codeq_sum = **TeichAI** Fable-5-v1 (Qwythos fallback) · smart_trim = **batiai-e2b** · web_synth = TeichAI · code_gen = **lift** · bug_finding = **OmniCoder** (xentriom fallback) · tool_call/browser/pdf_extract = **SetneufPT** · pdf_ocr = Unlimited-OCR · embed = embeddinggemma.
- **Agent rule:** do not propose pruning the installed library; see REFERENCE iron rule 2026-07-18.

---
> 2026-07-12 (PM, very late): Round-12 CLOSED + cleanup pass applied. **Lineup 24 models TERMINAL STABILITY.** Cross-CLI rewire all done. Drift guard hardened. Dead code removed.

## State: IDLE — lineup CLOSED (round-12 terminal stability); cross-CLI rewire ALL APPLIED 2026-07-12 PM

## Latest durable state (round-12 cleanup pass 2026-07-12 PM)

- **Lineup:** 19 LLM + 3 embeddings = 22 models (round-13 purge 2026-07-12: deleted Librellama/gemma4-e2b-Uncensored + hf.co/unsloth/gemma-4-12b-it-qat — both not in any task top-5).
- **Champions:** improve = TeichAI · codeq_sum = Qwythos · smart_trim = batiai-e2b ·
  web_synth = TeichAI (multi-task) · code_gen = lift · bug_finding = xentriom Q8_0 ·
  tool_call + browser_tool + pdf_extract = SetneufPT · pdf_ocr = Unlimited-OCR ·
  embed = embeddinggemma.
- **Multi-task:** TeichAI (improve + web_synth), xentriom Q8_0 (bug_finding + web_synth fallback).
- **Cross-CLI rewire complete:** ~/prompt-improve (192/192 tests), ~/smart-trim (170/170 tests), ~/.claude/scripts/diff-review.py (OLLAMA_CODE_MODEL=xentriom).
- **Internal hygiene:** drift guard extended with `tertiary_model` sync check; dead `paths.py::log_path` removed; `__pycache__` cleaned across src/; codescan found no actionable findings beyond legacy cruft.

## Round-12 + cleanup verdict

Lineup at TERMINAL STABILITY (rounds 11/12 zero rewires). All plausible
architectures exhausted (no coder-MoE 14B-A3B on HF, gemma-4-26B-A4B MoE loses
on quality + latency, official QAT ties community heretic, cross-task
challengers exhausted). Manual-only improvement opportunities also exhausted.
Adopt TRIGGERED re-bench policy indefinitely.

## When a new task surfaces (TRIGGERED re-bench only)

- **External trigger → re-bench**: new HF candidate matching the gap (coder-MoE
  14B-A3B, new base family, novel architecture).
- **Ollama major upgrade** → re-run `ollama-bench smoke` + canonical `deep` on
  installed lineup; watch for sampling drift.
- **Quarterly** (scheduled): full 5-task re-bench on existing lineup, watch for model drift.
- **Annual** (full sweep): re-test ALL installed models including previous-round losers.
- **DO NOT** run unprompted re-bench cycles. Each costs ~1.5h GPU + ~30min memory-bank
  work. Stable lineup means wasted cycles return zero rewires.

## Strategic recommendation — reduce re-bench cadence

| cadence | trigger |
|---|---|
| Triggered (immediate) | new HF candidate that matches the gap, OR Ollama 0.32+ resolves the gemma-4-oficial pull blocker |
| Quarterly | model-drift watch on installed lineup |
| Annual | full sweep including previously-deleted models (drift detection) |

## Negative constraints (GPU-safe — never violate)

- DO NOT re-introduce parallel pools (ThreadPoolExecutor) — overheat root cause. Use shared `paced()`.
- DO NOT run benches without `--cooldown`/`--temp-limit`.
- DO NOT pull >10GB models (RTX 5080 16GB) or Q5/Q6/Q8 of existing Q4 winners (xentriom Q8_0 is the single justified exception; tradeoff noted in diff-review.py:12GB warning).
- DO NOT skip cross-task validation when adding a new candidate to a single task — pattern from round-10.
- **DO NOT run periodic re-bench without external trigger.** Local optimum confirmed.