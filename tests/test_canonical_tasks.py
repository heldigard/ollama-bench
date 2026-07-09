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
            assert case["weight"] > 0


def test_codeq_sum_good_response_beats_empty_response():
    case = iter_cases("codeq_sum")[0]
    good = {
        "out": "This function skips empty or already-sending messages, clears the draft, posts chat text, and stores API errors.",
        "tps": 30.0,
        "done": "stop",
    }
    empty = {"out": "", "tps": 30.0, "done": "stop"}
    assert (
        score_task_response("codeq_sum", good, case)["score"]
        > score_task_response("codeq_sum", empty, case)["score"]
    )


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


def test_grounded_improve_case_penalizes_invented_stack_and_files():
    case = next(c for c in iter_cases("improve") if c["id"] == "improve_grounded_ranking")
    grounded = {
        "out": (
            "## Goal\nReview ~/ollama-bench/ and reconcile the role-specific "
            "ranking: batiai/gemma4-e4b:q4 versus stale jaahas/crow:9b evidence."
        ),
        "tps": 30.0,
        "done": "stop",
    }
    invented = {
        "out": (
            "## Goal\nImplement the fix in Golang, run codescan, inspect .env "
            "and config.yaml, then use ollama run to find the active model."
        ),
        "tps": 30.0,
        "done": "stop",
    }
    good = score_task_response("improve", grounded, case)
    bad = score_task_response("improve", invented, case)
    assert good["score"] > bad["score"] + 10
    assert good["metrics"]["preserve_hits"] == 4
    assert bad["metrics"]["forbidden_hits"] >= 5


def test_speed_is_only_a_small_quality_tiebreaker():
    case = iter_cases("codeq_sum")[0]
    response = "This function posts chat text, skips empty input, and stores API errors."
    slow = score_task_response("codeq_sum", {"out": response, "tps": 1.0, "done": "stop"}, case)
    fast = score_task_response("codeq_sum", {"out": response, "tps": 100.0, "done": "stop"}, case)
    assert 0 <= fast["score"] - slow["score"] <= 0.25


def test_codeq_contract_accepts_semantic_alternatives_and_rejects_missing_branch():
    case = next(c for c in iter_cases("codeq_sum") if c["id"] == "sum_stale_cache")
    precise = {
        "out": "Loads remotely, returning the cached value on failure if available and otherwise rethrows the error.",
        "tps": 30.0,
        "done": "stop",
    }
    misleading = {
        "out": "Loads remotely and returns stale cached data on failure instead of propagating the error.",
        "tps": 30.0,
        "done": "stop",
    }
    good = score_task_response("codeq_sum", precise, case)
    bad = score_task_response("codeq_sum", misleading, case)
    assert good["metrics"]["alternative_hits"] == 3
    assert bad["metrics"]["missing_alternatives"] >= 2
    assert good["score"] > bad["score"] + 7


def test_improve_unknown_context_penalizes_turning_task_into_user_question():
    case = next(c for c in iter_cases("improve") if c["id"] == "improve_unknown_context")
    bounded = {
        "out": "## Goal\nDo not guess. Locate evidence and verify available context before defining the task.",
        "tps": 30.0,
        "done": "stop",
    }
    asks_user = {
        "out": "Please provide the missing context and share these details so I can identify the task.",
        "tps": 30.0,
        "done": "stop",
    }
    good = score_task_response("improve", bounded, case)
    bad = score_task_response("improve", asks_user, case)
    assert good["score"] > bad["score"] + 10


def test_improve_penalizes_unprompted_files_and_stack_choices():
    case = next(c for c in iter_cases("improve") if c["id"] == "improve_auth_flake")
    grounded = {
        "out": "## Goal\nReproduce the password-reset login failure and verify the session and token behavior.",
        "tps": 30.0,
        "done": "stop",
    }
    invented = {
        "out": "## Goal\nEdit auth_service.py, add Redis, Docker, and PostgreSQL, then change config.yaml.",
        "tps": 30.0,
        "done": "stop",
    }
    good = score_task_response("improve", grounded, case)
    bad = score_task_response("improve", invented, case)
    assert bad["metrics"]["unprompted_files"] == 2
    assert bad["metrics"]["unprompted_stack"] == 3
    assert good["score"] > bad["score"] + 6
