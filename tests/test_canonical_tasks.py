"""Unit tests for canonical task cases and scorers."""
from __future__ import annotations

from ollama_bench.features.canonical_tasks import CANONICAL_TASKS, iter_cases, score_task_response


def test_each_canonical_task_has_multiple_cases():
    for task in CANONICAL_TASKS:
        cases = iter_cases(task)
        assert len(cases) >= 3, f"{task} should have enough cases to avoid tiny-sample ties"
        for case in cases:
            assert case["id"]
            assert case["prompt"].strip()
            assert case["anchors"]
            assert case["budget_words"] > 0


def test_codeq_sum_good_response_beats_empty_response():
    case = iter_cases("codeq_sum")[0]
    good = {
        "out": "This function skips empty or already-sending messages, clears the draft, posts chat text, and stores API errors.",
        "tps": 30.0,
        "done": "stop",
    }
    empty = {"out": "", "tps": 30.0, "done": "stop"}
    assert score_task_response("codeq_sum", good, case)["score"] > score_task_response(
        "codeq_sum", empty, case
    )["score"]


def test_score_task_response_records_strip_required_policy():
    case = iter_cases("codeq_sum")[0]
    res = {
        "out": "<think>private</think>This function posts chat text and stores API errors.",
        "tps": 30.0,
        "done": "stop",
    }
    scored = score_task_response("codeq_sum", res, case)
    assert scored["metrics"]["policy"] == "strip_required"
    assert "think_tag" in scored["metrics"]["raw_leaks"]
