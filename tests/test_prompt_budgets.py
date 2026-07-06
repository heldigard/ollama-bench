"""Prompt-budget invariant — every bench task MUST declare a sane budget_words.

Budget drives `first_pass_score`:
  - wc <= budget        → +2 (concise)
  - wc <= budget * 1.5  → +1
  - wc >  budget * 2    → -3 (rambling)

A task with budget_words=0 makes the +2 tier unreachable and the -3 tier fire
on every 1-word response (1 > 0 * 2 = 0). Silent scoring distortion → every
model ranks identically wrong. Lock the invariant.

Also asserts deep + tie_break PROMPTS agree on which tasks exist (a task in
one but not the other is usually a copy-paste miss).
"""

from __future__ import annotations

from ollama_bench.features.deep.command import PROMPTS as DEEP_PROMPTS
from ollama_bench.features.tie_break.command import PROMPTS as TIE_BREAK_PROMPTS
from ollama_bench.shared.config import TASKS

CANONICAL_TASKS = {"improve", "codeq_sum", "smart_trim", "web_synth", "code_gen"}


# ---------------------------------------------------------------------------
# Every declared task has a sane budget
# ---------------------------------------------------------------------------


def test_config_tasks_have_budget_words():
    """Each TASKS entry MUST have budget_words, and it must be > 0."""
    for task, cfg in TASKS.items():
        assert "budget_words" in cfg, f"{task}: missing budget_words"
        budget = cfg["budget_words"]
        assert isinstance(budget, int) and budget > 0, (
            f"{task}: budget_words must be a positive int, got {budget!r}"
        )


def test_deep_prompts_have_budget_words():
    """Each deep PROMPTS entry MUST have a sane budget_words."""
    for task, cfg in DEEP_PROMPTS.items():
        assert "budget_words" in cfg, f"deep/{task}: missing budget_words"
        budget = cfg["budget_words"]
        assert isinstance(budget, int) and budget > 0, (
            f"deep/{task}: budget_words must be a positive int, got {budget!r}"
        )


def test_tie_break_prompts_have_budget():
    """Each tie_break PROMPTS entry MUST have a sane budget (tie-break uses
    done='length' + budget*2 truncation check; budget=0 → no headroom signal).
    """
    for task, cfg in TIE_BREAK_PROMPTS.items():
        assert "budget" in cfg, f"tie_break/{task}: missing budget"
        budget = cfg["budget"]
        assert isinstance(budget, int) and budget > 0, (
            f"tie_break/{task}: budget must be a positive int, got {budget!r}"
        )


# ---------------------------------------------------------------------------
# Task-set consistency across config / deep / tie_break
# ---------------------------------------------------------------------------


def test_deep_and_tie_break_cover_same_canonical_tasks():
    """deep PROMPTS + tie_break PROMPTS MUST both cover the canonical 5 tasks.

    A task in deep but missing from tie_break = the saturating tier never gets
    discrimination for that task. A task in tie_break but not deep = tie-break
    re-benches something never first-pass benched (useless).
    """
    deep_keys = set(DEEP_PROMPTS.keys())
    tie_break_keys = set(TIE_BREAK_PROMPTS.keys())
    missing_from_deep = CANONICAL_TASKS - deep_keys
    missing_from_tie_break = CANONICAL_TASKS - tie_break_keys
    assert not missing_from_deep, (
        f"deep PROMPTS missing canonical tasks: {sorted(missing_from_deep)}"
    )
    assert not missing_from_tie_break, (
        f"tie_break PROMPTS missing canonical tasks: {sorted(missing_from_tie_break)}"
    )


def test_config_tasks_match_deep_tasks():
    """shared/config.py TASKS keys MUST equal deep PROMPTS keys.

    config.py is documentary (mirrors harness wiring) but MUST stay aligned
    with the bench runner's task set. Drift = a task gets benched but never
    wired into the harness, or vice versa.
    """
    config_keys = set(TASKS.keys())
    deep_keys = set(DEEP_PROMPTS.keys())
    assert config_keys == deep_keys, (
        f"config TASKS ≠ deep PROMPTS keys.\n"
        f"  only in config: {sorted(config_keys - deep_keys)}\n"
        f"  only in deep:   {sorted(deep_keys - config_keys)}"
    )


# ---------------------------------------------------------------------------
# Budget sanity: tie-break budget > deep budget for the same task
# (hard prompts legitimately need more headroom)
# ---------------------------------------------------------------------------


def test_tie_break_budget_at_least_deep_budget():
    """Tie-break uses HARDER prompts → budget should be >= deep budget.

    If someone shrinks tie_break budget below deep, the truncation penalty
    fires unfairly on the harder task. Soft check (>= not strict >) so a tie
    is allowed when prompts happen to be similar length.
    """
    for task in CANONICAL_TASKS:
        deep_b = DEEP_PROMPTS[task]["budget_words"]
        tb_b = TIE_BREAK_PROMPTS[task]["budget"]
        assert tb_b >= deep_b, (
            f"{task}: tie_break budget ({tb_b}) < deep budget ({deep_b}). "
            "Hard prompts need >= headroom; either bump tie_break budget or "
            "shrink the prompt."
        )
