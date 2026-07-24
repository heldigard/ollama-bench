"""Unit tests for report slice — TSV aggregation + MD rendering."""

from __future__ import annotations

from ollama_bench.features.report.command import _read_tsv, _render_markdown, cmd_report_build


def test_render_markdown_empty():
    out = _render_markdown({}, "Title")
    assert "Title" in out
    assert "no data" in out


def test_render_markdown_with_data():
    per_task = {"improve": [("m1", 5.5), ("m2", 4.0)]}
    out = _render_markdown(per_task, "My Bench")
    assert "My Bench" in out
    assert "## improve" in out
    assert "m1" in out
    assert "5.5" in out
    assert "|" in out  # table format


def test_read_tsv_sorts_descending(tmp_path):
    tsv = tmp_path / "in.tsv"
    tsv.write_text(
        "task\trank\tscore\tmodel\nimprove\t1\t3.0\tm3\nimprove\t2\t7.0\tm1\nimprove\t3\t5.0\tm2\n"
    )
    out = _read_tsv(tsv)
    assert out["improve"][0] == ("m1", 7.0)
    assert out["improve"][1] == ("m2", 5.0)
    assert out["improve"][2] == ("m3", 3.0)


def test_cmd_report_build_missing_input(tmp_path):
    args = type(
        "A",
        (),
        {
            "input": str(tmp_path / "noexist.tsv"),
            "output": None,
            "title": None,
        },
    )()
    rc = cmd_report_build(args)
    assert rc == 2  # error


def test_cmd_report_build_renders(tmp_path):
    tsv = tmp_path / "in.tsv"
    tsv.write_text("task\trank\tscore\tmodel\nimprove\t1\t5.0\tm1\n")
    out = tmp_path / "out.md"
    args = type(
        "A",
        (),
        {
            "input": str(tsv),
            "output": str(out),
            "title": "Test Report",
        },
    )()
    rc = cmd_report_build(args)
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "Test Report" in content
    assert "m1" in content
