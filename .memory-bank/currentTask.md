# Current Task
> 2026-07-08 (PM, late): Round-8 candidate sweep CLOSED. Lineup stable at 22. Nothing running.

## State: IDLE — no active bench, no pending rewire

Round-7 full pipeline + consumer rewire shipped earlier this session. Round-8 tested
4 NEW HF candidates against the round-7 champions — all 4 lost, deleted. Lineup stable
and well-tuned; no open work.

## Latest durable state (round-7 + round-8)

- **Lineup:** 19 LLM + 3 embeddings = 22 models. Trimmed to top-5 union per role.
- **Champions (combined deep+tiebreak):** improve+bug_finding = OmniCoder; codeq_sum =
  batiai/gemma4-e4b:q4; smart_trim = HauhauCS-Balanced; web_synth = TeichAI/Fable-5-v1;
  code_gen = lift; tool_call+pdf_extract+browser = SetneufPT/Qwopus3.5-4B-MTP; pdf_ocr =
  Unlimited-OCR; embed = embeddinggemma.
- **Infra default:** cryptidbleh/gemma4-claude-opus-4.6 (replaced qwen3.5:4b).
- **Round-8 verdict:** MoE 14B-A3B = strong generalist, no specialist-killer (re-test only
  if a CODER-tuned variant drops, not a reasoning distill). Same-base Fable5/composer2.5
  finetunes do not beat the originals. Q4-vs-Q8 gap ~1.1pt on web_synth justifies xentriom Q8.

## When a new task surfaces

- **New fine-tune to evaluate** → `ollama-bench smoke` + `deep`. Check RANKING_HISTORY.md
  §round-8 FIRST — don't re-pull rejected models (shuhulx, tvall43, llmfan46, KevinJK51)
  unless a genuinely new fine-tune/base drops.
- **Promising new architecture** → a coder-tuned Qwen3.6-14B-A3B MoE is the one untested
  bet with real champion potential. Reasoning-distill (FableVibes) already failed.
- **New task type** → add `features/<slice>/` + register in `cli.py::_SLICES` + tests.
- **Ollama upgrade** → re-run `ollama-bench smoke` + canonical `deep`.
- **Reasoning leak model** → do not hard-drop if `strippable=1`; bench with cleaned output.

## Negative constraints (GPU-safe — never violate)

- DO NOT re-introduce parallel pools (ThreadPoolExecutor) — overheat root cause. Use shared `paced()`.
- DO NOT run benches without `--cooldown`/`--temp-limit`.
- DO NOT pull >10GB models (RTX 5080 16GB) or Q5/Q6/Q8 of existing Q4 winners (xentriom Q8 is the single justified exception).
