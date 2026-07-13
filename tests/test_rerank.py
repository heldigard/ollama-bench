"""Tests for deterministic, quality-only reranking."""

from __future__ import annotations

from unittest.mock import patch

from ollama_bench.features.rerank.cases import CASES, build_prompt
from ollama_bench.features.rerank.command import evaluate_model
from ollama_bench.features.rerank.metrics import (
    mrr_at_k,
    ndcg_at_k,
    parse_ranking,
    promotion_decision,
    summarize,
)
from ollama_bench.shared.ollama import CallOpts


def test_cases_are_bilingual_with_ten_documents_and_graded_relevance():
    assert len(CASES) >= 8
    assert {case["language"] for case in CASES} == {"en", "es"}
    assert {case["difficulty"] for case in CASES} >= {"medium", "hard"}
    for case in CASES:
        assert len(case["documents"]) == 10
        assert len({document["id"] for document in case["documents"]}) == 10
        assert {document["relevance"] for document in case["documents"]} >= {0, 2, 3}


def test_prompt_requires_json_and_does_not_expose_relevance():
    prompt = build_prompt(CASES[0])
    assert '"ranking"' in prompt
    assert "d1:" in prompt and "d10:" in prompt
    assert "relevance" not in prompt.lower()


def test_parse_ranking_requires_exact_unique_known_top_three():
    allowed = {"d1", "d2", "d3", "d4"}
    assert parse_ranking('{"ranking":["d2","d1","d3"]}', allowed) == ("d2", "d1", "d3")
    assert parse_ranking('{"ranking":["d2","d2","d3"]}', allowed) is None
    assert parse_ranking('{"ranking":["d2","d1","d9"]}', allowed) is None
    assert parse_ranking('answer: {"ranking":["d2","d1","d3"]}', allowed) is None


def test_relevance_metrics_reward_correct_order_and_penalize_bad_order():
    relevance = {"d1": 3, "d2": 2, "d3": 1, "d4": 0}
    assert ndcg_at_k(("d1", "d2", "d3"), relevance) == 1.0
    assert mrr_at_k(("d1", "d2", "d3"), relevance) == 1.0
    assert ndcg_at_k(("d4", "d3", "d2"), relevance) < 0.3
    assert mrr_at_k(("d4", "d3", "d2"), relevance) == 0.3333


def test_summary_counts_invalid_output_as_quality_failure():
    summary = summarize(
        [
            {
                "ranking": ("d1", "d2", "d3"),
                "ndcg_at_3": 1.0,
                "mrr_at_3": 1.0,
                "top1_correct": True,
            },
            {
                "ranking": None,
                "ndcg_at_3": 0.0,
                "mrr_at_3": 0.0,
                "top1_correct": False,
            },
        ]
    )
    assert summary == {
        "cases": 2,
        "ndcg_at_3": 0.5,
        "mrr_at_3": 0.5,
        "top1_accuracy": 0.5,
        "invalid_rate": 0.5,
    }


def test_promotion_requires_strict_quality_gain_without_regression():
    baseline = {"ndcg_at_3": 0.80, "mrr_at_3": 0.90, "invalid_rate": 0.0}
    accepted = promotion_decision(
        {"ndcg_at_3": 0.83, "mrr_at_3": 0.90, "invalid_rate": 0.0},
        baseline,
        min_ndcg_gain=0.02,
    )
    rejected = promotion_decision(
        {"ndcg_at_3": 0.82, "mrr_at_3": 0.80, "invalid_rate": 0.0},
        baseline,
        min_ndcg_gain=0.02,
    )
    assert accepted["decision"] == "ACCEPT"
    assert rejected["decision"] == "REJECT"
    assert rejected["failed"] == ["mrr_no_regression"]


def test_evaluate_model_scores_a_valid_response_without_a_judge():
    case = (
        {
            "id": "x",
            "language": "en",
            "difficulty": "medium",
            "query": "q",
            "documents": (
                {"id": "d1", "text": "best", "relevance": 3},
                {"id": "d2", "text": "useful", "relevance": 2},
                {"id": "d3", "text": "noise", "relevance": 0},
            ),
        },
    )
    with patch(
        "ollama_bench.features.rerank.command.call",
        return_value={"out": '{"ranking":["d1","d2","d3"]}', "dt": 0.1, "tps": 10.0},
    ):
        rows = evaluate_model("m", case, CallOpts())
    assert rows[0]["ndcg_at_3"] == 1.0
    assert rows[0]["mrr_at_3"] == 1.0
