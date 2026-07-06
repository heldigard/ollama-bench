"""Score saturation contract.

Locks down the scoring caps documented in scorer.py docstrings + CLAUDE.md
("per-task cap-of-7.0 makes 20+ models tie" → tie_break for discrimination).

If the first_pass cap moves (e.g., 7.00 → 7.50), the saturating tier shifts and
every RANKING comparison invalidates. These tests assert the cap explicitly.
"""

from __future__ import annotations

from ollama_bench.shared.scorer import (
    first_pass_score,
    quality_score,
    structural_score,
    tie_break_score,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clean_res(out: str, *, tps: float, etoks: int, done: str = "stop") -> dict:
    """Build a result dict that LOOKS like a clean first-pass response."""
    return {"out": out, "tps": tps, "etoks": etoks, "done": done}


# ---------------------------------------------------------------------------
# 1) structural_score cap (0..10)
# ---------------------------------------------------------------------------


def test_structural_score_caps_at_10():
    """At max sections + keywords, score saturates at 10.0, not higher."""
    out = "## GOAL ## STEPS ## ACCEPTANCE ## RESULT ## TESTS foo bar baz qux"
    # 5 sections × 2.0 = 10.0 from sections alone
    sc = structural_score(
        out,
        expected_sections=("## GOAL", "## STEPS", "## ACCEPTANCE", "## RESULT", "## TESTS"),
        must_have=("foo", "bar", "baz", "qux"),  # 4 × 1.5 = 6.0 (would push >10)
    )
    assert sc == 10.0, f"structural_score must cap at 10.0; got {sc}"


def test_structural_score_only_sections():
    out = "## GOAL\n## STEPS\n## ACCEPTANCE"
    sc = structural_score(
        out,
        expected_sections=("## GOAL", "## STEPS", "## ACCEPTANCE"),
    )
    assert sc == 6.0


# ---------------------------------------------------------------------------
# 2) quality_score cap (0..10)
# ---------------------------------------------------------------------------


def test_quality_score_caps_at_10():
    """6 keywords × 2.0 = 12, must clamp to 10.0."""
    # Keywords MUST appear in the output for the score to grow.
    out = " k0 k1 k2 k3 k4 k5 "  # all 6 keywords present
    sc = quality_score(out, keywords=tuple(f"k{i}" for i in range(6)))
    assert sc == 10.0, f"quality_score must cap at 10.0 with 6 present kw; got {sc}"


# ---------------------------------------------------------------------------
# 3) first_pass_score cap (~7.0 saturating tier)
# ---------------------------------------------------------------------------


def test_first_pass_score_clean_short_saturates_at_7():
    """Clean + short + fast response must hit the +7.0 saturating tier.

    Without this cap, every top-quality model would get a unique score (and
    tie_break would never be needed). The cap is the WHOLE POINT of the
    smoke → deep → tie-break pipeline. DON'T lower it without updating
    `topics/bench-methodology.md` AND every RANKING.md.
    """
    # Clean + very-short (10 words vs budget=120) + max-thr tps (50 → +5 bonus).
    res = _clean_res("one two three four five six seven eight nine ten", tps=50.0, etoks=10)
    sc = first_pass_score("any", res, budget=120)
    # Expected: +2 (under-budget) + 5 (tps cap) = 7.0.
    assert sc == 7.0, f"expected saturating first_pass=7.0; got {sc}"


def test_first_pass_score_penalizes_think_leak():
    """A 5-point penalty if 'think>' or 'thinking process' appears in output."""
    res_clean = _clean_res("hi there", tps=10.0, etoks=5)
    sc_clean = first_pass_score("any", res_clean, budget=120)
    res_leak = _clean_res("hi  think> there", tps=10.0, etoks=5)
    sc_leak = first_pass_score("any", res_leak, budget=120)
    assert sc_leak < sc_clean
    # Penalty -5 means the leak loses at least 5 points vs the clean baseline.
    assert sc_clean - sc_leak >= 5.0, (
        f"first_pass think-leak penalty should be ≥5; delta={sc_clean - sc_leak}"
    )


def test_first_pass_score_penalizes_refusal():
    """A different model emits 'as an ai' — also -5 penalty."""
    res_clean = _clean_res("hi there", tps=10.0, etoks=5)
    res_refusal = _clean_res("I cannot help with that", tps=10.0, etoks=5)
    assert first_pass_score("any", res_refusal, budget=120) < first_pass_score(
        "any", res_clean, budget=120
    )


def test_first_pass_score_penalizes_truncation_at_budget():
    """If done='length' and etoks >= 190 (used all num_predict=200 budget),
    the response is truncated → -2 penalty."""
    res_clean_stop = _clean_res("hi", tps=10.0, etoks=5, done="stop")
    res_truncated = _clean_res("hi", tps=10.0, etoks=195, done="length")
    sc_clean = first_pass_score("any", res_clean_stop, budget=120)
    sc_trunc = first_pass_score("any", res_truncated, budget=120)
    assert sc_trunc < sc_clean
    assert sc_clean - sc_trunc >= 2.0


def test_first_pass_score_empty_response_heavy_penalty():
    """Empty output is scored MUCH worse than a comparable clean response.

    The scorer applies -10 for empty AND +2 for under-budget, so the absolute
    delta-vs-clean matters more than the raw number. The contract: empty is
    at least 5 points worse than the same model returning a short answer.
    """
    res_empty = _clean_res("", tps=0.0, etoks=0)
    res_clean = _clean_res("hi", tps=0.0, etoks=1)
    sc_empty = first_pass_score("any", res_empty, budget=120)
    sc_clean = first_pass_score("any", res_clean, budget=120)
    assert sc_clean - sc_empty >= 5.0, (
        f"empty response should score ≥5 worse than a short clean response; "
        f"got clean={sc_clean} empty={sc_empty}"
    )


def test_first_pass_score_error_returns_sentinel():
    """err= marker → -100.0 sentinel (lets downstream sort drop it from ranking)."""
    sc = first_pass_score("any", {"err": "boom"}, budget=120)
    assert sc == -100.0


# ---------------------------------------------------------------------------
# 4) tie_break_score: NO cap (range ~ -10 .. +15)
# ---------------------------------------------------------------------------


def test_tie_break_score_no_cap_in_high_band():
    """Tie-break has NO structural cap: high structural_score + tps_bonus +
    no tps penalty can exceed 10.

    Regression guard: if someone 'helpfully' adds a `min(s, 10.0)` clamp here,
    tie-break becomes useless (re-saturates just like first_pass).
    """
    res = _clean_res(
        "## GOAL ## ASSUMPTIONS ## STEPS ## ACCEPTANCE a b c d e f g h",
        tps=50.0,
        etoks=20,
    )

    def high_scorer(out: str) -> float:
        # Pretend a custom scoring callback returns 12.0 structural + keywords.
        return 12.0

    sc = tie_break_score(res, high_scorer, budget=250)
    # structural=12 + tps_bonus (capped at 3.0) = ≥15.
    assert sc > 10.5, (
        f"tie_break has no cap; expected > 10.5 to discriminate; got {sc}. "
        "If someone added `min(s, 10.0)` here, remove it — the whole point "
        "of tie_break is uncapped scoring to break 7.0 saturating ties."
    )


def test_tie_break_score_think_penalty_stronger_than_first_pass():
    """Tie-break think-leak penalty (-8) must exceed first_pass (-5) so the
    tie-break is STRICTER about leaks. Otherwise we'd let leaky models into
    the next pipeline phase."""
    res_clean = _clean_res("## GOAL hi", tps=10.0, etoks=5)
    res_leak = _clean_res("## GOAL  think>", tps=10.0, etoks=5)
    sc_clean = tie_break_score(res_clean, lambda o: 2.0, budget=250)
    sc_leak = tie_break_score(res_leak, lambda o: 2.0, budget=250)
    delta = sc_clean - sc_leak
    assert delta >= 8.0, (
        f"tie_break think penalty should be ≥8; got delta={delta}. "
        f"(first_pass uses -5; tie_break should be STRICTER.)"
    )


def test_tie_break_score_error_returns_sentinel():
    sc = tie_break_score({"err": "boom"}, lambda o: 0.0, budget=250)
    assert sc == -100.0
