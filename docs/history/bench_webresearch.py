#!/usr/bin/env python3
"""Bench webresearch tasks (synthesize + focused_extract) across local models.

Measures the EXACT prompt the web_research engine uses, swapping only the model,
so we see real quality differences for the two generative tasks that shape the
final research output. query_profile is skipped (short JSON, high-freq, qwen3.5
already fine + has rule-based fallback).

Scoring is done by the controller reading the saved outputs (rubric below).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

SCRIPTS = Path("/home/eldi/.claude/scripts")
sys.path.insert(0, str(SCRIPTS))
# NOTE: do NOT add web_research/ to path — its http.py shadows stdlib `http`.

import ollama_client as oc  # noqa: E402

OUT = Path("/home/eldi/bench/ollama/results_webresearch")
OUT.mkdir(exist_ok=True)

CANDIDATES = [
    # Round-2: the OTHER strong models from today's lineup (gemma4 family + champs),
    # vs the round-1 references. Same fixture/rubric -> directly comparable.
    "jaahas/crow:9b",              # REF: round-1 synth winner (wire'd)
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf",  # REF: round-1 6/6 synth + 5/5 extract (best double)
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0",  # gemma4 code-champ 0.97, 13GB (NEW)
    "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",  # reason/longctx champ (NEW)
    "fredrezones55/Qwopus3.5:9b",  # reason alt (NEW)
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b",  # improve fast alt (NEW)
]

NUM_CTX = 16384  # match web_research/ollama_api.generate default

# ----------------------------------------------------------------------------
# FIXTURE 1: synthesize — 3 sources with: 1 fact confirmed by 2 sources,
# 1 contradiction between sources, 1 ambiguous/low-confidence fact, 1 version tag.
# ----------------------------------------------------------------------------
SYNTH_QUERY = "What is the default context window of the Acme-LLM v3 model, and is it stable across sources?"

SYNTH_DOCS = [
    {
        "title": "Acme-LLM v3 official release notes",
        "url": "https://example.com/acme-v3-release",
        "text": (
            "Acme-LLM v3 was released on 2026-03-15. The model ships with a default "
            "context window of 128,000 tokens. It supports a maximum output of 8,192 tokens. "
            "Pricing is $2 per million input tokens. A known issue causes crashes on inputs "
            "exceeding 120k tokens in streaming mode."
        ),
    },
    {
        "title": "Acme-LLM v3 migration guide",
        "url": "https://wiki.example.com/acme-v3-migrate",
        "text": (
            "When migrating from v2, note the context window is now 128k tokens by default. "
            "However, some users report the default dropping to 64k tokens when the "
            "low-memory preset is enabled in config.yaml. Tool-calling syntax changed to "
            "the 'tools=[...]' parameter. Released March 2026."
        ),
    },
    {
        "title": "Reddit discussion: Acme-LLM v3 context",
        "url": "https://reddit.example.com/r/acme/comments/123",
        "text": (
            "u/dev42: I think Acme-LLM v3 has a 200k context window, much bigger than v2. "
            "u/mod99: That's wrong, the docs say 128k. Please check official sources. "
            "u/dev42: oh you're right, my bad. No release date info here."
        ),
    },
]
# Ground truth for scoring:
#   - Default ctx = 128,000 tokens (src 1 + src 2 agree) → HIGH confidence, cite [1],[2]
#   - Contradiction: 200k claim (src 3, retracted) vs 128k (src 1,2) → should note
#   - Caveat: low-memory preset drops to 64k (src 2) → should mention as condition
#   - Released 2026-03-15 (src 1) / March 2026 (src 2) → optional
#   - Should NOT cite pricing/tool-calling/crash unless asked
#   - "stable across sources?" → answer NO (200k claim + 64k preset caveat)

# ----------------------------------------------------------------------------
# FIXTURE 2: focused_extract — a noisy page with nav, ads, 2 relevant paras,
# 1 irrelevant para, and a version tag.
# ----------------------------------------------------------------------------
EXTRACT_QUERY = "How do I configure retries on the Acme client?"
EXTRACT_INTENT = "docs"
EXTRACT_PAGE = """
Home | Docs | Pricing | Blog | Sign in   [search bar]   [cookie banner: accept all]

# Acme Client Documentation

Advertisements: Buy Acme Pro now! 50% off this week. Sponsored content.

