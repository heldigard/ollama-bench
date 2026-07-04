"""lfm_variant — codeq summary tie-break for LFM family (think-strip).

All 9 LFM variants (LiquidAI/batiai/nathanrchn/sliderforthewin/Huihui-LFM/
gaston-parravicini/DuoNeural/brownsauto) leak thinking despite think=False on
Ollama 0.23.2. This slice strips <think> tags BEFORE scoring so we can compare
quality of the actual summary output.

# vs-soft-allow  — end-to-end pipeline (variants → strip → score → rank → MD).
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import strip_think

LFM_VARIANTS: tuple[str, ...] = (
    "hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M",
    "hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:q4_k_m",
    "hf.co/batiai/LFM2.5-8B-A1B-GGUF:Q4_K_M",
    "hf.co/nathanrchn/LFM2.5-8B-A1B-GGUF-fixed:Q4_K_M",
    "hf.co/sliderforthewin/lfm2.5-8b-a1b-ft-GGUF:Q3_K_M",
    "hf.co/mradermacher/Huihui-LFM2.5-8B-A1B-abliterated-i1-GGUF:Q4_K_M",
    "hf.co/gaston-parravicini/LFM2.5-8B-A1B-Uncensored-Gaston-GGUF:Q4_K_M",
    "hf.co/DuoNeural/LFM2.5-8B-A1B-Abliterated-GGUF:Q4_K_M",
    "hf.co/brownsauto/LFM2.5-8B-A1B-GGUF:Q4_K_M",
)

PROMPTS: tuple[tuple[str, str], ...] = (
    ("sum_async",
     "Summarize in ONE sentence, max 30 words. NO preamble.\n\n"
     "async function uploadWithRetry(file, retries=3) {\n"
     "  for (let i = 0; i < retries; i++) {\n"
     "    try {\n"
     "      const res = await fetch('/upload', { method: 'POST', body: file });\n"
     "      if (!res.ok) throw new Error(`HTTP ${res.status}`);\n"
     "      return res.json();\n"
     "    } catch (e) {\n"
     "      if (i === retries - 1) throw e;\n"
     "      await sleep(2 ** i * 100);\n"
     "    }\n"
     "  }\n"
     "}"),
    ("sum_state",
     "Summarize in ONE sentence, max 30 words. NO preamble.\n\n"
     "function getVisibleItems(items, filter) {\n"
     "  const result = [];\n"
     "  for (const item of items) {\n"
     "    if (filter.search) {\n"
     "      if (!item.name.toLowerCase().includes(filter.search.toLowerCase())) continue;\n"
     "    }\n"
     "    if (filter.minPrice !== undefined && item.price < filter.minPrice) continue;\n"
     "    if (filter.maxPrice !== undefined && item.price > filter.maxPrice) continue;\n"
     "    if (filter.tags?.length && !filter.tags.some(t => item.tags.includes(t))) continue;\n"
     "    result.push(item);\n"
     "  }\n"
     "  return result;\n"
     "}"),
    ("sum_lifecycle",
     "Summarize in ONE sentence, max 30 words. NO preamble.\n\n"
     "class Session {\n"
     "  constructor(token, ttl=3600) {\n"
     "    this.token = token;\n"
     "    this.expiresAt = Date.now() + ttl * 1000;\n"
     "    this.observers = new Set();\n"
     "  }\n"
     "  isValid() { return Date.now() < this.expiresAt; }\n"
     "  refresh(newTtl) {\n"
     "    this.expiresAt = Date.now() + newTtl * 1000;\n"
     "    for (const cb of this.observers) cb(this);\n"
     "  }\n"
     "  onExpire(cb) { this.observers.add(cb); return () => this.observers.delete(cb); }\n"
     "}"),
)

SUMMARY_KEYWORDS: tuple[str, ...] = (
    "function", "method", "class", "asynchronously", "expir",
    "filter", "retri", "session", "upload",
)


def _score(res: dict, budget: int = 30) -> float:
    """Score an LFM response AFTER stripping <think>...</think>."""
    if "err" in res:
        return -100.0
    clean = strip_think(res["out"])
    L = clean.lower()
    s = 0.0
    if not clean:
        s -= 8
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if res.get("done") == "length" and res.get("etoks", 0) >= 119:
        s -= 4
    wc = len(clean.split())
    if 5 <= wc <= budget:
        s += 4
    elif wc <= budget * 1.5:
        s += 2
    elif wc > budget * 2:
        s -= 2
    if any(kw in L for kw in SUMMARY_KEYWORDS):
        s += 3
    s += min(res.get("tps", 0) / 15.0, 3.0)
    return round(s, 2)


def run_model(model: str, opts: CallOpts) -> dict:
    out: dict = {}
    for pid, prompt in PROMPTS:
        res = call(model, prompt, opts=opts)
        out[pid] = {"score": _score(res), "res": res}
    return {model: out}


def _rank(results: dict) -> list[tuple[str, float, float, list[float]]]:
    """Aggregate per-variant scores into a sorted leaderboard."""
    ranked = []
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r:
            continue
        scores = [v["score"] for v in r.values()]
        avg = round(sum(scores) / len(scores), 2) if scores else -100.0
        avg_tps = round(sum(v["res"].get("tps", 0) for v in r.values()) / len(r), 1)
        ranked.append((m, avg, avg_tps, scores))
    ranked.sort(key=lambda x: -x[1])
    return ranked


def cmd_lfm_variant(args: argparse.Namespace) -> int:
    """`ollama-bench lfm-variant` entry point."""
    candidates = list(args.variants) if args.variants else list(LFM_VARIANTS)
    print(f"# LFM tie-break: {len(candidates)} variants × {len(PROMPTS)} prompts", file=sys.stderr)
    opts = CallOpts(num_predict=120, num_ctx=4096)

    results: dict = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m, opts): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i}/{len(candidates)}] {m[:55]}  done", file=sys.stderr, flush=True)

    ranked = _rank(results)
    out_path = Path(args.output) if args.output else result_path("lfm_ranking", ext="md")
    with out_path.open("w") as f:
        f.write("# LFM2.5-8B-A1B Variant Tie-Break\n\n")
        f.write("Task: codeq summary (3 prompts). All variants leak thinking; `<think>` stripped before scoring.\n\n")
        f.write("| # | Score | Avg TPS | sum_async | sum_state | sum_lifecycle | Model |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for i, (m, avg, tps, scores) in enumerate(ranked, 1):
            s_str = " | ".join(f"{s:.2f}" for s in scores)
            f.write(f"| {i} | {avg:.2f} | {tps} | {s_str} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    """Attach lfm-variant subcommand to root CLI."""
    p = sub.add_parser(
        "lfm-variant", parents=[parent],
        help="codeq summary tie-break for LFM family (think-strip).",
    )
    p.add_argument("-v", "--variants", nargs="*", help="LFM variants to test (default: built-in 9).")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_lfm_variant)
