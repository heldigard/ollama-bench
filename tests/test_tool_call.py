"""Unit tests for the tool_call slice — JSON extraction + ground-truth scoring."""

from __future__ import annotations

from ollama_bench.features.tool_call.command import PROMPTS, _score, extract_json


def test_extract_json_plain_object():
    out = '{"tool": "get_weather", "args": {"location": "Tokyo"}}'
    obj = extract_json(out)
    assert obj == {"tool": "get_weather", "args": {"location": "Tokyo"}}


def test_extract_json_wrapped_in_prose_and_fence():
    out = 'Sure!\n```json\n{"tool": "set_timer", "args": {"minutes": 10}}\n```\nDone.'
    obj = extract_json(out)
    assert obj is not None
    assert obj["tool"] == "set_timer"


def test_extract_json_invalid_returns_none():
    assert extract_json("not json at all") is None
    assert extract_json("{broken json}}}") is None
    assert extract_json("") is None


def test_score_full_marks_on_correct_call():
    res = {
        "out": '{"tool": "get_weather", "args": {"location": "Tokyo"}}',
        "tps": 40.0,
        "etoks": 12,
        "done": "stop",
    }
    sc = _score(res, expected=("get_weather", "tokyo"))
    # +3 valid JSON, +4 (2 hits x 2), +2 tps(cap) = 9
    assert sc > 7.0


def test_score_penalizes_refusal():
    res = {"out": "As an AI, I cannot do that.", "tps": 0.0, "etoks": 0, "done": "stop"}
    sc = _score(res, expected=("get_weather", "tokyo"))
    assert sc < 0


def test_score_recovers_strippable_think_leak():
    res = {
        "out": '<think>hmm</think>{"tool": "get_weather", "args": {"location": "Tokyo"}}',
        "tps": 10.0,
        "etoks": 20,
        "done": "stop",
    }
    sc = _score(res, expected=("get_weather", "tokyo"))
    # The modern benchmark strips recoverable reasoning traces before scoring.
    assert sc > 7.0


def test_score_err_returns_sentinel():
    res = {"err": "boom"}
    assert _score(res, expected=("get_weather",)) == -100.0


def test_prompts_have_expected_substrings():
    for p in PROMPTS:
        assert "expected" in p, f"{p['id']} missing expected"
        assert isinstance(p["expected"], tuple) and len(p["expected"]) >= 2
        assert p["prompt"].strip(), f"{p['id']} has empty prompt"
