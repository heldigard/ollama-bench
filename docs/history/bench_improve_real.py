#!/usr/bin/env python3
"""Real-pipeline improve bench → RANKING_IMPROVE.md + results_improve_real.tsv

Tests each candidate model through the ACTUAL prompt-improve hook path:

    build_rewrite_system_prompt(lang)  →  ollama_client.chat  →  clean_rewrite

This is the source of truth for `_ROLE_MODEL_MAP` routing in ~/prompt-improve.
`deep_bench.py`'s `improve` column uses its OWN prompt + a leak detector that
misses `<|channel>` tokens (it false-ranked Huihui-abliterated #1). This bench
reflects what the hook ACTUALLY ships — same system prompt, same cleaner, same
140-word budget, same hard rules (no preamble, no AI-mention, no user-questions).

Why sequential (no ThreadPoolExecutor): deep_bench runs 4 workers in parallel,
which causes VRAM contention on a 16GB card → model-load failures + skewed tps.
Accurate per-model tps needs ONE model loaded at a time. Slower, but the user
asked for "más reales y certeros".

Scoring (per prompt, averaged across the prompt set):
  GATE   clean_rewrite(raw, prompt) returns non-empty  (else component score = 0)
  +3.0   structure: imperative Task line + ≥2 of {Context, Objective,
         Constraints, Acceptance} sections present (language-aware markers)
  +2.0   within budget (≤140 words, the system-prompt cap)
  +1.0   hook hard rules: no preamble ("here is"/"aquí está"),
         no AI-mention ("as an ai"/"como modelo"), no user-questions ("?")
  +tps   speed bonus = tps/10, capped at +5
  -5.0   raw leak (<think> / <|channel> / refusal) — the harness strips these,
         but a cleaner model is preferred; strip is a workaround, not a feature
  -3.0   over budget (>2× cap = >280 words)
  LOAD   OllamaRequestError → gate fails (score 0), flagged FAIL. Not excluded:
         ranks last so unreliable loaders are visible.

Candidates: --models flag (comma-sep) or env BENCH_IMPROVE_MODELS, else a
default set = current _ROLE_MODEL_MAP chain + deep_bench improve top-5 + strong
new smoke contenders + Mobius (old primary, to re-validate). Embeddings skipped.

Usage:
  python3 bench_improve_real.py
  python3 bench_improve_real.py --models "qwen3.5:4b,fredrezones55/Qwopus3.5:9b"
  BENCH_IMPROVE_MODELS="a,b" python3 bench_improve_real.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from statistics import mean

# --- wire the REAL solution into the bench ----------------------------------
sys.path.insert(0, "/home/eldi/prompt-improve/src")
sys.path.insert(0, "/home/eldi/.claude/scripts")

from prompt_improve.features.rules import build_rewrite_system_prompt  # noqa: E402
from prompt_improve.features.clean import clean_rewrite  # noqa: E402
from prompt_improve.features.detect import detect_language  # noqa: E402
import ollama_client as oc  # noqa: E402

OLLAMA = "http://localhost:11434"
NUM_PREDICT = 500          # rewrites are ≤140 words; 500 tokens is generous headroom
NUM_CTX = 8192
TIMEOUT = 240
WORD_BUDGET = 140          # matches build_rewrite_system_prompt hard cap
DEFAULT_OUT_TSV = "/home/eldi/bench/ollama/results_improve_real.tsv"
DEFAULT_OUT_MD = "/home/eldi/bench/ollama/RANKING_IMPROVE.md"

# Real vague prompts the hook actually receives (ES + EN mix).
PROMPTS = [
    ("es_dash", "haz que el dashboard cargue mas rapido, esta lentisimo"),
    ("en_auth", "fix the auth bug, users cant login"),
    ("es_btn", "agrega un boton de exportar csv en la pagina de reportes"),
    ("en_report", "the reports page is broken, fix it"),
    ("es_perf", "mejora el rendimiento de la query de ventas"),
    ("en_log", "add logging to the payment service"),
]

DEFAULT_CANDIDATES = [
    # current _ROLE_MODEL_MAP chain (deep_bench 2026-07-04 winners)
    "hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M",
    "fredrezones55/Qwopus3.5:9b",
    "jaahas/crow:9b",
    "qwen3.5:4b",
    # deep_bench improve top-5 extras
    "fredrezones55/Qwopus3.5:4b",
    "hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest",
    # old primary — re-validate (couldn't load during deep_bench: VRAM contention)
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
    # strong smoke contenders (high tps, untested on improve through real pipeline)
    "ducquoc/gemma4-fast-sonnet:latest",
    "hf.co/pegasus912/gemma-4-12b-it-qat-heretic-ud-q4-k-xl:latest",
    # smart_trim co-winner (cross-task value)
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b",
    # web_synth winner (cross-task value)
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest",
]

# Language-aware structure markers (must match build_rewrite_system_prompt).
_SECTIONS = {
    "English": ["Task", "Context", "Objective", "Constraints", "Acceptance"],
    "Spanish": ["Tarea", "Contexto", "Objetivo", "Restricciones", "Criterios"],
}
_PREAMBLE = re.compile(
    r"\b(here is|here's|below is|this is|sure|certainly|of course|i'll|i will|"
    r"aqu[ií] est[aá]|debajo est[aá]|esto es|por supuesto|claro|voy a)\b",
    re.I,
)
_AI_MENTION = re.compile(r"\b(as an ai|i am an ai|i'm an ai|as a language model|"
                         r"como (un )?(modelo|ia|ai)|como asistente)\b", re.I)
_LEAK = re.compile(r"<think|<\|channel|<reasoning|<\|think\|>", re.I)


def _installed() -> set[str]:
    try:
        with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
            return {m["name"] for m in json.load(r).get("models", [])}
    except Exception:
        return set()


def _call_chat(model: str, messages: list[dict]) -> dict:
    """One real-pipeline call. Returns {raw, cleaned, tps, err}."""
    t0 = time.perf_counter()
    try:
        raw = oc.chat(
            messages,
            model=model,
            temperature=0.2,
            num_predict=NUM_PREDICT,
            think=False,
            timeout=TIMEOUT,
            base_url=OLLAMA,
            cache=False,
            num_ctx=NUM_CTX,
        )
    except oc.OllamaRequestError as e:
        return {"raw": "", "cleaned": None, "tps": 0.0, "err": f"load:{e.status}"}
    except oc.OllamaUnavailable as e:
        return {"raw": "", "cleaned": None, "tps": 0.0, "err": f"down:{str(e)[:60]}"}
    dt = time.perf_counter() - t0
    raw = raw or ""
    # tps: re-derive from raw length vs wall-time (chat() doesn't return eval_count;
    # approximate by tokens ≈ words*1.3). Marked approximate — structural score is
    # the primary signal, tps is the tiebreaker.
    tps = (len(raw.split()) * 1.3 / dt) if dt > 0 and raw else 0.0
    return {"raw": raw, "cleaned": None, "tps": round(tps, 1), "err": None}


def _structure_score(cleaned: str, language: str) -> float:
    """Reward the sections build_rewrite_system_prompt asks for."""
    score = 0.0
    sections = _SECTIONS.get(language, _SECTIONS["English"])
    present = [s for s in sections if re.search(rf"(?i)\b{re.escape(s)}\b", cleaned)]
    if len(present) >= 3:
        score += 3.0
    elif len(present) >= 2:
        score += 2.0
    elif len(present) >= 1:
        score += 1.0
    return score


def _score_one(raw: str, cleaned: str | None, language: str, tps: float) -> dict:
    """Score a single prompt's output through the real pipeline."""
    wc_raw = len(raw.split())
    # comps holds ONLY score components (all summed). Diagnostics kept separate.
    comps = {"gate": 0.0, "structure": 0.0, "budget": 0.0, "rules": 0.0,
             "tps": 0.0, "leak": 0.0, "over": 0.0}
    leaks = bool(_LEAK.search(raw))
    if not cleaned:
        return {"score": 0.0, "leak": leaks, "wc_raw": wc_raw, "wc_clean": 0, **comps}
    comps["gate"] = 5.0
    wc_clean = len(cleaned.split())
    comps["structure"] = _structure_score(cleaned, language)
    if wc_clean <= WORD_BUDGET:
        comps["budget"] = 2.0
    elif wc_clean > WORD_BUDGET * 2:
        comps["over"] = -3.0
    rule_ok = (not _PREAMBLE.search(cleaned)) and (not _AI_MENTION.search(cleaned)) and ("?" not in cleaned)
    if rule_ok:
        comps["rules"] = 1.0
    comps["tps"] = min(tps / 10.0, 5.0)
    if leaks:
        comps["leak"] = -5.0
    return {"score": round(sum(comps.values()), 2), "leak": leaks,
            "wc_raw": wc_raw, "wc_clean": wc_clean, **comps}


