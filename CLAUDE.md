# Project: ollama-bench

`ollama-bench` — local Ollama model evaluation suite with leak gating,
multi-prompt scoring, and tie-break re-benching. Public repo:
https://github.com/heldigard/ollama-bench.

## Architecture: vertical-slice CLI package

ollama-bench is a **plain CLI** invoked on-demand. Each command family
(`smoke`, `deep`, `tie-break`, `lfm-variant`, `multi-domain`, `judge`,
`embedding`, `report`, `list`) owns its CLI behavior under
`src/ollama_bench/features/<slice>/command.py`. Shared infrastructure
(HTTP, scoring, paths, config) lives in `src/ollama_bench/shared/`.

```
src/ollama_bench/
  shared/        config, paths, ollama, scorer (infra; no feature deps)
  features/
    smoke/        1-prompt leak gate (per-model fast filter)
    deep/         5-task × N model bench
    tie_break/    re-bench tied candidates with harder prompts
    lfm_variant/  codeq summary tie-break for LFM family (think-strip)
    multi_domain/ legacy 4-domain bench (improve/compact/code/reason)
    judge/        LLM-as-judge helpers (LLM scoring rubric)
    embedding/    embedding model evaluation
    report/       ranking markdown generation
    list/         enumerate installed models
```

## Conventions

- **One responsibility per feature folder** (cohesion > size). `vs-soft-allow`
  marker for cohesive pipelines > 250 LOC.
- `shared/` modules never import from `features/` (one direction).
- Cross-feature imports go through `shared/`, never feature→feature.
- All HTTP calls go through `shared/ollama.call()` (single path, leak-safe).
- All scoring goes through `shared/scorer.score_*()` (single rubric registry).

## CLI shape

```bash
ollama-bench list                    # installed models (ollama list wrapper)
ollama-bench smoke [-m M]            # 1-prompt leak gate per model
ollama-bench deep [--tasks ...]      # 5-task × N model bench
ollama-bench tie-break --winners W   # re-bench tied candidates (harder prompts)
ollama-bench lfm-variant             # codeq summary tie-break for LFM family
ollama-bench multi-domain [-m M]     # legacy 4-domain bench (improve/compact/code/reason)
ollama-bench judge score --input F   # LLM-as-judge scoring
ollama-bench embedding eval [-m M]   # embedding model benchmark
ollama-bench report build            # markdown ranking from TSV
```

## Critical constraints (regression risks)

1. **`think=False` is TOP-LEVEL in Ollama API** (NOT inside `options`). Putting
   it inside `options` is silently ignored — qwen3.x + gemma4 still emit the
   thinking trace in the response field. `shared/ollama.call()` enforces this.
2. **Leak gate first**: any model that produces `<think>`, `Thinking Process:`,
   `As an AI`, or empty string with non-zero eval_count is HARD-DISQUALIFIED for
   the task it leaked on. `shared/scorer.detect_leaks()` is the gate.
3. **Ollama 0.23.2 incompat** with gemma4 Q4_0 + qwen3next MTP + LFM (think leak).
   See `topics/ollama-0.23.2-gemma4-q4_0-incompat.md`. `report build` flags these
   when listing models.
4. **Score saturation trap**: a per-task cap-of-7.0 score makes 20+ models tie
   unhelpfully. `tie_break` uses HARDER prompts + STRUCTURAL scoring (no cap)
   to discriminate — see `topics/bench-methodology.md`.

## Commands

- Install (dev): `pip install -e ~/ollama-bench`
- Test: `python3 -m pytest tests/ -q`
- Layout gate: `python3 -m pytest tests/test_layout.py -q` (one command.py per
  feature; shared/ never imports features/)
- Lint: `ruff check .` · Format: `ruff format --check .`

## Workflow

- New bench/feature → failing test in `tests/test_<slice>.py` first, then implement.
- Before editing a slice → `codeq refs <name>` (call sites across package).
- After changes → `pytest tests/ -q` + `ruff check .`.
- Register durable decisions in `.memory-bank/systemPatterns.md`.

## Things that look wrong but aren't

- `report/` has no command.py yet — it builds from TSV, lives in
  `shared/report_builder.py` until a `cmd_report` exists. Will split when ≥2
  report formats need separate code paths.
- `embedding/` only has eval scaffolding — the real eval still lives in
  `~/.claude/scripts/ollama-summarize.py` (separate consumer).
- `docs/history/` contains 30+ deprecated bench scripts. They are NOT in the
  CLI; kept for git history of model evaluations.