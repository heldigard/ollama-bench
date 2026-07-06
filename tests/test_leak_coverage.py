"""Leak-pattern coverage — exhaustively exercise every LEAK_PATTERNS entry.

Closes the gap where test_scorer only spot-checked ~6 of 14 patterns. A new
pattern added to LEAK_PATTERNS without a row here = the test name shows up red,
forcing the author to confirm the new pattern actually fires.

If detect_leaks() regresses on ANY of these (Ollama version bump, model swap),
the smoke gate would let a leaky model through → 24+ minutes of wasted deep
bench on a model that should have been disqualified.
"""

from __future__ import annotations

import pytest

from ollama_bench.shared.scorer import (
    LEAK_PATTERNS,
    STRIPPABLE_TAGS,
    detect_leaks,
    leaks_are_strippable,
)

# (substring_to_inject, expected_tag). Substring is in a neutral host sentence
# so we test the regex, not prefix-matching quirks.
LEAK_FIXTURES: list[tuple[str, str]] = [
    # Thinking-trace tags (strippable)
    ("<think>plan</think>", "think_tag"),
    ("<think>orphan", "think_tag"),
    ("</think>", "think_tag_close"),
    ("<reasoning>step 1</reasoning>", "reasoning_tag"),
    ("<reflection>hmm</reflection>", "reflection_tag"),
    ("<output>final</output>", "output_tag"),
    ("<|channel|>thought<|channel|>", "channel_token"),
    # Visible thinking prefixes (strippable)
    ("Thinking Process: 1. foo", "thinking_process"),
    ("Let me think: about it", "thinking_prefix"),
    # Refusal / stuck (NOT strippable)
    ("Sorry, as an AI, I cannot.", "refusal_pattern"),
    ("As a language model, I...", "refusal_pattern"),
    ("I cannot help with that.", "refusal_pattern"),
    ("I'm just an AI, I can't know.", "refusal_pattern"),
    ("I'm unable to access that.", "refusal_pattern"),
    ("I am unable to comply.", "refusal_pattern"),
    ("I'm having an issue processing.", "stuck_response"),
]


@pytest.mark.parametrize("text,expected_tag", LEAK_FIXTURES)
def test_each_leak_pattern_fires(text: str, expected_tag: str):
    """Every LEAK_FIXTURES row MUST trip detect_leaks() for its expected tag.

    If you ADD a pattern to LEAK_PATTERNS, add a row here. If a row fails,
    the regex for that tag is broken (rename, typo, scope change).
    """
    leaks = detect_leaks(text)
    assert expected_tag in leaks, f"expected {expected_tag!r} in leaks for {text!r}; got {leaks}"


def test_every_leak_pattern_tag_has_fixture():
    """Every tag in LEAK_PATTERNS MUST have ≥1 fixture in LEAK_FIXTURES.

    Forces coverage discipline: a new pattern without a fixture fails here.
    """
    fixture_tags = {tag for _, tag in LEAK_FIXTURES}
    pattern_tags = {tag for _, tag in LEAK_PATTERNS}
    missing = pattern_tags - fixture_tags
    assert not missing, (
        f"LEAK_PATTERNS tags without a fixture in LEAK_FIXTURES: {sorted(missing)}. "
        "Add a row to LEAK_FIXTURES for each."
    )


def test_clean_text_emits_no_leaks():
    """Real code summary must NOT trip the gate (false-positive guard)."""
    clean = (
        "Returns the parsed schema as a dict. Raises ValueError on malformed input. "
        "Side effects: none. Idempotent."
    )
    assert detect_leaks(clean) == []


def test_strippable_tags_classified_correctly():
    """Each strippable fixture must be salvageable; each refusal must NOT."""
    strippable_tag_set = STRIPPABLE_TAGS
    for text, tag in LEAK_FIXTURES:
        leaks = detect_leaks(text)
        if tag in strippable_tag_set:
            # Pure strippable fixture → salvageable.
            # (May include multiple tags; all must be strippable.)
            assert leaks_are_strippable(leaks), (
                f"fixture {tag!r} should be strippable but leaks={leaks}"
            )
        else:
            # Refusal / stuck → NOT strippable.
            assert not leaks_are_strippable(leaks), (
                f"fixture {tag!r} should NOT be strippable but leaks={leaks}"
            )


def test_detect_leaks_case_insensitive():
    """Mixed-case variants must still fire (some models emit 'Thinking Process')."""
    assert "thinking_process" in detect_leaks("THINKING PROCESS: hello")
    assert "refusal_pattern" in detect_leaks("AS AN AI, I CANNOT")
    assert "think_tag" in detect_leaks("<THINK>x</THINK>")


def test_detect_leaks_empty_and_whitespace():
    """Empty / whitespace-only inputs are safe no-ops."""
    assert detect_leaks("") == []
    assert detect_leaks("   \n\t  ") == []
    # None is tolerated (the scorer is called with res.get('out', '') which can be None).
    assert detect_leaks(None) == []  # type: ignore[arg-type]
