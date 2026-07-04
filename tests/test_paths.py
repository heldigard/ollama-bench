"""Unit tests for shared.paths — output dir + unsafe-name guard."""
from __future__ import annotations

import tempfile

from ollama_bench.shared.paths import logs_dir, result_path


def test_result_path_basic():
    with tempfile.TemporaryDirectory():
        p = result_path("my_bench")
        assert p.name == "my_bench.tsv"
        assert p.parent.exists()


def test_result_path_rejects_traversal():
    try:
        result_path("../escape")
    except ValueError as e:
        assert "unsafe" in str(e).lower()
        return
    raise AssertionError("expected ValueError")


def test_result_path_rejects_slash():
    try:
        result_path("foo/bar")
    except ValueError as e:
        assert "unsafe" in str(e).lower()
        return
    raise AssertionError("expected ValueError")


def test_logs_dir_creates():
    with tempfile.TemporaryDirectory():
        p = logs_dir()
        assert p.exists()
