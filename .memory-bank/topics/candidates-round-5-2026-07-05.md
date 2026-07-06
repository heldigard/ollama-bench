# Round-5 Re-Bench — 2026-07-05 (Ollama 0.31.1)

> Full re-bench of all 20 LLM winners after the round-3/round-4 candidate sweeps.
> Triggered by user: "vuelve a testear todos los modelos ganadores a ver si hay
> cambios en el ranking". 2 material changes found; 3 tasks maintained (saturated).

## Pipeline

1. **smoke** (20 LLMs, 1 prompt) — 20/20 ok, 0 leaks. bge-m3 HTTP 400 (expected: embedding).
2. **deep** (20 × 8 prompts, 5 tasks) — heavy saturation (7.0) across smart_trim/web_synth/code_gen.
3. **tie-break** (13 candidates × 5 hard prompts) — revealed the e4b collapse.

## Material changes (2)

### codeq_sum: `batiai/gemma4-e4b:q4` → `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU`

- e4b collapsed in r5 hard-prompt tb: **9.00, rank #11** (was #1 with tb 11.00 in round-3).
- SetneufPT: combined **2.0** (deep #1 / 7.00, tb #3 / 11.00) — consistent across both passes.
- Likely cause: Ollama 0.31.x sampling drift on the hard summary prompt (seed=42 deterministic,
  same machine, so the regression is real, not noise).
- Side effect: SetneufPT now holds BOTH smart_trim #1 AND codeq_sum #1. Acceptable — e4b
  previously held codeq_sum + web_synth (2 roles), so role concentration is symmetric.

### web_synth: `batiai/gemma4-e4b:q4` → `jaahas/crow:9b`

- e4b collapsed in r5 hard-prompt tb: **5.50, rank #13** — the ONLY model below the 10.50
  saturation tier (failed the discrepancy-surfacing hard prompt: did not flag the [2] vs [3]
  contradiction).
- crow:9b: combined **2.5** (deep #2 / 7.00, tb #3 / 10.50). tb saturated for 12/13 candidates;
  crow wins on deep_rank + non-collapse.
- Note: web_synth tb is saturated (10.50 × 12) — the #2-#5 ordering is soft. Only the e4b
  collapse + crow's deep #2 are clear signal.

## Maintained (3 — saturated, no real signal beyond incumbents)

### improve: `hf.co/kai-os/Grug-12B-GGUF:Q4_K_M` stays #1

- Combined-rank arithmetic puts SetneufPT #1 (comb 3.5) above Grug (comb 4.0), BUT that's
  misleading: deep is saturated near 4.0, and **Grug's tb (8.35) is 2× SetneufPT's (4.27)**.
- Tie-break is the discrimination pass; Grug wins it clearly. Round-3 decision holds.

### smart_trim: `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` stays #1

- BOTH deep (7.0) and tb (10.50) saturate for all 13 candidates. Combined-rank is pure noise.
- SetneufPT maintained by inertia (round-3/4 decision; no counter-signal in r5).

### code_gen: `aratan/gemma-4-E4B-it-heretic:Q6_K` stays #1

- tb saturates at 16.00 for 12/13 candidates. Combined-rank noise.
- aratan maintained (round-4 decision; no counter-signal).

## Methodology lesson

Combined-rank = avg(deep_rank, tie_break_rank) **lies when one pass saturates and the other
doesn't**. When deep saturates (improve) but tb discriminates, weight tb higher. When BOTH
saturate (smart_trim, code_gen), the ranking is noise — maintain the incumbent and document
the saturation. The `test_score_saturation.py` contract locks the caps that produce this; the
discrimination strategy lives in `topics/bench-methodology.md`.

## Cross-project rewire done

| consumer | file | old → new |
|---|---|---|
| codeq | `src/codeq/shared/llm.py` (`_CODEQ_SUMMARY_MODEL`) | e4b → SetneufPT |
| codeq | `src/codeq/cli.py` (`--summary` help) | e4b → SetneufPT |
| web-research | `src/web_research/shared/config.py` (`_OLLAMA_DEFAULT_SYNTH_MODEL`) | e4b → crow:9b |
| web-research | `src/web_research/features/synthesis/engine.py` (comment) | e4b → crow:9b |
| `~/.zshrc` | `CODEQ_SUMMARY_MODEL` export | e4b → SetneufPT |
| ollama-bench | `src/ollama_bench/shared/config.py::TASKS[codeq_sum/web_synth]` | e4b → SetneufPT / crow:9b |

Tests after rewire: ollama-bench 174, codeq 71, web-research 63 — all green.

## Live-env gotcha (carried from round-3 wiring topic)

`CODEQ_SUMMARY_MODEL` is exported in `~/.zshrc`. A live Claude Code session does NOT re-source
zshrc, so the OLD export wins for every codeq subprocess until the session relaunches. Same
applies to `OLLAMA_SYNTH_MODEL`. After this commit, relaunch any long-running session that
depends on codeq/web-research to pick up the new defaults. The source files + zshrc are correct;
the drift is live-env only.

## Artifacts

- `~/.cache/ollama-bench/results/smoke_all.tsv` (round-5)
- `~/.cache/ollama-bench/results/deep_r5.{tsv,md}`
- `~/.cache/ollama-bench/results/tiebreak_r5.md`
