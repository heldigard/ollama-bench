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

from ollama_bench.shared.config import SPECIALIZED_TASKS, TASKS

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
    in_primary_table = False
    for line in text.splitlines():
        if line.startswith("## Per-task PRIMARY"):
            in_primary_table = True
            current_task = None
            continue
        m = re.match(r"^##\s+(\w+)", line)
        if m:
            in_primary_table = False
            current_task = m.group(1)
            continue
        if in_primary_table:
            summary = re.match(r"^\|\s*(\w+)\s*\|\s*`([^`]+)`", line)
            if summary:
                tag = re.sub(r"\s+←.*$", "", summary.group(2))
                top[summary.group(1)] = tag
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
    """Return the imported canonical + specialized primary registry."""
    return {
        task: str(cfg["primary_model_default"])
        for task, cfg in {**TASKS, **SPECIALIZED_TASKS}.items()
    }


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


def test_canonical_tasks_declare_consumer_protocol():
    assert {task: cfg.get("protocol") for task, cfg in TASKS.items()} == {
        "improve": "chat-fallback",
        "codeq_sum": "generate",
        "smart_trim": "chat-fallback",
        "web_synth": "generate",
        "code_gen": "generate",
    }


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
            drift.append((task, cfg_model or "<missing>", rank_model))
    if missing_ranking:
        pytest.fail(f"RANKING.md has no top-1 row for canonical tasks: {missing_ranking}")
    if drift:
        msg = "\n".join(f"  - {t}: config={c!r} ranking={r!r}" for t, c, r in drift)
        pytest.fail(
            f"config.py primary_model_default drifted from RANKING.md top-1:\n{msg}\n"
            "Either update config.py to match RANKING (if RANKING is canonical), "
            "or update RANKING.md and re-run the bench."
        )


def test_specialized_config_primary_matches_ranking_top1():
    cfg = _config_primary_per_task()
    ranking = _ranking_top1_per_task()
    drift = {
        task: (cfg[task], ranking.get(task))
        for task in SPECIALIZED_TASKS
        if ranking.get(task) != cfg[task]
    }
    assert not drift, f"specialized task config drifted from RANKING.md: {drift}"


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


def test_tertiary_model_in_ranking_top_n():
    """When config.py declares a `tertiary_model` for a canonical or specialized
    task, RANKING.md MUST list it in that task's top-N rows (default N=3).

    Round-9 added tertiary_model to codeq_sum (`SetneufPT` after the Qwythos
    primary and batiai fallback). Round-10 added tertiary_model to improve
    (`cryptidbleh` after TeichAI primary and Negentropy-9B fallback). Without
    this guard, a future rewire that demotes a tertiary to fallback-or-below
    leaves a stale chain entry pointing at a model that's no longer in the
    top-N — and downstream consumers using the 3rd-chain tier would silently
    drift to a model that wasn't validated for that task.
    """
    ranking = _ranking_top1_per_task()
    cfg_tertiary = {
        task: cfg.get("tertiary_model")
        for task, cfg in {**TASKS, **SPECIALIZED_TASKS}.items()
        if cfg.get("tertiary_model")
    }
    # RANKING.md parser currently captures top-1; extend it to top-N.
    text = RANKING.read_text().splitlines()
    in_task: dict[str, str] = {}
    current_task: str | None = None
    for line in text:
        m = re.match(r"^##\s+(\w+)", line)
        if m:
            current_task = m.group(1)
            in_task.setdefault(current_task, "")
            continue
        if current_task is None:
            continue
        # Capture every backticked model tag in rows under each `## task`.
        for tag in re.findall(r"`([^`]+)`", line):
            if tag in {current_task, "model", "task"}:
                continue
            in_task[current_task] = (in_task[current_task] + "\n" + tag).strip()
    missing: list[tuple[str, str]] = []
    for task, tertiary in cfg_tertiary.items():
        if not ranking.get(task):
            continue  # drift test will catch this separately
        if tertiary not in in_task.get(task, ""):
            missing.append((task, tertiary))
    if missing:
        msg = "\n".join(
            f"  - {t}: tertiary_model={m!r} not in RANKING.md top-N" for t, m in missing
        )
        pytest.fail(
            f"config.py tertiary_model not aligned with RANKING.md:\n{msg}\n"
            "Either remove the tertiary_model from config.py (single-tier fallback), "
            "or add the model to RANKING.md's task table (rows 2 or 3)."
        )


# ---------------------------------------------------------------------------
# Score-consistency guard (anti name-bias / circular-justification)
# ---------------------------------------------------------------------------
# Tasks whose RANKING.md table is single-rubric (every row scored under the
# same rubric / comparable rounds). Only these are score-guarded. Tasks that mix
# rubrics or rounds (improve, web_synth) can have a #1 with a LOWER raw score
# than a #2 from a different rubric — guarding them would false-positive. Add a
# task here only after confirming its whole table is single-rubric.
SCORE_GUARDED_TASKS = {"smart_trim", "codeq_sum"}
# Tolerance: a contender within DELTA of the primary is a tie (noise), not a
# quality inversion. Round-15's gap (11.67 vs 10.79 = 0.88) clears it easily.
SCORE_GUARD_DELTA = 0.3


