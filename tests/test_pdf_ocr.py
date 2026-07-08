"""Unit tests for the pdf_ocr slice."""

from pathlib import Path

from ollama_bench.features.pdf_ocr.command import CASES, build_pdf_images, score_ocr


def test_score_ocr_rewards_recall_and_penalizes_hallucination():
    case = {
        "must_contain": ["inv-4827", "acme corp"],
        "must_not": ["server error"],
    }
    scored = score_ocr("text [1,2,3,4] INVOICE INV-4827 Acme Corp", case)
    assert scored["recall"] == 1.0
    assert scored["hallucination_rate"] == 0.0
    assert scored["score"] == 10.0

    bad = score_ocr("INV-4827 server error", case)
    assert bad["recall"] == 0.5
    assert bad["hallucination_rate"] == 1.0
    assert bad["score"] == 1.0


def test_build_pdf_images_returns_png_bytes(tmp_path: Path):
    images = build_pdf_images(tmp_path)
    assert sorted(images) == sorted(case["id"] for case in CASES)
    assert all(data.startswith(b"\x89PNG") for data in images.values())