## Installation
Install the Acme client with `pip install acme-client`. Requires Python 3.10+.

## Configuring Retries
The Acme client supports automatic retries for transient failures. Set the
`max_retries` parameter to an integer (default 3) when constructing the client.
Use exponential backoff by enabling `retry_backoff=True`. Available since
client version 2.4.0. Example: `client = Acme(max_retries=5, retry_backoff=True)`.

## Rate Limiting
The Acme API enforces 60 requests per minute on the free tier. Upgrade to Pro
for higher limits.

Newsletter signup form. Footer links: About, Careers, Contact.
"""
# Ground truth:
#   - Keep: max_retries param (default 3), retry_backoff=True, version 2.4.0, example
#   - Discard: nav, ads (Buy Acme Pro), rate-limit section, newsletter, install (tangential)
#   - Should mention version 2.4.0


def synth_prompt() -> tuple[str, str]:
    """Reproduce web_research.synthesis.synthesize prompt (non-structured, non-answer)."""
    ctx_parts = []
    for i, d in enumerate(SYNTH_DOCS, 1):
        ctx_parts.append(f"[{i}] {d['title']}\nURL: {d['url']}\n{d['text']}")
    context = "\n\n---\n\n".join(ctx_parts)
    system = (
        "You are a precise research analyst. Be factual, cite sources, no filler. "
        "Use only the provided sources."
    )
    style = (
        "Write a concise, well-organized synthesis of the sources answering the research query. "
        "Use bullet points and cite facts as [n] matching source numbers. "
        "Ignore marketing fluff. Note contradictions. "
        "Do NOT include a Sources section at the end; it will be appended automatically."
    )
    prompt = f"QUERY: {SYNTH_QUERY}\n\nSOURCES:\n{context}\n\n{style}"
    return prompt, system


def extract_prompt() -> tuple[str, str]:
    """Reproduce web_research.intelligence.focused_extract prompt."""
    system = (
        "You extract only information relevant to the user's query. "
        "Discard menus, ads, intros, and unrelated sections. "
        "Return: a concise answer (if any), one exact quote between quotes, "
        "and a note about date/version if present. If nothing is relevant, "
        "reply exactly: NO_RELEVANT_CONTENT."
    )
    prompt = (
        f"Query: {EXTRACT_QUERY}\nIntent: {EXTRACT_INTENT}\n"
        f"Page text:\n{EXTRACT_PAGE[:6000]}\n\nExtraction:"
    )
    return prompt, system


def run_model(model: str, prompt: str, system: str, temp: float) -> tuple[str, float]:
    full = f"{system}\n\n{prompt}" if system else prompt
    t0 = time.time()
    out = oc.generate(
        full, model=model, temperature=temp, num_ctx=NUM_CTX, cache=False,
        base_url="http://localhost:11434",
    )
    dt = time.time() - t0
    return (out or ""), dt


def leak_check(text: str) -> bool:
    return "</think>" in text or "<think>" in text


def main() -> int:
    report = {"synth": {}, "extract": {}}
    sp, ss = synth_prompt()
    ep, es = extract_prompt()

    for m in CANDIDATES:
        print(f"\n=== {m} ===", flush=True)
        # synth (temp 0.2 — matches synthesize)
        try:
            stext, sdt = run_model(m, sp, ss, 0.2)
            sleak = leak_check(stext)
        except Exception as e:  # noqa: BLE001
            stext, sdt, sleak = f"[ERR {e}]", 0, False
        print(f"  synth: {sdt:.1f}s leak={sleak} chars={len(stext)}", flush=True)
        report["synth"][m] = {"text": stext, "dt": sdt, "leak": sleak}

        # extract (temp 0.1 — matches focused_extract)
        try:
            etext, edt = run_model(m, ep, es, 0.1)
            eleak = leak_check(etext)
        except Exception as e:  # noqa: BLE001
            etext, edt, eleak = f"[ERR {e}]", 0, False
        print(f"  extract: {edt:.1f}s leak={eleak} chars={len(etext)}", flush=True)
        report["extract"][m] = {"text": etext, "dt": edt, "leak": eleak}

    stamp = "2026-06-28_r2"
    raw = OUT / f"bench_{stamp}.json"
    raw.write_text(json.dumps(report, indent=2))
    print(f"\nSaved raw -> {raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
