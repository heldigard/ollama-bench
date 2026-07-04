# Reference
> Stable facts about ollama-bench — CLI, scoring, models.

## CLI Surface (10 sub-commands)

```bash
ollama-bench --version            # 0.1.0
ollama-bench --help

ollama-bench list [-o FILE]                  # installed models + warn flags
ollama-bench smoke [-m M...] [-o FILE]        # 1-prompt leak gate (skips embeddings)
ollama-bench deep [-c C...] [-t T...] [-o FILE]   # 5-task x N model
ollama-bench tie-break -w W... [-o FILE]     # re-bench tied candidates (hard prompts)
ollama-bench bug-finding -m M... [-o FILE]   # diff-review task (count bugs found)
ollama-bench lfm-variant [-v V...] [-o FILE]  # codeq summary for LFM family (think-strip)
ollama-bench multi-domain [-m M] [-o FILE]    # legacy 4-domain
ollama-bench judge score -i IN [-o OUT]      # LLM-as-judge
ollama-bench embedding eval -m M             # embedding model eval
ollama-bench report build [-i IN] [-o OUT]   # TSV -> MD ranking
```

## Canonical 6 tasks

| task | budget_words | PRIMARY (re-bench 2026-07-04) |
|---|---|---|
| improve | 120 | hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl |
| codeq_sum | 30 | batiai/gemma4-e4b:q4 |
| smart_trim | 150 | SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU |
| web_synth | 200 | batiai/gemma4-e4b:q4 |
| code_gen | 100 | fredrezones55/Qwopus3.5:9b |
| bug_finding | — | cryptidbleh/gemma4-claude-sonnet-4.6 |

Full top-2 map + 16-winner rationale: `topics/local-ollama-lineup.md`.

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

- `OLLAMA_0_23_INCOMPAT_MODELS`: **empty** (was the stale 0.23.2 binary, not the models; resolved by upgrade to 0.31.1).
- `LEAKY_THINK_MODELS_SUBSTR`: tuple of substrings matching models known to leak thinking despite think=False (LFM family — model-inherent, persists on every Ollama version).

## Output paths (shared/paths.py)

- `result_path(name, ext='tsv')` → `~/.cache/ollama-bench/results/<name>.<ext>`
- `log_path(name)` → `~/.cache/ollama-bench/logs/<name>.log`
- Unsafe names (`..`, `/`) are rejected.

## Ollama API call (shared/ollama.py)

- `CallOpts` dataclass: timeout, num_predict, num_ctx, temperature, think (TOP-LEVEL)
- `call(model, prompt, opts=None)` → dict with dt/tps/etoks/ptoks/len/done/out/err
- 8-param call refactored to 3-param (model, prompt, opts) — `vertical-slice-guard` rule.
- **`think` is TOP-LEVEL in the request body** (not inside `options`). Putting it inside `options` is silently ignored — qwen3.x + gemma4 still emit the thinking trace.

## Quant rule (verified 2026-07-04)

Q4_K_M is the quality ceiling for gemma4-e4b/e2b and qwen3.5:4b. Higher quants (Q5/Q6/Q8) add weight + latency WITHOUT quality gain, sometimes strictly worse (non-monotonic). Do not pull Q8 variants of existing Q4 winners. See `topics/quant-comparison-2026-07-04.md`.