def _parse_ranking_scores(text: str) -> dict[str, list[tuple[float, str, str]]]:
    """Parse RANKING.md text → {task: [(score, model_tag, annotation)]}.

    annotation ∈ {"current", "held", "deleted", "candidate"}:
      - ``candidate`` — rank column literally reads "candidate"
      - ``held``     — row mentions "held" or a "(round-N …)" historical marker
      - ``deleted``  — row mentions "deleted"
      - ``current``  — everything else with a parseable numeric score

    score = first float in the row (the deep/score column). Header, separator,
    and narrative rows are skipped. The model tag strips trailing ``← note``
    annotations and is what config.py primary strings are compared against.
    """
    by_task: dict[str, list[tuple[float, str, str]]] = {}
    current_task: str | None = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(\w+)", line)
        if m:
            current_task = m.group(1)
            continue
        if current_task is None or not line.lstrip().startswith("|"):
            continue
        if line.lstrip().startswith("| #"):
            continue  # header row
        if set(line) <= set("|- "):
            continue  # separator row
        tag_match = re.search(r"`([^`]+)`", line)
        nums = re.findall(r"-?\d+\.\d+", line)
        if not tag_match or not nums:
            continue
        tag = re.sub(r"\s+←.*$", "", tag_match.group(1))
        try:
            score = float(nums[0])
        except ValueError:
            continue
        low = line.lower()
        if "deleted" in low:
            ann = "deleted"
        elif line.split("|")[1].strip() == "candidate":
            ann = "candidate"
        elif "held" in low or re.search(r"\(round-\d", low):
            ann = "held"
        else:
            ann = "current"
        by_task.setdefault(current_task, []).append((score, tag, ann))
    return by_task


def _primary_score_violations(
    ranking_text: str,
    primaries: dict[str, str],
    guarded: set[str],
    delta: float = SCORE_GUARD_DELTA,
) -> list[tuple[str, str, float, list[str], float]]:
    """Return [(task, primary, primary_score, [better_models], best_score)] for
    each guarded task whose cabled primary is NOT the top scorer among its
    current+candidate rows (beyond ``delta``).

    Pure function so the regression test can feed it the round-15 buggy
    snapshot directly without monkeypatching the module-level ``RANKING`` path.
    """
    rows_by_task = _parse_ranking_scores(ranking_text)
    out: list[tuple[str, str, float, list[str], float]] = []
    for task in guarded:
        rows = rows_by_task.get(task, [])
        contenders = [(s, t) for s, t, _ in rows if _ is not None and _ in ("current", "candidate")]
        if not contenders:
            continue
        primary = primaries.get(task, "")
        best = max(s for s, _ in contenders)
        primary_scores = [s for s, t in contenders if t == primary]
        if not primary_scores:
            continue  # the drift test covers a missing primary separately
        if primary_scores[0] < best - delta:
            better = sorted({t for s, t in contenders if s > primary_scores[0] + delta})
            out.append((task, primary, primary_scores[0], better, best))
    return out


def test_primary_is_highest_score_in_single_rubric_tasks():
    """Anti name-bias guard — see systemPatterns.md (round-15, 2026-07-13).

    For SCORE_GUARDED_TASKS, the config primary MUST be the top scorer among
    its current+candidate rows (within DELTA). A lower-scoring primary signals a
    non-governing metric was used to discard a quality win — exactly the
    round-15 bug where SC117 (10.79) was cabled over batiai-e2b (11.67) with a
    circular "throughput is non-decisive" argument. held/deleted rows are
    excluded (different rubric / removed from lineup).
    """
    cfg = _config_primary_per_task()
    violations = _primary_score_violations(RANKING.read_text(), cfg, SCORE_GUARDED_TASKS)
    assert not violations, (
        "config primary is NOT the top scorer in its task — quality-over-speed "
        "violation (see systemPatterns.md round-15 anti-pattern):\n"
        + "\n".join(
            f"  - {t}: primary={p!r} score={ps:.2f}, but higher-scoring {b} "
            f"(max={mx:.2f}) — promote the argmax or annotate the row as held."
            for t, p, ps, b, mx in violations
        )
    )


def test_score_guard_would_have_caught_round15_bug():
    """Regression: the round-15 smart_trim table that motivated this guard MUST
    trip it. Pins the guard's intent so a future weakening (larger DELTA,
    dropping a task from SCORE_GUARDED_TASKS, a parser change) can't silently
    re-open the hole it was written to close.
    """
    buggy_ranking = (
        "## smart_trim\n\n"
        "| # | deep | tiebreak | model |\n|---|---|---|---|\n"
        "| **1** | 10.79 | established incumbent | `hf.co/SC117/x` |\n"
        "| 2 | 9.87 | fallback | `hf.co/HauhauCS/y` |\n"
        "| candidate | 11.67 | one round | `batiai/gemma4-e2b:q4` |\n"
    )
    violations = _primary_score_violations(
        buggy_ranking,
        {"smart_trim": "hf.co/SC117/x"},
        {"smart_trim"},
    )
    assert violations, (
        "score-consistency guard failed to detect the round-15 bug: SC117 "
        "(10.79) cabled as primary over batiai-e2b (11.67). The guard must "
        "fire on this snapshot."
    )
    assert violations[0][0] == "smart_trim"
    assert "batiai/gemma4-e2b:q4" in violations[0][3]
