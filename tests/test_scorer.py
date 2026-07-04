"""Unit tests for shared.scorer — leak detection, scoring, strip_think."""
from __future__ import annotations

from ollama_bench.shared.scorer import (
    detect_leaks,
    first_pass_score,
    quality_score,
    strip_think,
    structural_score,
    tie_break_score,
)


def test_detect_leaks_empty_input():
    assert detect_leaks("") == []
    assert detect_leaks(None) == []  # type: ignore[arg-type]


def test_detect_leaks_think_tag():
    assert "think_tag" in detect_leaks("<think>hello</think>")
    assert "think_tag" in detect_leaks("<think>orphan")


def test_detect_leaks_thinking_process():
    assert "thinking_process" in detect_leaks("Thinking Process: 1. Foo")


def test_detect_leaks_refusal():
    assert "refusal_pattern" in detect_leaks("I'm sorry, but as an AI...")
    assert "refusal_pattern" in detect_leaks("I cannot help with that")


def test_strip_think_matched_pair():
    assert strip_think("<think>think</think>actual answer") == "actual answer"


def test_strip_think_orphan():
    assert strip_think("<think>orphan thinking content") == ""


def test_strip_think_no_think():
    assert strip_think("plain answer") == "plain answer"


def test_structural_score_sections():
    out = "## GOAL\n## STEPS\n## ACCEPTANCE"
    assert structural_score(out, expected_sections=("## GOAL", "## STEPS", "## ACCEPTANCE")) == 6.0
    assert structural_score("nothing", expected_sections=("## GOAL",)) == 0.0


def test_quality_score_keywords():
    out = "def function(): return value"
    assert quality_score(out, keywords=("def", "function", "return")) == 6.0


def test_first_pass_score_clean_fast():
    res = {"out": "hi there", "tps": 30.0, "etoks": 5, "done": "stop"}
    sc = first_pass_score("any", res, budget=120)
    assert sc > 0  # at least tps bonus


def test_first_pass_score_err():
    res = {"err": "boom"}
    assert first_pass_score("any", res, budget=120) == -100.0


def test_tie_break_score_with_scorer():
    res = {"out": "## GOAL x", "tps": 30.0, "etoks": 5, "done": "stop"}
    sc = tie_break_score(res, lambda o: structural_score(o, expected_sections=("## GOAL",)), budget=120)
    assert sc > 2.0


def test_tie_break_score_empty_penalized():
    res = {"out": "", "tps": 0.0, "etoks": 0, "done": "stop"}
    sc = tie_break_score(res, lambda o: 0.0, budget=120)
    assert sc < 0
