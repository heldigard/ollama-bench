"""Versioned, ground-truth cases for the classification benchmark."""

from __future__ import annotations

from typing import TypedDict


class ClassificationCase(TypedDict):
    id: str
    suite: str
    text: str
    label: str


TAXONOMIES: dict[str, tuple[str, ...]] = {
    "route": ("code", "web", "doc", "trivial", "security"),
    "caveman": ("critical", "routine", "base"),
}

SUITE_GUIDANCE = {
    "route": (
        "code=implementation, debugging, or code analysis; "
        "web=current or externally sourced information; "
        "doc=document extraction, conversion, or editing; "
        "trivial=acknowledgement or simple closed response; "
        "security=security, credentials, authentication, or vulnerability work"
    ),
    "caveman": (
        "critical=security, errors, architecture, correctness, migrations, or production risk; "
        "routine=acknowledgements and file listings; "
        "base=all other prompts"
    ),
}


def _case(case_id: str, suite: str, label: str, text: str) -> ClassificationCase:
    return {"id": case_id, "suite": suite, "label": label, "text": text}


CASES: tuple[ClassificationCase, ...] = (
    # Route taxonomy: six cases per class. English and Spanish are both first-class.
    _case("route-code-01", "route", "code", "Implement an LRU cache in Python."),
    _case("route-code-02", "route", "code", "Fix the flaky assertion in this Vitest test."),
    _case("route-code-03", "route", "code", "Refactor this service to remove the circular import."),
    _case("route-code-04", "route", "code", "Escribe una consulta SQL con una window function."),
    _case("route-code-05", "route", "code", "Explain why this Rust borrow checker error occurs."),
    _case("route-code-06", "route", "code", "Add pagination to the existing REST client."),
    _case("route-web-01", "route", "web", "Find the current stable Angular version."),
    _case("route-web-02", "route", "web", "What changed in today's Ollama release?"),
    _case("route-web-03", "route", "web", "Busca el precio actual de una RTX 5080 en Colombia."),
    _case("route-web-04", "route", "web", "Compare recent reviews of two travel routers."),
    _case("route-web-05", "route", "web", "Verify who is the current CEO of the company."),
    _case("route-web-06", "route", "web", "Find primary sources for the new Kubernetes feature."),
    _case("route-doc-01", "route", "doc", "Extract the termination clause from this PDF."),
    _case("route-doc-02", "route", "doc", "Convierte este archivo DOCX a Markdown."),
    _case("route-doc-03", "route", "doc", "Create a table from the attached quarterly report."),
    _case("route-doc-04", "route", "doc", "Redact personal data in these scanned invoices."),
    _case("route-doc-05", "route", "doc", "Merge these three PDFs and add page numbers."),
    _case("route-doc-06", "route", "doc", "Edit the spreadsheet and preserve its formulas."),
    _case("route-trivial-01", "route", "trivial", "Thanks, that is all."),
    _case("route-trivial-02", "route", "trivial", "OK."),
    _case("route-trivial-03", "route", "trivial", "¿Cuánto es 7 por 8?"),
    _case("route-trivial-04", "route", "trivial", "Rewrite hello in uppercase."),
    _case("route-trivial-05", "route", "trivial", "Answer yes or no: is 10 greater than 3?"),
    _case("route-trivial-06", "route", "trivial", "List the vowels in the word model."),
    _case("route-security-01", "route", "security", "Audit this OAuth callback for CSRF."),
    _case("route-security-02", "route", "security", "Check this query for SQL injection."),
    _case(
        "route-security-03", "route", "security", "¿Es seguro guardar este token en localStorage?"
    ),
    _case("route-security-04", "route", "security", "Review the patch for an auth bypass."),
    _case("route-security-05", "route", "security", "Rotate the leaked API credential safely."),
    _case("route-security-06", "route", "security", "Threat-model the password reset flow."),
    # Caveman taxonomy mirrors the live deterministic classifier's three outcomes.
    _case("caveman-critical-01", "caveman", "critical", "Debug this production crash."),
    _case("caveman-critical-02", "caveman", "critical", "Review the authentication architecture."),
    _case(
        "caveman-critical-03", "caveman", "critical", "Demuestra que este invariante es correcto."
    ),
    _case("caveman-critical-04", "caveman", "critical", "Plan a zero-downtime database migration."),
    _case("caveman-critical-05", "caveman", "critical", "Find the root cause of this deadlock."),
    _case("caveman-critical-06", "caveman", "critical", "Diseña un eval para el model router."),
    _case("caveman-routine-01", "caveman", "routine", "Thanks!"),
    _case("caveman-routine-02", "caveman", "routine", "Vale, entendido."),
    _case("caveman-routine-03", "caveman", "routine", "List all files."),
    _case("caveman-routine-04", "caveman", "routine", "Muestra los archivos del directorio."),
    _case("caveman-routine-05", "caveman", "routine", "Perfect, thank you."),
    _case("caveman-routine-06", "caveman", "routine", "tree"),
    _case("caveman-base-01", "caveman", "base", "Write a short project status update."),
    _case("caveman-base-02", "caveman", "base", "Suggest three names for this module."),
    _case("caveman-base-03", "caveman", "base", "Resume este párrafo en una oración."),
    _case("caveman-base-04", "caveman", "base", "Explain the difference between RAM and disk."),
    _case("caveman-base-05", "caveman", "base", "Translate this sentence into Spanish."),
    _case("caveman-base-06", "caveman", "base", "Draft a friendly meeting agenda."),
)


def select_cases(suite: str) -> tuple[ClassificationCase, ...]:
    """Return all cases or one named suite."""
    if suite == "all":
        return CASES
    return tuple(case for case in CASES if case["suite"] == suite)


def build_prompt(case: ClassificationCase) -> str:
    """Build the exact closed-label prompt used for one case."""
    labels = " | ".join(TAXONOMIES[case["suite"]])
    return (
        "Classify the INPUT using exactly one label.\n"
        f"Labels: {labels}\n"
        f"Definitions: {SUITE_GUIDANCE[case['suite']]}\n"
        "Return only the label, with no punctuation, reasoning, or prose.\n\n"
        f"INPUT:\n{case['text']}\n\nLABEL:"
    )
