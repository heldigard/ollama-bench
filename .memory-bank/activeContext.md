# Active Context
> 2026-07-08 (PM, late): IDLE. Round-8 closed. Lineup stable at 22.

## Current state

- **No active objective.** Round-7 (full pipeline + consumer rewire) and round-8
  (4-candidate sweep, all rejected) both shipped and pushed this session.
- **Lineup:** 19 LLM + 3 embeddings = 22 models (top-5 union per role).
- **All 7 consumer repos + ollama-bench:** clean (`dirty=0`, `ahead=0`), pushed.

## Last session actions (2026-07-08 PM, late)

- Round-8: pulled + benched 4 NEW HF candidates (shuhulx Qwopus-Fable5, tvall43 Qwen3.6-14B-A3B
  MoE, llmfan46 composer2.5-v2 Q4, KevinJK51 Thinking-V2). All 4 lost vs round-7 champions → deleted.
- Recorded rejects + 4 durable learnings in RANKING_HISTORY.md §round-8 + topics/local-ollama-lineup.md.
- Updated currentTask + progress to round-8-closed state.

## Champions (round-7 combined — unchanged by round-8)

improve+bug_finding=OmniCoder · codeq_sum=batiai/gemma4-e4b:q4 · smart_trim=HauhauCS-Balanced ·
web_synth=TeichAI/Fable-5-v1 · code_gen=lift · tool_call+pdf_extract+browser=SetneufPT/Qwopus3.5-4B-MTP ·
pdf_ocr=Unlimited-OCR · embed=embeddinggemma · infra-default=cryptidbleh/gemma4-claude-opus-4.6

## Negative constraints (GPU-safe — preserved)

- DO NOT re-introduce parallel pools (ThreadPoolExecutor) — GPU overheat root cause.
- DO NOT run benches without `--cooldown`/`--temp-limit`.
- DO NOT pull Q5/Q6/Q8 of existing Q4 winners; DO NOT install >10GB models (RTX 5080 16GB).
  (xentriom Q8 is the single justified exception — holds web_synth #3.)
- DO NOT discard strippable models solely for thinking leaks.
- DO NOT re-pull round-8 rejects (shuhulx, tvall43, llmfan46, KevinJK51) — see RANKING_HISTORY §round-8.

## Next session entry point

Resume only if: a genuinely new base/fine-tune appears (not another Fable5/composer2.5 finetune
of Qwen3.5-9B / Qwopus3.5-4B / gemma-4-12B), or a coder-tuned Qwen3.6-14B-A3B MoE drops. Otherwise
the lineup is stable.
