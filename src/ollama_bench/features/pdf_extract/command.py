"""pdf_extract — schema-driven field-extraction bench (ground-truth scoring).

Each case gives the model a markdown document (the post-marker stage) + a field
list (schema). The model must emit a JSON object mapping each field to its value
(or null if absent — LIFT-style abstention). Scoring is DETERMINISTIC: valid JSON
+ per-field value hits + an abstention bonus for correctly returning null on a
field the document does NOT contain (a model that hallucinates a value loses it).

This is the bench the cross-cli pdf-extract-structured.py needs: it isolates the
LLM extraction stage (model-dependent) from the upstream marker parse
(model-independent). Retires the pegasus912 proxy choice there.

# vs-soft-allow  — end-to-end pipeline (doc + schema -> JSON -> per-field score -> rank).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import prepare_scored_response

# Each case: id, doc (markdown), fields (schema field list), expected (field ->
# lowercase substring that MUST appear in a correct value, or None to require
# abstention i.e. the field is genuinely absent and the model must output null).
CASES: list[dict] = [
    {
        "id": "invoice",
        "fields": ["vendor", "total", "currency", "due_date", "invoice_number"],
        "expected": {
            "vendor": "acme corp",
            "total": "1,250.00",
            "currency": "usd",
            "due_date": "2026-08-01",
            "invoice_number": "inv-4827",
        },
        "doc": (
            "# INVOICE\n\n"
            "**Vendor:** Acme Corp\n"
            "**Invoice Number:** INV-4827\n"
            "**Date:** 2026-07-04\n"
            "**Due Date:** 2026-08-01\n\n"
            "| Item | Qty | Price |\n|---|---|---|\n| Widget | 10 | 125.00 |\n\n"
            "**Total:** 1,250.00 USD\n"
        ),
    },
    {
        "id": "contact_card",
        "fields": ["name", "email", "phone", "company"],
        "expected": {
            "name": "jordan lee",
            "email": "jordan.lee@example.com",
            "phone": "+1-555-0142",
            "company": "northwind",
        },
        "doc": (
            "## Contact\n\n"
            "- **Name:** Jordan Lee\n"
            "- **Email:** jordan.lee@example.com\n"
            "- **Phone:** +1-555-0142\n"
            "- **Company:** Northwind\n"
        ),
    },
    {
        "id": "product",
        "fields": ["name", "price", "sku", "in_stock"],
        "expected": {
            "name": "ergonomic chair",
            "price": "299.99",
            "sku": "chr-erg-22",
            "in_stock": "true",
        },
        "doc": (
            "# Product\n\n"
            "**Name:** Ergonomic Chair\n"
            "**SKU:** CHR-ERG-22\n"
            "**Price:** $299.99\n"
            "**In stock:** Yes\n"
        ),
    },
    {
        "id": "event",
        "fields": ["title", "date", "location", "organizer"],
        "expected": {
            "title": "rust meetup",
            "date": "2026-09-15",
            "location": "berlin",
            "organizer": "rust berlin",
        },
        "doc": (
            "## Event\n\n"
            "**Title:** Rust Meetup\n"
            "**Date:** 2026-09-15\n"
            "**Location:** Berlin\n"
            "**Organizer:** Rust Berlin\n"
        ),
    },
    {
        "id": "abstention",  # the doc is missing 2 of 5 fields — model MUST null them, not hallucinate
        "fields": ["name", "email", "phone", "vat_id", "account_number"],
        "expected": {
            "name": "sam rivera",
            "email": "sam@acme.io",
            "phone": None,  # absent -> correct answer is null
            "vat_id": None,  # absent -> correct answer is null
            "account_number": "acc-9912",
        },
        "doc": (
            "## Customer\n\n"
            "- **Name:** Sam Rivera\n"
            "- **Email:** sam@acme.io\n"
            "- **Account Number:** ACC-9912\n"
            "(no phone or VAT id on record)\n"
        ),
    },
    {
        "id": "bank_statement_noise",
        "fields": ["account_holder", "closing_balance", "currency", "statement_period", "swift_code"],
        "expected": {
            "account_holder": "maria chen",
            "closing_balance": "8,441.20",
            "currency": "eur",
            "statement_period": "2026-06",
            "swift_code": None,
        },
        "doc": (
            "# Monthly Statement\n\n"
            "Account Holder: Maria Chen\n"
            "Period: 2026-06\n"
            "Opening Balance: EUR 7,900.00\n"
            "Closing Balance: EUR 8,441.20\n"
            "Note: SWIFT/BIC is not printed on this statement.\n"
        ),
    },
    {
        "id": "contract_terms",
        "fields": ["client", "effective_date", "termination_notice_days", "governing_law", "auto_renewal"],
        "expected": {
            "client": "blue finch labs",
            "effective_date": "july 1, 2026",
            "termination_notice_days": "30",
            "governing_law": "new york",
            "auto_renewal": "true",
        },
        "doc": (
            "## Services Agreement\n\n"
            "Client: Blue Finch Labs\n"
            "Effective Date: July 1, 2026\n"
            "This agreement renews automatically for successive one-year terms unless either party provides 30 days written notice.\n"
            "Governing Law: New York\n"
        ),
    },
    {
        "id": "medical_lab",
        "fields": ["patient", "test", "result", "unit", "reference_range", "doctor"],
        "expected": {
            "patient": "alex rivera",
            "test": "hemoglobin",
            "result": "13.8",
            "unit": "g/dl",
            "reference_range": "13.0-17.0",
            "doctor": None,
        },
        "doc": (
            "# Lab Result\n\n"
            "Patient: Alex Rivera\n"
            "| Test | Result | Unit | Reference Range |\n"
            "|---|---:|---|---|\n"
            "| Hemoglobin | 13.8 | g/dL | 13.0-17.0 |\n"
            "Ordering doctor: not provided in source export.\n"
        ),
    },
]

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(out: str) -> dict | None:
    """Return the first parseable JSON object in out, or None."""
    if not out:
        return None
    m = _JSON_BLOCK_RE.search(out)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _is_null(v) -> bool:
    """True if v is JSON null / missing / an explicit null-ish string."""
    if v is None:
        return True
    if isinstance(v, str) and v.strip().lower() in ("", "null", "none", "n/a"):
        return True
    return False


def _score(res: dict, case: dict) -> float:
    """Ground-truth score. Range -10 to ~12.

    Leak/refusal/empty penalties; +3 valid JSON; per-field scoring:
      - present-in-doc field: +1.5 if the expected substring appears in the value
      - absent-in-doc field (expected None): +2 if the model correctly abstained
        (null), -2 if it hallucinated a value
    ; tps bonus capped at 2.
    """
    if "err" in res:
        return -100.0
    res, policy = prepare_scored_response(res)
    out = res["out"]
    L = out.lower()
    s = 0.0
    if policy["policy"] == "unsafe" and ("<think>" in L or "thinking process" in L):
        s -= 5
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if not out.strip():
        s -= 10

    obj = extract_json(out)
    if obj is not None:
        s += 3.0

    expected: dict = case["expected"]
    if obj is not None:
        for field, want in expected.items():
            got = obj.get(field)
            if want is None:
                # Abstention field: reward null, penalize hallucination.
                s += 2.0 if _is_null(got) else -2.0
            else:
                got_s = "" if got is None else str(got)
                if want.lower() in got_s.lower():
                    s += 1.5

    s += min(res.get("tps", 0) / 15.0, 2.0)
    return round(s, 2)


def _build_prompt(case: dict) -> str:
    fields_nl = "\n".join(f"  - {f}" for f in case["fields"])
    return f"""You extract structured fields from a document. Read the document and respond with ONLY a JSON object mapping each field to its value as a string. If a field is genuinely absent from the document, output null for it (abstain — do NOT guess). No prose, no code fence.

