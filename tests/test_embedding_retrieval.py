"""Unit tests for embedding_retrieval — cosine + eval_model (mocked embed)."""

from __future__ import annotations

from unittest.mock import patch

from ollama_bench.features.embedding_retrieval.command import CASES, _cosine, eval_model


def test_cosine_identical():
    v = [1.0, 2.0, 3.0]
    assert _cosine(v, v) == 1.0


def test_cosine_orthogonal():
    assert abs(_cosine([1.0, 0.0], [0.0, 1.0])) < 1e-9


def test_cosine_opposite():
    assert _cosine([1.0, 1.0], [-1.0, -1.0]) == -1.0


def test_cosine_mismatched_length_returns_zero():
    assert _cosine([1.0, 2.0], [1.0]) == 0.0
    assert _cosine([], []) == 0.0


def test_eval_model_perfect_rank_when_gold_closest():
    """If the gold passage embeds identical to the query and others are
    orthogonal, MRR=1.0, recall@5=1.0."""

    # Build deterministic vectors: query == gold passage; distractors orthogonal.
    def fake_embed(model, text, timeout=60):
        if "query-sentinel" in text or "gold-sentinel" in text:
            return {"vec": [1.0, 0.0, 0.0]}
        return {"vec": [0.0, 1.0, 0.0]}

    one_case = [
        {
            "id": "x",
            "query": "query-sentinel",
            "passages": ["gold-sentinel", "distractor1", "distractor2"],
            "gold_idx": 0,
        }
    ]
    with (
        patch("ollama_bench.features.embedding_retrieval.command.CASES", one_case),
        patch("ollama_bench.features.embedding_retrieval.command.embed", side_effect=fake_embed),
    ):
        r = eval_model("m", timeout=5)
    assert "err" not in r
    assert r["mrr"] == 1.0
    assert r["recall5"] == 1.0


def test_eval_model_propagates_embed_error():
    def fake_embed(model, text, timeout=60):
        return {"err": "HTTP 500: boom"}

    with patch("ollama_bench.features.embedding_retrieval.command.embed", side_effect=fake_embed):
        r = eval_model("m", timeout=5)
    assert "err" in r


def test_cases_have_gold_in_range():
    for c in CASES:
        assert 0 <= c["gold_idx"] < len(c["passages"]), f"{c['id']} bad gold_idx"
        assert len(c["passages"]) >= 3
