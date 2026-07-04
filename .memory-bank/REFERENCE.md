# Reference
> Stable facts about ollama-bench — CLI, scoring, models.

## CLI Surface (9 sub-commands)

```bash
ollama-bench --version            # 0.1.0
ollama-bench --help

ollama-bench list [-o FILE]                  # installed models + warn flags
ollama-bench smoke [-m M...] [-o FILE]        # 1-prompt leak gate
ollama-bench deep [-c C...] [-t T...] [-o FILE]   # 5-task x N model
ollama-bench tie-break -w W... [-o FILE]     # re-bench tied candidates
ollama-bench lfm-variant [-v V...] [-o FILE]  # codeq summary for LFM family
ollama-bench multi-domain [-m M] [-o FILE]    # legacy 4-domain
ollama-bench judge score -i IN [-o OUT]      # LLM-as-judge
ollama-bench embedding eval -m M             # embedding model eval
ollama-bench report build [-i IN] [-o OUT]   # TSV -> MD ranking
```

## Canonical 5 tasks (TASKS dict in shared/config.py)

| task | budget_words | primary_model_default |
|---|---|---|
| improve | 120 | fredrezones55/Qwopus3.5:9b |
| codeq_sum | 30 | Librellama/gemma4:e2b-Uncensored |
| smart_trim | 150 | qwen3.5:4b |
| web_synth | 200 | batiai/gemma4-e2b:q6 |
| code_gen | 100 | qwen3.5:4b |

## Leak patterns (shared/scorer.py LEAK_PATTERNS)

- `<think>` / `</think>` → think_tag
- `thinking process[: ]` → thinking_process
- `as an ai` / `i cannot` → refusal_pattern
- `i'm having an issue` → stuck_response

## Scoring functions

- `first_pass_score(task, res, budget)` — range -10 to +10. Saturates at +7.0 for fast+clean responses.
- `tie_break_score(res, scorer, budget)` — range -10 to +15. NO saturation cap.
- `structural_score(out, expected_sections, must_have)` — 0-10 by keyword/section presence.
- `quality_score(out, keywords)` — 0-10 (2 pts per keyword).
- `strip_think(text)` — removes `<think>...</think>` (matched or orphan).
- `tps_bonus(tps, cap=3.0)` — cap=3 at tps=45.

## Ollama compat flags (shared/config.py)

- `OLLAMA_0_23_INCOMPAT_MODELS`: set of model tags that fail to load on Ollama 0.23.2
  (gemma4 Q4_0 architecture + qwen3next MTP layers).
- `LEAKY_THINK_MODELS_SUBSTR`: tuple of substrings matching models known to leak thinking
  despite think=False (LFM family).

## Output paths (shared/paths.py)

- `result_path(name, ext='tsv')` → `~/.cache/ollama-bench/results/<name>.<ext>`
- `log_path(name)` → `~/.cache/ollama-bench/logs/<name>.log`
- Unsafe names (`..`, `/`) are rejected.

## Ollama API call (shared/ollama.py)

- `CallOpts` dataclass: timeout, num_predict, num_ctx, temperature, think (TOP-LEVEL)
- `call(model, prompt, opts=None)` → dict with dt/tps/etoks/ptoks/len/done/out/err
- 8-param call refactored to 3-param (model, prompt, opts) — `vertical-slice-guard` rule.