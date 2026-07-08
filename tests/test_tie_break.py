"""Unit tests for tie_break slice."""

from __future__ import annotations

from ollama_bench.features.canonical_tasks import HARD_PROMPTS, iter_hard_cases
from ollama_bench.features.tie_break.command import _aggregate


def test_hard_prompts_have_items():
    """All tie-break tasks MUST have hard prompt items."""
    for task, cfg in HARD_PROMPTS.items():
        assert "items" in cfg, f"{task} missing items"
        assert "budget" in cfg, f"{task} missing budget"
        assert len(cfg["items"]) >= 2, f"{task} should have >= 2 hard prompts"


def test_hard_prompts_cover_5_tasks():
    assert set(HARD_PROMPTS.keys()) == {
        "improve",
        "codeq_sum",
        "smart_trim",
        "web_synth",
        "code_gen",
    }


def test_iter_hard_cases_returns_valid():
    """iter_hard_cases must produce normalized cases for each task."""
    for task in HARD_PROMPTS:
        cases = iter_hard_cases(task)
        assert len(cases) >= 2, f"{task}: expected >= 2 hard cases"
        for case in cases:
            assert case["id"]
            assert case["prompt"].strip()
            assert case["anchors"]
            assert case["budget_words"] > 0


def test_aggregate_no_errors():
    results = {
        "m1": {"improve": 5.0, "codeq_sum": 6.0},
        "m2": {"improve": 7.0, "codeq_sum": 4.0},
    }
    out = _aggregate(results, ["improve", "codeq_sum"])
    assert out["improve"][0][0] == "m2"
    assert out["codeq_sum"][0][0] == "m1"
