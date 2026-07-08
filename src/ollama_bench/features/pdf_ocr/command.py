"""pdf_ocr — rendered-PDF OCR benchmark for vision/OCR Ollama models.

This slice complements ``pdf_extract``. ``pdf_extract`` measures the LLM stage
after marker has already converted a PDF to text/markdown; this slice measures
whether a model can actually read rendered PDF pages. It is intentionally based
on synthetic PDFs generated at runtime so the ground truth is deterministic and
does not depend on private documents.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from ollama_bench.shared.config import OLLAMA_URL
from ollama_bench.shared.paths import result_path

PROMPT = "ocr [img]"

CASES: list[dict[str, Any]] = [
    {
        "id": "invoice_table",
        "lines": [
            "INVOICE INV-4827",
            "Vendor: Acme Corp",
            "Due Date: 2026-08-01",
            "Item Widget Qty 10 Price 125.00",
            "Total: 1,250.00 USD",
        ],
        "must_contain": ["inv-4827", "acme corp", "2026-08-01", "widget", "1,250.00 usd"],
        "must_not": ["northwind", "404", "server error"],
    },
    {
        "id": "lab_report",
        "lines": [
            "LAB RESULT",
            "Patient: Alex Rivera",
            "Test: Hemoglobin",
            "Result: 13.8 g/dL",
            "Reference Range: 13.0-17.0",
            "Ordering doctor: not provided",
        ],
        "must_contain": [
            "alex rivera",
            "hemoglobin",
            "13.8",
            "g/dl",
            "13.0-17.0",
            "not provided",
        ],
        "must_not": ["invoice", "total", "maria chen"],
    },
    {
        "id": "statement_noise",
        "lines": [
            "MONTHLY STATEMENT",
            "Account Holder: Maria Chen",
            "Period: 2026-06",
            "Opening Balance: EUR 7,900.00",
            "Closing Balance: EUR 8,441.20",
            "SWIFT/BIC is not printed on this statement.",
        ],
        "must_contain": [
            "maria chen",
            "2026-06",
            "eur 7,900.00",
            "eur 8,441.20",
            "swift/bic",
            "not printed",
        ],
        "must_not": ["acme corp", "hemoglobin", "password"],
    },
]


@dataclass(frozen=True)
class PdfOcrOpts:
    temperature: float = 0.0
    num_predict: int = 500
    timeout: float = 120.0


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _import_fitz():
    try:
        import fitz  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit("pdf-ocr requires PyMuPDF/fitz to generate and render PDF fixtures.") from exc
    return fitz


def _make_pdf(case: dict[str, Any], out_path: Path) -> None:
    fitz = _import_fitz()
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    y = 86
    for i, line in enumerate(case["lines"]):
        size = 18 if i else 26
        page.insert_text((72, y), line, fontsize=size, fontname="helv", color=(0, 0, 0))
        y += 44 if i else 58
    doc.save(out_path)
    doc.close()


def _render_first_page(pdf_path: Path) -> bytes:
    fitz = _import_fitz()
    doc = fitz.open(pdf_path)
    try:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        return pix.tobytes("png")
    finally:
        doc.close()


def build_pdf_images(tmp_dir: Path) -> dict[str, bytes]:
    """Create deterministic PDF fixtures and return rendered first-page PNG bytes."""
    images: dict[str, bytes] = {}
    for case in CASES:
        pdf_path = tmp_dir / f"{case['id']}.pdf"
        _make_pdf(case, pdf_path)
        images[case["id"]] = _render_first_page(pdf_path)
    return images


def _post_chat(payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def call_vision(model: str, image_bytes: bytes, opts: PdfOcrOpts) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": PROMPT,
            "images": [base64.b64encode(image_bytes).decode("ascii")],
        }
    ]
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {"temperature": opts.temperature, "num_predict": opts.num_predict},
    }
    t0 = time.perf_counter()
    try:
        raw = _post_chat(payload, opts.timeout)
    except Exception as exc:  # noqa: BLE001
        return {"err": f"{type(exc).__name__}: {exc}"}
    dt = time.perf_counter() - t0
    msg = raw.get("message") or {}
    out = str(msg.get("content") or "")
    ed = raw.get("eval_duration", 0) / 1e9
    return {
        "out": out.strip(),
        "dt": round(dt, 2),
        "etoks": raw.get("eval_count", 0),
        "ptoks": raw.get("prompt_eval_count", 0),
        "tps": round(raw.get("eval_count", 0) / ed, 1) if ed > 0 else 0.0,
    }


def score_ocr(out: str, case: dict[str, Any]) -> dict[str, Any]:
    blob = _normalize(out)
    hits = [w for w in case["must_contain"] if _normalize(w) in blob]
    hallucinated = [w for w in case["must_not"] if _normalize(w) in blob]
    recall = len(hits) / max(len(case["must_contain"]), 1)
    hallucination_rate = len(hallucinated) / max(len(case["must_not"]), 1)
    score = 10.0 * recall - 4.0 * hallucination_rate
    if not blob:
        score -= 5.0
    return {
        "hits": hits,
        "misses": [w for w in case["must_contain"] if w not in hits],
        "hallucinated": hallucinated,
        "recall": round(recall, 2),
        "hallucination_rate": round(hallucination_rate, 2),
        "score": round(score, 2),
    }


def run_model(model: str, images: dict[str, bytes], opts: PdfOcrOpts) -> dict[str, Any]:
    rows = []
    for case in CASES:
        res = call_vision(model, images[case["id"]], opts)
        if "err" in res:
            rows.append({"id": case["id"], "score": -100.0, "err": res["err"]})
            continue
        scored = score_ocr(res["out"], case)
        speed_bonus = min(float(res.get("tps", 0)) / 100.0, 2.0)
        rows.append(
            {
                "id": case["id"],
                "score": round(scored["score"] + speed_bonus, 2),
                "recall": scored["recall"],
                "hallucination_rate": scored["hallucination_rate"],
                "seconds": res["dt"],
                "tokens_per_sec": res["tps"],
                "out": res["out"][:500],
            }
        )
    return {model: rows}


def cmd_pdf_ocr(args: argparse.Namespace) -> int:
    candidates = args.models or []
    if not candidates:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    opts = PdfOcrOpts()
    with TemporaryDirectory(prefix="ollama-bench-pdf-ocr-") as td:
        images = build_pdf_images(Path(td))
        results = [run_model(m, images, opts) for m in candidates]

    ranked = []
    flat: dict[str, Any] = {}
    for result in results:
        flat.update(result)
    for model, rows in flat.items():
        scores = [float(r["score"]) for r in rows if "score" in r]
        recalls = [float(r.get("recall", 0.0)) for r in rows]
        avg = round(sum(scores) / len(scores), 2) if scores else -100.0
        recall = round(sum(recalls) / len(recalls), 2) if recalls else 0.0
        ranked.append((model, avg, recall))
    ranked.sort(key=lambda row: (-row[1], -row[2], row[0]))

    out_path = Path(args.output) if args.output else result_path("pdf_ocr", ext="md")
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# PDF-OCR Bench — rendered PDF page OCR\n\n")
        f.write(
            f"Prompt: `{PROMPT}`. Scoring: 10 * recall - 4 * hallucination_rate "
            f"+ speed bonus capped at 2. {len(CASES)} synthetic PDF cases per model.\n\n"
        )
        f.write("| # | Score | Avg Recall | Model |\n|---|---:|---:|---|\n")
        for i, (model, score, recall) in enumerate(ranked, 1):
            f.write(f"| {i} | {score:.2f} | {recall:.2f} | `{model}` |\n")
        f.write("\n## Per-Case Details\n\n")
        for model, rows in flat.items():
            f.write(f"### `{model}`\n\n")
            f.write("| Case | Score | Recall | Hallucination | Seconds | tok/s |\n")
            f.write("|---|---:|---:|---:|---:|---:|\n")
            for row in rows:
                if "err" in row:
                    f.write(f"| {row['id']} | -100.00 | 0.00 | 1.00 | 0.00 | 0.00 |\n")
                    continue
                f.write(
                    f"| {row['id']} | {row['score']:.2f} | {row['recall']:.2f} | "
                    f"{row['hallucination_rate']:.2f} | {row['seconds']:.2f} | "
                    f"{row['tokens_per_sec']:.1f} |\n"
                )
            f.write("\n")
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser(
        "pdf-ocr",
        parents=[parent],
        help="Rendered-PDF OCR bench for vision/OCR models.",
    )
    p.add_argument("-m", "--models", nargs="+", required=True, help="Models to bench.")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_pdf_ocr)