Schema (emit exactly these keys):
{fields_nl}

DOCUMENT:
{case["doc"]}"""


def run_model(model: str, opts: CallOpts) -> dict:
    out: list = []
    for c in CASES:
        res = call(model, _build_prompt(c), opts=opts)
        out.append({"id": c["id"], "sc": _score(res, c)})
    return {model: out}


def cmd_pdf_extract(args: argparse.Namespace) -> int:
    """`ollama-bench pdf-extract` entry point."""
    candidates = args.models or []
    if not candidates:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    print(f"# PDF-extract bench: {len(candidates)} models x {len(CASES)} cases", file=sys.stderr)
    opts = CallOpts(num_predict=300, num_ctx=4096)

    results: dict = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m, opts): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(candidates)}] {m[:55]}  done", file=sys.stderr, flush=True)

    ranked = []
    for m, r in results.items():
        if not isinstance(r, list) or not r:
            continue
        scores = [it["sc"] for it in r if "sc" in it]
        avg = round(sum(scores) / len(scores), 2) if scores else -100.0
        ranked.append((m, avg))
    ranked.sort(key=lambda x: -x[1])

    out_path = Path(args.output) if args.output else result_path("pdf_extract", ext="md")
    with out_path.open("w") as f:
        f.write("# PDF-Extract Bench — schema-driven field extraction\n\n")
        f.write(
            f"Scoring: +3 valid JSON, +1.5 per correct field value, +2 abstention on absent "
            f"fields (-2 hallucinate), leak penalty, tps bonus. {len(CASES)} cases per model.\n\n"
        )
        f.write("| # | Score | Model |\n|---|---|---|\n")
        for i, (m, sc) in enumerate(ranked, 1):
            f.write(f"| {i} | {sc:.2f} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser(
        "pdf-extract",
        parents=[parent],
        help="Schema-driven field-extraction bench (ground-truth + abstention).",
    )
    p.add_argument("-m", "--models", nargs="+", required=True, help="Models to bench.")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_pdf_extract)
