"""TSV schema contract.

Lock down the column names each writer produces and each reader expects.
Silent breakage: a writer renames `name` → `model` without updating the reader,
the reader crashes on KeyError deep inside the bench run with no clear cause.

Approach: regex over source (string literals, single/double quotes) — picks up
both DictWriter(fieldnames=[...]) and csv.writer() + writerow([...]) sites.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "src" / "ollama_bench"


def _read(path: Path) -> str:
    return path.read_text()


# Match a string literal: "abc" OR 'abc'.
_QUOTED = r'(?:"([^"]+)"|\'([^\']+)\')'


def _list_items(match_text: str) -> list[str]:
    """Pull string items from a `["a", "b"]` or `['a', 'b']` list source."""
    return [a or b for a, b in re.findall(_QUOTED, match_text)]


def _writer_columns(text: str) -> list[list[str]]:
    """Find DictWriter(fieldnames=...) sites + resolve to column-list.

    Handles two forms:
      1. `fieldnames=["a", "b"]` — literal list → use directly.
      2. `fieldnames=keys` — variable → scan source for `keys = [...]` literal.
    """
    out: list[list[str]] = []
    literal_pat = (
        r"DictWriter\([^)]*?fieldnames\s*=\s*\[((?:"
        + _QUOTED
        + r"\s*,\s*)+(?:"
        + _QUOTED
        + r"\s*)?)\]"
    )
    for m in re.finditer(literal_pat, text):
        out.append(_list_items(m.group(1)))

    # Resolve variable references: `fieldnames=keys` → look back for `keys = [...]`.
    var_pat = r"DictWriter\([^)]*?fieldnames\s*=\s*([A-Za-z_]\w*)"
    for m in re.finditer(var_pat, text):
        var = m.group(1)
        # Word-boundary anchor (not line start) so indented assignments match.
        assign = re.search(
            rf"\b{var}\s*=\s*\[((?:" + _QUOTED + r"\s*,\s*)*(?:" + _QUOTED + r"\s*)?)\]",
            text[: m.start()],
        )
        if assign:
            out.append(_list_items(assign.group(1)))
    return out


def _writer_literal_header(text: str) -> list[list[str]]:
    """Find csv.writer() + writerow(["col1",...]) sites. Returns list of column-lists."""
    out: list[list[str]] = []
    pat = r"writerow\s*\(\s*\[((?:" + _QUOTED + r"\s*,\s*)+(?:" + _QUOTED + r"\s*)?)\]"
    for m in re.finditer(pat, text):
        out.append(_list_items(m.group(1)))
    return out


def _reader_columns(text: str) -> set[str]:
    """Return the set of all `row["col"]` / `row.get("col")` accesses in text."""
    cols: set[str] = set()
    for m in re.finditer(r'row(?:\.get)?\s*\(\s*"([^"]+)"\s*\)', text):
        cols.add(m.group(1))
    for m in re.finditer(r"row(?:\.get)?\s*\(\s*'([^']+)'\s*\)", text):
        cols.add(m.group(1))
    return cols


# ---------------------------------------------------------------------------
# smoke: writer MUST emit every column candidates consumes
# ---------------------------------------------------------------------------


def test_smoke_writer_emits_all_columns():
    src = _read(ROOT / "features" / "smoke" / "command.py")
    writers = _writer_columns(src)
    assert writers, "smoke.command has no DictWriter(fieldnames=[...]) site"
    written: set[str] = set()
    for cols in writers:
        written.update(cols)

    candidates_src = _read(ROOT / "features" / "candidates" / "command.py")
    candidates_cols = _reader_columns(candidates_src)
    needed = candidates_cols & {"name", "status", "strippable"}
    missing = needed - written
    assert not missing, (
        f"smoke writer missing columns consumed by candidates: {sorted(missing)}; "
        f"written={sorted(written)}; candidates reads={sorted(candidates_cols)}"
    )


# ---------------------------------------------------------------------------
# deep: writer MUST emit every column report + candidates consume
# ---------------------------------------------------------------------------


def test_deep_writer_emits_all_columns():
    src = _read(ROOT / "features" / "deep" / "command.py")
    writers = _writer_literal_header(src)
    assert writers, "deep.command has no csv.writer() + writerow([...]) header"
    written = set()
    for cols in writers:
        written.update(cols)

    report_cols = _reader_columns(_read(ROOT / "features" / "report" / "command.py"))
    candidates_cols = _reader_columns(_read(ROOT / "features" / "candidates" / "command.py"))

    needed = (report_cols | candidates_cols) & {"task", "rank", "score", "model"}
    missing = needed - written
    assert not missing, (
        f"deep._write_outputs header missing columns: {sorted(missing)}; "
        f"written={sorted(written)}; "
        f"report reads={sorted(report_cols)}; "
        f"candidates reads={sorted(candidates_cols)}"
    )


# ---------------------------------------------------------------------------
# tie-break: writer emits (model, score) ranking tuples
# ---------------------------------------------------------------------------


def test_tie_break_ranking_emits_model_and_score():
    """tie_break.cmd_tie_break writes an MD ranking; the per-row tuple MUST
    contain (model, score) so the report builder can consume it.
    """
    src = _read(ROOT / "features" / "tie_break" / "command.py")
    fn_start = src.find("def cmd_tie_break")
    next_def = src.find("\ndef ", fn_start + 1)
    body = src[fn_start : next_def if next_def > 0 else len(src)]
    body_lower = body.lower()
    assert "model" in body_lower and "score" in body_lower, (
        "tie_break cmd_tie_break ranking body must include both `model` and `score` "
        "in its formatted output; downstream tooling (candidates, report) needs both"
    )


# ---------------------------------------------------------------------------
# Delimiter lock: TAB across all TSV I/O sites
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        ROOT / "features" / "smoke" / "command.py",
        ROOT / "features" / "deep" / "command.py",
        ROOT / "features" / "report" / "command.py",
        ROOT / "features" / "candidates" / "command.py",
    ],
)
def test_tsv_delimiter_is_tab(path: Path):
    """Lock delimiter='\\t' across all TSV readers + writers.

    Comma (csv default) would silently mis-parse model tags containing commas
    (e.g. tags with size info from some HF repos).
    """
    text = _read(path)
    if "csv." not in text:
        pytest.skip(f"{path.name}: no csv I/O")
    n_tabs = text.count('delimiter="\\t"')
    n_csv_calls = text.count("DictWriter(") + text.count("DictReader(") + text.count("csv.writer(")
    assert n_tabs >= n_csv_calls, (
        f'{path.name}: only {n_tabs} `delimiter="\\t"` for {n_csv_calls} csv calls; '
        "all TSV I/O must use TAB"
    )
