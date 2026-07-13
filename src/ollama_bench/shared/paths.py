"""Output paths. ABSOLUTE resolution to survive symlinks and CWD changes."""

from __future__ import annotations

from pathlib import Path

from ollama_bench.shared.config import LOGS_DIR, RESULTS_DIR


def results_dir() -> Path:
    """Return the root results dir, creating if needed."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


def logs_dir() -> Path:
    """Return the logs dir, creating if needed."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def result_path(name: str, ext: str = "tsv") -> Path:
    """Return path to a named result file under results_dir().

    `name` should NOT include extension. Returns: ~/.cache/ollama-bench/results/<name>.<ext>
    """
    if not name or "/" in name or ".." in name:
        raise ValueError(f"unsafe result name: {name!r}")
    return results_dir() / f"{name}.{ext}"
