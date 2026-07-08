"""Unit tests for deep slice — exercise _aggregate, _write_outputs, mock call."""

from __future__ import annotations

import csv
import json

from ollama_bench.features.deep.command import (
    PROMPTS,
    _aggregate,
    _details_path,
    _load_results_from_details,
    _load_results_from_tsv,
    _write_outputs,
)


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


def _write_details(base, rows):
    path = _details_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return path


def test_load_results_from_details_reconstructs_model(tmp_path):
    """Resume source-of-truth: the append-only JSONL rebuilds a model's scores."""
    base = tmp_path / "deep_bench_strip"
    _write_details(
        base,
        [
            {"model": "modelA", "task": "improve", "case": "c1", "score": 5.0, "metrics": {}},
            {"model": "modelA", "task": "improve", "case": "c2", "score": 5.0, "metrics": {}},
        ],
    )
    results = _load_results_from_details(base, ["improve"])
    assert "modelA" in results
    scores = [it["sc"] for it in results["modelA"]["improve"]]
    assert scores == [5.0, 5.0]


def test_load_results_from_details_skips_truncated_line(tmp_path):
    """A kill mid-write leaves a partial trailing JSON record — resume must not crash."""
    base = tmp_path / "deep_bench_strip"
    path = _details_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(
            json.dumps({"model": "modelA", "task": "improve", "case": "c1", "score": 5.0}) + "\n"
        )
        f.write('{"model": "modelA", "task": "improve", "case": "c2", "score": 5')  # truncated
    results = _load_results_from_details(base, ["improve"])
    assert "modelA" in results
    assert len(results["modelA"]["improve"]) == 1  # only the well-formed line survived


def test_resume_aggregate_preserves_completed_model(tmp_path):
    """CRITICAL regression: a resumed run must keep previously-scored models in
    the final ranking — not overwrite them with only the newly-benched ones
    (the exact 'perder todo el progreso' bug)."""
    base = tmp_path / "deep_bench_strip"
    _write_details(
        base,
        [
            {"model": "modelA", "task": "improve", "case": "c1", "score": 5.0, "metrics": {}},
            {"model": "modelA", "task": "improve", "case": "c2", "score": 5.0, "metrics": {}},
        ],
    )
    # Resume reconstructs modelA from JSONL, then modelB is benched fresh this run.
    results = _load_results_from_details(base, ["improve"])
    results["modelB"] = {"improve": [{"sc": 7.0}, {"sc": 7.0}]}
    per_task = _aggregate(results, ["improve"])
    ranked_models = [m for m, _ in per_task["improve"]]
    assert "modelA" in ranked_models  # the old bug DROPPED this
    assert "modelB" in ranked_models
    assert per_task["improve"][0][0] == "modelB"  # 7.0 outranks 5.0


def test_write_outputs_keeps_resumed_model(tmp_path):
    """The final TSV rewrite must contain the resumed model (not just new ones)."""
    base = tmp_path / "deep_bench_strip"
    per_task = {"improve": [("modelB", 7.0), ("modelA", 5.0)]}  # modelA came from resume
    _write_outputs(per_task, ["improve"], base)
    tsv = (tmp_path / "deep_bench_strip.tsv").read_text()
    assert "modelA" in tsv
    assert "modelB" in tsv


def test_load_results_from_tsv_fallback(tmp_path):
    """When the details JSONL is missing, the ranked TSV still reconstructs means."""
    base = tmp_path / "deep_bench_strip"
    tsv = base.with_suffix(".tsv")
    tsv.parent.mkdir(parents=True, exist_ok=True)
    with tsv.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["task", "rank", "score", "model"])
        w.writerow(["improve", 1, 6.5, "modelA"])
    results = _load_results_from_tsv(tsv, ["improve"])
    assert "modelA" in results
    assert results["modelA"]["improve"][0]["sc"] == 6.5
