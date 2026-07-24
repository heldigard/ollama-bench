"""Unit tests for judge slice."""

from __future__ import annotations

from ollama_bench.features.judge.command import FAIL_PATTERNS, judge_quality


def test_judge_clean_improve():
    out = "## GOAL\n## STEP\n## FILE\n## ACCEPTANCE"
    v = judge_quality("improve", out)
    assert v["score"] > 0.5
    assert not v["failures"]


def test_judge_refusal_penalized():
    out = "I'm sorry, but as an AI language model I cannot help."
    v = judge_quality("improve", out)
    assert v["failures"]
    assert v["score"] < 1.0


def test_judge_stub_penalized():
    out = "TODO: write code here (placeholder)"
    v = judge_quality("code_gen", out)
    assert v["failures"]


def test_judge_unfilled_template():
    out = "Hello ${user} world"
    v = judge_quality("improve", out)
    assert "unfilled_template" in v["failures"]


def test_fail_patterns_nonempty():
    assert len(FAIL_PATTERNS) >= 3
