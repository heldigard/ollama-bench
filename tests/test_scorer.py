"""Unit tests for shared.scorer — leak detection, scoring, strip_think."""

from __future__ import annotations

from ollama_bench.shared.scorer import (
    detect_leaks,
    first_pass_score,
    leak_policy,
    leaks_are_strippable,
    prepare_scored_response,
    quality_score,
    strip_reasoning,
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


def test_detect_leaks_reasoning_trace_tags():
    # Structured-reasoning trace tags from thinking-models (Qwen3/DeepSeek/GPT-OSS).
    assert "reasoning_tag" in detect_leaks("<reasoning>step 1</reasoning>")
    assert "reflection_tag" in detect_leaks("<reflection>hmm</reflection>")
    assert "output_tag" in detect_leaks("<output>final</output>")


def test_detect_leaks_refusal_variants():
    assert "refusal_pattern" in detect_leaks("As a language model, I...")
    assert "refusal_pattern" in detect_leaks("I'm just an AI, I can't know")
    assert "refusal_pattern" in detect_leaks("I'm unable to access that")
    assert "refusal_pattern" in detect_leaks("I am unable to comply")


def test_detect_leaks_clean_summary_no_false_positive():
    # A legitimate code summary must NOT trip the gate.
    clean = (
        "Sends a trimmed chat message to the API; clears the draft and surfaces "
        "errors to the error ref. Returns nothing."
    )
    assert detect_leaks(clean) == []


def test_strip_think_matched_pair():
    assert strip_think("<think>think</think>actual answer") == "actual answer"


def test_strip_think_orphan():
    assert strip_think("<think>orphan thinking content") == ""


def test_strip_think_no_think():
    assert strip_think("plain answer") == "plain answer"


def test_strip_reasoning_removes_all_trace_tags():
    raw = "<think>plan</think><reasoning>step</reasoning>actual <output>answer</output>"
    assert strip_reasoning(raw) == "actual answer"


def test_strip_reasoning_orphan_tags():
    # Orphan (no closing tag) must still be stripped to end-of-string.
    assert strip_reasoning("<think>thinking...") == ""
    assert strip_reasoning("<reasoning>still reasoning") == ""


def test_strip_reasoning_unwraps_output_only():
    # <output> wrapper unwraps (keeps content); not treated as a leak to drop.
    assert strip_reasoning("<output>keep me</output>") == "keep me"


def test_strip_reasoning_visible_prefix_with_final_answer():
    raw = "Thinking Process: inspect options.\nFinal Answer: BUG: mutable default"
    assert strip_reasoning(raw) == "BUG: mutable default"


def test_strip_reasoning_visible_prefix_without_answer_drops_trace():
    assert strip_reasoning("Let me think: only private reasoning") == ""


def test_strip_reasoning_idempotent_on_clean():
    clean = "A normal summary with no tags at all."
    assert strip_reasoning(clean) == clean


def test_leaks_are_strippable_true_for_thinking_only():
    assert leaks_are_strippable(["think_tag", "reasoning_tag"]) is True
    assert leaks_are_strippable(["thinking_process"]) is True


def test_leaks_are_strippable_false_for_refusal():
    # Refusal leak present → not salvageable by stripping.
    assert leaks_are_strippable(["think_tag", "refusal_pattern"]) is False


def test_leaks_are_strippable_false_for_empty():
    assert leaks_are_strippable([]) is False


def test_leak_policy_classifies_strip_required_only_when_recoverable():
    assert leak_policy("<think>plan</think>final") == "strip_required"
    assert leak_policy("Thinking Process: private only") == "unsafe"
    assert leak_policy("As an AI, I cannot") == "unsafe"
    assert leak_policy("plain answer") == "clean"


def test_prepare_scored_response_strips_recoverable_trace():
    res, meta = prepare_scored_response({"out": "<think>x</think>final", "tps": 1})
    assert res["out"] == "final"
    assert meta["policy"] == "strip_required"


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
    sc = tie_break_score(
        res, lambda o: structural_score(o, expected_sections=("## GOAL",)), budget=120
    )
    assert sc > 2.0


def test_tie_break_score_empty_penalized():
    res = {"out": "", "tps": 0.0, "etoks": 0, "done": "stop"}
    sc = tie_break_score(res, lambda o: 0.0, budget=120)
    assert sc < 0
