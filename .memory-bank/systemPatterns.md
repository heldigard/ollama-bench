# System Patterns
> Architectural decisions for ollama-bench.

## Vertical-slice package (mirrors codeq + smart-trim)

```
src/ollama_bench/
├── shared/        config, paths, ollama, scorer  (infra; no feature deps)
├── features/
│   ├── smoke/        1-prompt leak gate (skips embeddings)
│   ├── deep/         5-task × N model bench
│   ├── tie_break/    re-bench tied candidates with harder prompts
│   ├── bug_finding/  diff-review task (count bugs found) — NEW 2026-07-04
│   ├── lfm_variant/  codeq summary tie-break for LFM family (think-strip)
│   ├── multi_domain/ legacy 4-domain bench (improve/compact/code/reason)
│   ├── judge/        LLM-as-judge helpers
│   ├── embedding/    embedding model evaluation
│   ├── report/       markdown ranking generation
│   └── list/         enumerate installed models + flag incompat
├── cli.py          argparse multi-command root
├── __init__.py     __version__ = "0.1.0"
└── __main__.py     `python3 -m ollama_bench`
```

## Conventions

- **One responsibility per feature folder**. Each `features/<slice>/` has minimal `__init__.py` (1-line docstring) and the actual implementation in `command.py`.
- **`shared/` never imports from `features/`** (enforced by `tests/test_layout.py`).
- **No cross-feature imports** — features talk to each other only via `shared/` (enforced by `tests/test_layout.py`).
- **`call(model, prompt, opts=None)`** is the single Ollama HTTP path. All features use it. `CallOpts` is a frozen dataclass for the 5 keyword params (timeout, num_predict, num_ctx, temperature, think).
- **`shared/scorer.py`** is the single registry for leak detection + scoring rubrics.
- **`# vs-soft-allow`** marker for cohesive end-to-end pipelines > 250 LOC. Cohesion > size.

## CLI shape

```python
# cli.py
_SLICES = [
    ("smoke", add_smoke, "1-prompt leak gate per model"),
    ("deep", add_deep, "5-task x N model bench"),
    ...
]
for slug, add_parser_fn, brief in _SLICES:
    add_parser_fn(sub, parent)
```

Adding a new slice = import its `add_parser` and append to `_SLICES`. One place to touch.

## Two-pass scoring strategy (anti-saturation)

- **first_pass_score** (smoke, deep, multi_domain) — fast, saturates at 7.0 for fast+clean responses. Use to rank quickly.
- **tie_break_score** (tie_break, lfm_variant) — slower, no cap. Structural scoring + structural keywords. Use when first_pass saturates (20+ models tie).

**Why two passes**: cost. Most models are eliminated by smoke; surviving models get deep; surviving-on-deep get re-benched with harder prompts only.

## Leak gate is FIRST

Any model that emits `<think>` / `Thinking Process:` / `As an AI` is HARD-DISQUALIFIED for the task it leaked on. Smoke applies this to every model before deep burns cycles.

## Output is regenerable (not git-tracked)

All outputs go to `~/.cache/ollama-bench/{results,logs}/`. Not in repo. `gitignore` excludes them.

## Path resolution: ABSOLUTE

`shared/paths.py` uses absolute paths from `Path.home()`. Symlinks + CWD changes don't matter (lesson learned from smart-trim `compat.py`).