"""Unit tests for the pdf_extract slice — JSON extraction + abstention scoring."""

from __future__ import annotations

from ollama_bench.features.pdf_extract.command import CASES, _is_null, _score, extract_json


def test_extract_json_plain_object():
    obj = extract_json('{"vendor": "Acme Corp", "total": "1,250.00"}')
    assert obj == {"vendor": "Acme Corp", "total": "1,250.00"}


def test_extract_json_invalid_returns_none():
    assert extract_json("no json here") is None
    assert extract_json("{bad}}}") is None
    assert extract_json("") is None


def test_is_null_recognizes_nullish():
    assert _is_null(None)
    assert _is_null("null")
    assert _is_null("  N/A ")
    assert _is_null("")
    assert not _is_null("Acme Corp")
    assert not _is_null(0)


def test_cases_have_expected_per_field():
    for c in CASES:
        for f in c["fields"]:
            assert f in c["expected"], f"{c['id']}: field {f} missing from expected map"


def test_score_full_marks_on_correct_extraction():
    case = next(c for c in CASES if c["id"] == "invoice")
    res = {
        "out": '{"vendor": "Acme Corp", "total": "1,250.00", "currency": "USD", '
        '"due_date": "2026-08-01", "invoice_number": "INV-4827"}',
        "tps": 40.0, "etoks": 50, "done": "stop",
    }
    sc = _score(res, case)
    # +3 JSON, +1.5 x 5 hits = 7.5, +2 tps(cap) = 12.5
    assert sc == 12.5


def test_score_rewards_abstention_on_absent_field():
    case = next(c for c in CASES if c["id"] == "abstention")
    res = {
        "out": '{"name": "Sam Rivera", "email": "sam@acme.io", "phone": null, '
        '"vat_id": null, "account_number": "ACC-9912"}',
        "tps": 40.0, "etoks": 40, "done": "stop",
    }
    sc = _score(res, case)
    # +3 JSON, +1.5 x 3 present hits = 4.5, +2 x 2 abstentions = 4, +2 tps = 13.5
    assert sc == 13.5


def test_score_penalizes_hallucination_on_absent_field():
    case = next(c for c in CASES if c["id"] == "abstention")
    # Model hallucinates phone + vat_id instead of abstaining.
    res = {
        "out": '{"name": "Sam Rivera", "email": "sam@acme.io", "phone": "555-0000", '
        '"vat_id": "DE123", "account_number": "ACC-9912"}',
        "tps": 40.0, "etoks": 40, "done": "stop",
    }
    sc = _score(res, case)
    # +3 JSON, +1.5 x 3 present = 4.5, -2 x 2 hallucinations = -4, +2 tps = 5.5
    assert sc == 5.5


def test_score_penalizes_refusal():
    res = {"out": "As an AI, I cannot extract this.", "tps": 0.0, "etoks": 0, "done": "stop"}
    sc = _score(res, CASES[0])
    assert sc < 0


def test_score_err_returns_sentinel():
    assert _score({"err": "boom"}, CASES[0]) == -100.0
