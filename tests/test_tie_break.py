"""Unit tests for tie_break slice."""
from __future__ import annotations

from ollama_bench.features.tie_break.command import PROMPTS, _aggregate


def test_prompts_hard():
    """All tie-break prompts MUST be harder (structural / ambiguity) than first-pass."""
    for task, cfg in PROMPTS.items():
        assert "v_hard" in cfg, f"{task} missing v_hard prompt"
        assert "scorer" in cfg, f"{task} missing scorer callable"
        assert callable(cfg["scorer"])


def test_prompts_cover_5_tasks():
    assert set(PROMPTS.keys()) == {"improve", "codeq_sum", "smart_trim", "web_synth", "code_gen"}


def test_aggregate_no_errors():
    results = {
        "m1": {"improve": 5.0, "codeq_sum": 6.0},
        "m2": {"improve": 7.0, "codeq_sum": 4.0},
    }
    out = _aggregate(results, ["improve", "codeq_sum"])
    assert out["improve"][0][0] == "m2"
    assert out["codeq_sum"][0][0] == "m1"
