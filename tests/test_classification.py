"""Tests for the closed-label classification slice."""

from __future__ import annotations

from ollama_bench.features.classification.cases import CASES, TAXONOMIES, build_prompt
from ollama_bench.features.classification.metrics import (
    parse_label,
    promotion_decision,
    summarize,
)


def test_route_dataset_is_balanced_and_has_at_least_thirty_cases():
    route = [case for case in CASES if case["suite"] == "route"]
    counts = {label: sum(case["label"] == label for case in route) for label in TAXONOMIES["route"]}
    assert len(route) >= 30
    assert len(set(counts.values())) == 1
    assert all(count >= 6 for count in counts.values())


def test_all_cases_have_unique_ids_and_valid_labels():
    assert len({case["id"] for case in CASES}) == len(CASES)
    for case in CASES:
        assert case["label"] in TAXONOMIES[case["suite"]]
        assert case["text"].strip()


def test_prompt_contains_closed_taxonomy_and_no_gold_label_hint():
    case = next(case for case in CASES if case["id"] == "route-code-01")
    prompt = build_prompt(case)
    assert "code | web | doc | trivial | security" in prompt
    assert "Return only the label" in prompt
    assert case["text"] in prompt


def test_parse_label_is_closed_set_and_rejects_prose():
    allowed = TAXONOMIES["route"]
    assert parse_label("CODE", allowed) == "code"
    assert parse_label("`web`", allowed) == "web"
    assert parse_label("label: code", allowed) is None
    assert parse_label("code or security", allowed) is None
    assert parse_label("", allowed) is None


def test_summarize_counts_invalid_as_wrong_and_computes_macro_f1():
    rows = [
        {"gold": "code", "pred": "code", "dt": 0.4, "tps": 20},
        {"gold": "code", "pred": "web", "dt": 0.2, "tps": 40},
        {"gold": "web", "pred": "web", "dt": 0.3, "tps": 30},
        {"gold": "web", "pred": None, "dt": 0.1, "tps": 10},
    ]
    result = summarize(rows, ("code", "web"))
    assert result["accuracy"] == 0.5
    assert result["macro_f1"] == 0.5833
    assert result["invalid_rate"] == 0.25
    assert result["median_latency"] == 0.25
    assert result["median_tps"] == 25.0


def test_promotion_accepts_only_when_all_gates_pass():
    baseline = {"macro_f1": 0.98, "median_latency": 0.9}
    candidate = {
        "macro_f1": 0.96,
        "median_latency": 0.3,
        "invalid_rate": 0.05,
        "size_gib": 1.8,
    }
    result = promotion_decision(
        candidate,
        baseline,
        quality_margin=0.02,
        min_speedup=3.0,
        max_size_gib=2.0,
        max_invalid_rate=0.4,
    )
    assert result["decision"] == "ACCEPT"
    assert result["failed"] == []
    assert result["latency_speedup"] == 3.0


def test_promotion_rejects_unknown_size_and_semantic_quality_loss():
    result = promotion_decision(
        {"macro_f1": 0.90, "median_latency": 0.1, "invalid_rate": 0.0, "size_gib": None},
        {"macro_f1": 0.98, "median_latency": 1.0},
        quality_margin=0.02,
        min_speedup=3.0,
        max_size_gib=2.0,
        max_invalid_rate=0.4,
    )
    assert result["decision"] == "REJECT"
    assert result["failed"] == ["quality", "size"]
