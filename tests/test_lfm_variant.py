"""Unit tests for lfm_variant slice — exercises _rank, _score."""
from __future__ import annotations

from ollama_bench.features.lfm_variant.command import LFM_VARIANTS, _score


def test_lfm_variants_list_nonempty():
    assert len(LFM_VARIANTS) >= 1
    for v in LFM_VARIANTS:
        assert "LFM" in v or "lfm" in v


def test_score_err_returns_minus():
    assert _score({"err": "boom"}) == -100.0


def test_score_clean_in_budget():
    res = {"out": "Validates email format using regex.", "tps": 30.0, "etoks": 6, "done": "stop"}
    sc = _score(res, budget=30)
    assert sc > 0


def test_score_empty_penalized():
    res = {"out": "", "tps": 0.0, "etoks": 0, "done": "stop"}
    sc = _score(res)
    assert sc < 0
