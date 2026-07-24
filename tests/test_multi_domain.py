"""Unit tests for multi_domain slice."""

from __future__ import annotations

from ollama_bench.features.multi_domain.command import (
    ALL_TESTS,
    CODE_PROMPTS,
    COMPACT_PROMPTS,
    IMPROVE_PROMPTS,
    REASON_PROMPTS,
    BenchResult,
    _result_from_call,
)


def test_all_tests_has_4_domains():
    domains = {t[1] for t in ALL_TESTS}
    assert domains == {"improve", "compact", "code", "reason"}


def test_each_domain_has_prompts():
    assert len(IMPROVE_PROMPTS) >= 1
    assert len(COMPACT_PROMPTS) >= 1
    assert len(CODE_PROMPTS) >= 1
    assert len(REASON_PROMPTS) >= 1


def test_all_tests_tuples_have_3_elements():
    for entry in ALL_TESTS:
        assert len(entry) == 3  # (test_id, domain, prompt)
        assert isinstance(entry[0], str)
        assert isinstance(entry[1], str)
        assert isinstance(entry[2], str)


def test_result_from_call_error():
    r = _result_from_call(
        model="m",
        test_id="t",
        domain="d",
        prompt="p",
        call_res={"error": "boom"},
        mem_peak=100,
    )
    assert r.status == "error"
    assert "boom" in r.error


def test_result_from_call_ok():
    r = _result_from_call(
        model="m",
        test_id="t",
        domain="d",
        prompt="p",
        call_res={
            "output": "hello",
            "total_s": 1.0,
            "eval_tokens": 5,
            "prompt_tokens": 2,
            "ttft_s": 0.1,
        },
        mem_peak=200,
    )
    assert r.status == "ok"
    assert r.output == "hello"
    assert r.output_chars == 5
    assert r.gpu_mem_peak_mib == 200
    assert r.tok_per_s == 5.0


def test_benchresult_dataclass_defaults():
    r = BenchResult(model="m", test_id="t", domain="d", prompt_chars=10, status="ok")
    assert r.error == ""
    assert r.load_s == 0.0
    assert r.eval_tokens == 0
