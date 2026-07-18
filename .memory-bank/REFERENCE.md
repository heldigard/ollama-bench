# Reference
> Stable facts about ollama-bench — CLI, scoring, models.

## CLI Surface (14 sub-commands)

```bash
ollama-bench --version            # 0.1.0
ollama-bench --help

ollama-bench list [-o FILE]                  # installed models + warn flags
ollama-bench smoke [-m M...] [-o FILE]        # 1-prompt leak gate (skips embeddings)
ollama-bench deep [-c C...] [-t T...] [-o FILE]   # 5-task x N model
ollama-bench tie-break -w W... [-o FILE]     # re-bench tied candidates (hard prompts)
ollama-bench bug-finding -m M... [-o FILE]   # diff-review task (count bugs found)
ollama-bench tool-call -m M... [-o FILE]     # structured JSON tool-call (ground-truth)
ollama-bench browser-tool -m M... [-o FILE]  # ref-grounded a11y action (snap+ref)
ollama-bench pdf-extract -m M... [-o FILE]   # schema field extraction + abstention
ollama-bench embedding-retrieval [-m M]      # embedding MRR + recall@5 (ground-truth)
ollama-bench lfm-variant [-v V...] [-o FILE]  # codeq summary for LFM family (think-strip)
ollama-bench multi-domain [-m M] [-o FILE]    # legacy 4-domain
ollama-bench judge score -i IN [-o OUT]      # LLM-as-judge
ollama-bench embedding eval -m M             # embedding model eval
ollama-bench report build [-i IN] [-o OUT]   # TSV -> MD ranking
```

## Canonical 6 tasks

| task | budget_words | PRIMARY (re-bench 2026-07-12 round-10) |
|---|---|---|
| improve | 120 | hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M |
| codeq_sum | 30 | hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M |
| smart_trim | 150 | batiai/gemma4-e2b:q4 |
| web_synth | 200 | hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M |
| code_gen | 100 | hf.co/prithivMLmods/lift-GGUF:Q4_K_M |
| bug_finding | — | xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0 |

Full top-2 map + per-task champions + rationale: `topics/local-ollama-lineup.md`.
**NOTE**: REFERENCE.md previously held stale round-7 snapshot. Round-10 cross-task
validation generalized round-9's lesson: stale champions are vulnerable to other-task
challengers. TeichAI now improve + web_synth; batiai-e2b smart_trim (round-15 correction); xentriom bug_finding.

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

## Installed library = winners (agent rule, 2026-07-18)

- The live `ollama list` set on this host **is** the bench winner lineup (top-N union + PRIMARY/FALLBACK from `RANKING.md`).
- Size (~109 GiB / ~23 tags) is expected for multi-role coverage on RTX 5080 16 GB.
- **Agents must not recommend pruning** “similar” Gemma-4 / Claude-distill tags after ecosystem audits. Losers are already gone (`RANKING_HISTORY.md`).
- Cross-host runtime maps: `~/.config/dev/ollama-roles.json`, home `topics/local-ollama-lineup.md`.
- Authoritative table: repo root `RANKING.md` (not stale memory tables from 2026-07-04).