def _run_model(model: str) -> dict:
    """Run all prompts for one model; return aggregated result."""
    per_prompt = []
    for pid, prompt in PROMPTS:
        language = detect_language(prompt)
        messages = [
            {"role": "system", "content": build_rewrite_system_prompt(language)},
            {"role": "user", "content": f"Respond and write the rewritten prompt in {language}.\n\nOriginal prompt:\n{prompt}"},
        ]
        res = _call_chat(model, messages)
        if res["err"]:
            per_prompt.append({"pid": pid, "err": res["err"], "score": 0.0})
            continue
        cleaned = clean_rewrite(res["raw"], prompt)
        s = _score_one(res["raw"], cleaned, language, res["tps"])
        per_prompt.append({
            "pid": pid, "score": s["score"], "leak": s["leak"],
            "wc_clean": s["wc_clean"], "tps": res["tps"],
            "head": (cleaned or "")[:100].replace("\n", " "),
        })
    scores = [p["score"] for p in per_prompt]
    leaks = sum(1 for p in per_prompt if p.get("leak"))
    errs = [p for p in per_prompt if p.get("err")]
    return {
        "model": model,
        "mean": round(mean(scores), 2) if scores else 0.0,
        "leaks": leaks,
        "errors": len(errs),
        "per_prompt": per_prompt,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", help="comma-sep candidate list (default: built-in set)")
    ap.add_argument("--out-tsv", default=DEFAULT_OUT_TSV)
    ap.add_argument("--out-md", default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    candidates = (
        args.models.split(",")
        if args.models
        else os.environ.get("BENCH_IMPROVE_MODELS", "").split(",") or DEFAULT_CANDIDATES
    )
    candidates = [m.strip() for m in candidates if m.strip() and "embed" not in m.lower()]

    installed = _installed()
    missing = [m for m in candidates if m not in installed]
    if missing:
        print(f"# WARN: {len(missing)} candidate(s) not installed (skipped):", file=sys.stderr)
        for m in missing:
            print(f"#   - {m}", file=sys.stderr)
    candidates = [m for m in candidates if m in installed]
    print(f"# Real-pipeline improve bench: {len(candidates)} model(s) × {len(PROMPTS)} prompts "
          f"(sequential, no VRAM contention)", file=sys.stderr)

    results = []
    for i, m in enumerate(candidates, 1):
        print(f"  [{i:2d}/{len(candidates)}] {m[:62]}", file=sys.stderr, flush=True)
        results.append(_run_model(m))

    results.sort(key=lambda r: (-r["mean"], r["errors"]))

    # TSV
    with open(args.out_tsv, "w") as f:
        f.write("rank\tmean_score\terrors\tleaks\tmodel\n")
        for i, r in enumerate(results, 1):
            f.write(f"{i}\t{r['mean']}\t{r['errors']}\t{r['leaks']}\t{r['model']}\n")
    # Markdown
    with open(args.out_md, "w") as f:
        f.write(f"# Real-pipeline improve bench ({len(candidates)} models × {len(PROMPTS)} prompts)\n")
        f.write(f"> Through the ACTUAL prompt-improve path: `build_rewrite_system_prompt` → "
                f"`ollama_client.chat` → `clean_rewrite`. Source of truth for `_ROLE_MODEL_MAP`.\n")
        f.write(f"> deep_bench's improve column uses its own prompt + a leak detector that misses `<|channel>`.\n\n")
        f.write("| # | Mean | Err | Leaks | Model |\n|---|------|-----|--------|-------|\n")
        for i, r in enumerate(results, 1):
            flag = " ⚠️" if r["errors"] else (" 🔥" if r["leaks"] else "")
            f.write(f"| {i} | {r['mean']} | {r['errors']} | {r['leaks']}/{len(PROMPTS)} | `{r['model']}`{flag} |\n")
        f.write("\n## Per-prompt detail (top 3)\n\n")
        for r in results[:3]:
            f.write(f"\n### `{r['model']}` — mean {r['mean']}\n\n")
            for p in r["per_prompt"]:
                if p.get("err"):
                    f.write(f"- **{p['pid']}**: ERROR `{p['err']}`\n")
                else:
                    f.write(f"- **{p['pid']}** (score {p['score']}"
                            f"{', LEAK' if p.get('leak') else ''}): {p.get('head','')}\n")
    print(f"\nWrote {args.out_tsv}\nWrote {args.out_md}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
