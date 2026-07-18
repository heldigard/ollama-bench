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
│   ├── classification/ closed-label macro-F1 + tiny promotion gate
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
- **`call(model, prompt, opts=None)`** is the single Ollama HTTP path. All features use it. `CallOpts` is a frozen dataclass for protocol, system, timeout, generation, context, temperature, seed, and think controls.
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

## Tiny classification promotion policy

- A tiny model is an additional low-complexity layer, never an automatic replacement for quality roles.
- Compare macro-F1 with an explicit incumbent using an absolute `0.02` tolerance.
- Require `>=3x` median end-to-end latency speedup and installed size `<=2 GiB`; report generation TPS only as a diagnostic for one-label outputs.
- Closed-set validation catches malformed output, not semantically wrong valid labels. Offline macro-F1 gates the latter; do not describe invalid-output rate as a measured live escalation rate.
- No runtime wiring is allowed until a real candidate produces an `ACCEPT` report.

## Output is regenerable (not git-tracked)

All outputs go to `~/.cache/ollama-bench/{results,logs}/`. Not in repo. `gitignore` excludes them.

## Path resolution: ABSOLUTE

`shared/paths.py` uses absolute paths from `Path.home()`. Symlinks + CWD changes don't matter (lesson learned from smart-trim `compat.py`).

## Anti-pattern: name-bias + circular quality justification (round-15, 2026-07-13)

`batiai/gemma4-e2b:q4` was wrongly demoted in smart_trim because an agent read
the `e2b` suffix as "tiny / low-fidelity" and then justified keeping the
lower-scoring SC117 with "throughput is non-decisive." Two failures compounded:

1. **Don't infer model class from a name suffix.** `e2b` = effective-2B but the
   artifact is 4.6B (PLE embeddings). Verify size via `ollama show` / model card,
   never the tag. A misclassified model inherits the wrong acceptance gate.
2. **A non-decisive criterion can't be used to discard a win on the decisive
   one.** If quality governs and model A scores higher than B, "A is also
   faster" does NOT demote A — it makes A strictly better. Invoking the
   throughput rule there inverts "quality over speed": it penalizes the model
   for an attribute that, by the rule, shouldn't count against it.

**Decision rule (durable):** promotion/demotion is driven by the score on the
governing metric. When a model wins on the governing metric, secondary metrics
(throughput, size) are reported, not used as vetoes. A single-round win is a
*caution* signal for fidelity-critical roles (smart_trim, judging) — then run a
second cross-validation round, don't reach for a non-governing metric to block it.

## 2026-07-18 — Keep installed winners; prune only via RANKING_HISTORY

- **Decision**: Installed Ollama models after a closed bench round are **kept assets**, not a cleanup backlog.
- **Why**: Roles differ (improve ≠ codeq_sum ≠ tool_call ≠ OCR). Looking similar ≠ redundant.
- **Process**: New HF candidates → smoke → deep → tie-break → update RANKING.md → only then delete losers. Never reverse-delete from disk-size heuristics.
- **Incident**: 2026-07-18 native-Ubuntu ecosystem review almost marked the winner library as prune candidates; corrected + memory banks updated.

