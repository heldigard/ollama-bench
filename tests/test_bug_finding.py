"""Unit tests for bug_finding slice."""
from __future__ import annotations

from ollama_bench.features.bug_finding.command import (
    PROMPTS,
    _count_hits,
    _score,
)


def test_prompts_have_diffs():
    assert len(PROMPTS) >= 2
    for p in PROMPTS:
        assert "id" in p
        assert "n_bugs" in p
        assert "expected" in p
        assert "prompt" in p
        assert p["n_bugs"] >= 1


def test_count_hits_basic():
    out = "found mutable default and off-by-one and SQL injection"
    expected = ("mutable default", "off-by-one", "sql injection", "race", "lock")
    assert _count_hits(out, expected) == 3


def test_count_hits_case_insensitive():
    out = "Found MUTABLE DEFAULT"
    assert _count_hits(out, ("mutable default",)) == 1


def test_count_hits_empty():
    assert _count_hits("", ("any",)) == 0


def test_count_hits_grouped_synonyms_count_one_bug_once():
    out = "This has a race because there is no lock"
    expected = (("race", "lock"), ("sql injection", "execute"))
    assert _count_hits(out, expected) == 1


def test_score_clean_with_hits():
    res = {"out": "BUG: mutable default BUG: off-by-one COUNT: 2",
           "tps": 30.0, "etoks": 20, "done": "stop"}
    sc = _score(res, n_bugs=2, expected=("mutable default", "off-by-one"))
    assert sc > 2.0


def test_score_err():
    assert _score({"err": "x"}, 2, ("a",)) == -100.0


def test_score_recovers_strippable_leak():
    res = {"out": "<think>thinking</think>BUG: mutable default COUNT: 1",
           "tps": 30.0, "etoks": 20, "done": "stop"}
    sc = _score(res, 1, (("mutable default",),))
    assert sc > 10


def test_score_unsafe_leak_penalized():
    res = {"out": "Thinking Process: private only", "tps": 30.0, "etoks": 20, "done": "stop"}
    sc = _score(res, 1, (("mutable default",),))
    assert sc < 0
