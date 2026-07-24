"""Unit tests for the browser_tool slice — JSON extraction + ref-grounding score."""

from __future__ import annotations

from ollama_bench.features.browser_tool.command import (
    CASES,
    KNOWN_ACTIONS,
    _score,
    extract_json,
    refs_in_snapshot,
)


def test_extract_json_plain_object():
    obj = extract_json('{"action": "click", "ref": "e3"}')
    assert obj == {"action": "click", "ref": "e3"}


def test_extract_json_wrapped_in_prose_and_fence():
    out = 'Sure!\n```json\n{"action": "fill", "ref": "e5"}\n```\nDone.'
    obj = extract_json(out)
    assert obj is not None
    assert obj["action"] == "fill"


def test_extract_json_invalid_returns_none():
    assert extract_json("not json") is None
    assert extract_json("{broken}}}") is None
    assert extract_json("") is None


def test_refs_in_snapshot_extracts_en_tokens():
    snap = "- e3: link 'Login'\n- e11: region 'Comments'\nno other ref here"
    assert refs_in_snapshot(snap) == {"e3", "e11"}


def test_cases_have_expected_ref_in_snapshot_or_none():
    """Each expected_ref must actually exist in that case's snapshot (or be None)."""
    for c in CASES:
        if c["expected_ref"] is not None:
            assert c["expected_ref"] in refs_in_snapshot(c["snapshot"]), (
                f"{c['id']} expected_ref not in snapshot"
            )
        assert c["expected_action"] in KNOWN_ACTIONS, f"{c['id']} expected_action not known"


def test_score_full_marks_on_grounded_call():
    case = next(c for c in CASES if c["id"] == "click_link")
    res = {"out": '{"action": "click", "ref": "e3"}', "tps": 40.0, "etoks": 12, "done": "stop"}
    sc = _score(res, case)
    # +3 JSON, +3 known action, +2 grounded ref, +1 == expected ref, +2 tps(cap) = 11
    assert sc == 11.0


def test_score_penalizes_hallucinated_ref():
    """A ref NOT in the snapshot loses the ref points (hallucination)."""
    case = next(c for c in CASES if c["id"] == "click_link")  # snapshot has e1-e4, not e99
    res = {"out": '{"action": "click", "ref": "e99"}', "tps": 40.0, "etoks": 12, "done": "stop"}
    sc = _score(res, case)
    # +3 JSON, +3 known action, +0 (e99 not grounded), +2 tps = 8
    assert sc == 8.0


def test_score_no_ref_action_rewarded_when_url_inlined():
    case = next(c for c in CASES if c["id"] == "open_url_no_ref")
    res = {"out": '{"action": "navigate", "ref": "null"}', "tps": 40.0, "etoks": 10, "done": "stop"}
    sc = _score(res, case)
    # +3 JSON, +3 known action (navigate ∈ NO_REF), +3 correct no-ref, +2 tps = 11
    assert sc == 11.0


def test_score_penalizes_refusal():
    res = {"out": "As an AI, I cannot click that.", "tps": 0.0, "etoks": 0, "done": "stop"}
    sc = _score(res, CASES[0])
    assert sc < 0


def test_score_err_returns_sentinel():
    assert _score({"err": "boom"}, CASES[0]) == -100.0
