"""Unit tests for deep slice — exercise _aggregate, _write_outputs, mock call."""
from __future__ import annotations

from ollama_bench.features.deep.command import PROMPTS, _aggregate, _write_outputs


def test_aggregate_sorts_descending():
    results = {
        "m1": {"improve": [{"sc": 5.0}, {"sc": 5.0}]},
        "m2": {"improve": [{"sc": 7.0}, {"sc": 7.0}]},
        "m3": {"improve": [{"sc": 3.0}, {"sc": 3.0}]},
    }
    out = _aggregate(results, ["improve"])
    assert out["improve"][0][0] == "m2"
    assert out["improve"][1][0] == "m1"
    assert out["improve"][2][0] == "m3"


def test_aggregate_skips_errors():
    results = {
        "m1": {"improve": [{"sc": 5.0}]},
        "m2": {"err": "boom"},
        "m3": {"improve": [{"sc": 3.0}]},
    }
    out = _aggregate(results, ["improve"])
    assert len(out["improve"]) == 2


def test_write_outputs_creates_tsv_and_md(tmp_path):
    per_task = {"improve": [("m1", 5.5), ("m2", 4.0)], "codeq_sum": [("m3", 6.0)]}
    base = tmp_path / "deep_bench"
    _write_outputs(per_task, ["improve", "codeq_sum"], base)
    assert (tmp_path / "deep_bench.tsv").exists()
    assert (tmp_path / "deep_bench.md").exists()
    md = (tmp_path / "deep_bench.md").read_text()
    assert "## improve" in md
    assert "## codeq_sum" in md


def test_prompts_have_all_5_tasks():
    expected = {"improve", "codeq_sum", "smart_trim", "web_synth", "code_gen"}
    assert set(PROMPTS.keys()) == expected


def test_prompts_have_budget_words():
    for task, cfg in PROMPTS.items():
        assert "budget_words" in cfg, f"{task} missing budget_words"
        assert cfg["budget_words"] > 0
