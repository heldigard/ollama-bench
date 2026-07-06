"""Drift guard: config.py primary/fallback models must match RANKING.md top-N.

Drift here = the harness (claude-code/hooks, prompt-improve, smart-trim) wires
the wrong model into a hot path. Caught the 2026-07-05 8BB-GPU vs 8GB-GPU typo:
config.py had `MTP_Q4_64k_8BB-GPU` everywhere else says `8GB-GPU`.

These checks are CONSERVATIVE: missing-from-RANKING is a soft warning, missing-
from-config is a hard fail. If you legitimately want config to lead RANKING
(add a task before benching), bump the threshold + comment why.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
CONFIG = ROOT / "src" / "ollama_bench" / "shared" / "config.py"
RANKING = ROOT / "RANKING.md"


def _ranking_top1_per_task() -> dict[str, str]:
    """Return {task: top1_model_tag} from RANKING.md current state.

    Parses the per-task tables (lines start with `| **1**` = bold #1) and
    extracts the model tag from the backtick-quoted 4th column.
    """
    text = RANKING.read_text()
    top: dict[str, str] = {}
    current_task: str | None = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(\w+)", line)
        if m:
            current_task = m.group(1)
            continue
        if current_task is None:
            continue
        # Skip header rows (| # | combined | ...) and separator rows (|---|---|).
        if line.lstrip().startswith("| #") or line.lstrip().startswith("|---"):
            continue
        # Rank column may be `**1**` (round-3 winner, annotated) or `| 1 |` (plain).
        # First non-header row = combined-rank #1; capture its FIRST backtick-tagged model.
        if re.match(r"^\|\s+\**1\**\s+\|", line):
            tag = re.search(r"`([^`]+)`", line)
            if tag:
                top.setdefault(current_task, tag.group(1))
    return top


def _config_primary_per_task() -> dict[str, str]:
    """Return {task: primary_model_default} from shared/config.py::TASKS."""
    text = CONFIG.read_text()
    # Match `"task": { ... "primary_model_default": "...",` (compact dict style).
    primary: dict[str, str] = {}
    for m in re.finditer(r'"(\w+)":\s*\{[^}]*?"primary_model_default":\s*"([^"]+)"', text):
        primary[m.group(1)] = m.group(2)
    return primary


def test_config_keys_are_subset_of_tasks():
    """Every task in config.py MUST be a bench-relevant task.

    Drift guard: a stale task key here would never get exercised by the runner
    and silently fall out of any top-N check.
    """
    expected = {"improve", "codeq_sum", "smart_trim", "web_synth", "code_gen"}
    actual = set(_config_primary_per_task().keys())
    assert expected.issubset(actual), (
        f"config.py TASKS missing canonical tasks: {expected - actual}"
    )


def test_ranking_present():
    """Sanity: RANKING.md exists and parses at least one top1 row."""
    top = _ranking_top1_per_task()
    assert top, f"RANKING.md at {RANKING} has no `## task | **1** | ...` rows"


def test_config_primary_matches_ranking_top1():
    """For each canonical task, config.py primary_model_default MUST equal
    RANKING.md top-1 model tag.

    Drift here is a HARD FAIL: the harness (`~/.claude/hooks/`) reads config
    to wire task-specific models into prompt-improve / smart-trim / etc. A
    stale config string = the harness silently falls back to `ollama` defaults.
    """
    canonical = {"improve", "codeq_sum", "smart_trim", "web_synth", "code_gen"}
    cfg = _config_primary_per_task()
    ranking = _ranking_top1_per_task()
    drift: list[tuple[str, str, str]] = []
    missing_ranking: list[str] = []
    for task in sorted(canonical):
        if task not in ranking:
            missing_ranking.append(task)
            continue
        cfg_model = cfg.get(task)
        rank_model = ranking[task]
        if cfg_model != rank_model:
            drift.append((task, cfg_model, rank_model))
    if missing_ranking:
        pytest.fail(f"RANKING.md has no top-1 row for canonical tasks: {missing_ranking}")
    if drift:
        msg = "\n".join(f"  - {t}: config={c!r} ranking={r!r}" for t, c, r in drift)
        pytest.fail(
            f"config.py primary_model_default drifted from RANKING.md top-1:\n{msg}\n"
            "Either update config.py to match RANKING (if RANKING is canonical), "
            "or update RANKING.md and re-run the bench."
        )


def test_no_known_typos_in_config_models():
    """Regression: catch the 8BB-GPU vs 8GB-GPU typo that lived for one cycle.

    If you add another model string with a similar foot-gun (transposed chars),
    add the typo + canonical form here.
    """
    text = CONFIG.read_text()
    typos = {
        "8BB-GPU": "8GB-GPU",  # 2026-07-05 round-3 typo
    }
    for typo, correct in typos.items():
        assert typo not in text, f"config.py contains known typo {typo!r}; expected {correct!r}"
