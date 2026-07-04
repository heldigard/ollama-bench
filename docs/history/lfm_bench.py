#!/usr/bin/env python3
"""LFM-variant tie-break: 9 LFM2.5-8B-A1B variants × codeq summary task.

All LFM variants leak thinking; we strip it before scoring.
Goal: find which LFM variant is the BEST codeq-summary candidate.
"""
from __future__ import annotations
import json, time, re, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

OLLAMA = "http://localhost:11434"
TIMEOUT = 180

# All LFM variants discovered
LFM_VARIANTS = [
    "hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M",
    "hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:q4_k_m",
    "hf.co/batiai/LFM2.5-8B-A1B-GGUF:Q4_K_M",
    "hf.co/nathanrchn/LFM2.5-8B-A1B-GGUF-fixed:Q4_K_M",
    "hf.co/sliderforthewin/lfm2.5-8b-a1b-ft-GGUF:Q3_K_M",
    "hf.co/mradermacher/Huihui-LFM2.5-8B-A1B-abliterated-i1-GGUF:Q4_K_M",
    "hf.co/gaston-parravicini/LFM2.5-8B-A1B-Uncensored-Gaston-GGUF:Q4_K_M",
    "hf.co/DuoNeural/LFM2.5-8B-A1B-Abliterated-GGUF:Q4_K_M",
    "hf.co/brownsauto/LFM2.5-8B-A1B-GGUF:Q4_K_M",
]

# 3 hard codeq prompts to discriminate
PROMPTS = [
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
]

THINK_RE = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)

def strip_think(s: str) -> str:
    """Strip <think>...</think> blocks (matched or orphan)."""
    return THINK_RE.sub("", s).strip()

def call(model: str, prompt: str) -> dict:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_predict": 120, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
    except Exception as e:
        return {"err": str(e)[:200]}
    dt = time.perf_counter() - t0
    out = data.get("response", "") or ""
    return {
        "dt": round(dt, 2),
        "tps": round(data.get("eval_count", 0) / dt, 1) if dt > 0 else 0.0,
        "etoks": data.get("eval_count", 0),
        "len_raw": len(out),
        "len_clean": len(strip_think(out)),
        "done": data.get("done_reason"),
        "out": out,
        "clean": strip_think(out),
    }

def score(res: dict, budget: int = 30) -> float:
    if "err" in res: return -100.0
    clean = res["clean"]
    L = clean.lower()
    s = 0.0
    # Hard leaks (post-strip) — model still leaks if clean is empty or huge
    if not clean:
        s -= 8  # couldn't extract anything
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if res.get("done") == "length" and res["etoks"] >= 119:
        s -= 4
    # Within budget = good
    wc = len(clean.split())
    if 5 <= wc <= budget:
        s += 4
    elif wc <= budget * 1.5:
        s += 2
    elif wc > budget * 2:
        s -= 2
    # Contains a "function does X" / "class manages Y" pattern (heuristic)
    if any(kw in L for kw in ["function", "method", "class", "asynchronously", "expir", "filter", "retri", "session", "upload"]):
        s += 3
    # tps bonus
    s += min(res["tps"] / 15.0, 3.0)
    return round(s, 2)

def run_model(model: str) -> dict:
    out = {}
    for pid, prompt in PROMPTS:
        res = call(model, prompt)
        out[pid] = {"score": score(res), "res": res}
    return {model: out}

def main():
    print(f"# LFM tie-break: {len(LFM_VARIANTS)} variants × {len(PROMPTS)} prompts", flush=True)
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m): m for m in LFM_VARIANTS}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i}/{len(LFM_VARIANTS)}] {m[:55]}  done", flush=True)

    # Aggregate
    ranked = []
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r: continue
        scores = [v["score"] for v in r.values()]
        avg = round(sum(scores) / len(scores), 2) if scores else -100
        avg_tps = round(sum(v["res"].get("tps", 0) for v in r.values()) / len(r), 1)
        ranked.append((m, avg, avg_tps, scores))
    ranked.sort(key=lambda x: -x[1])

    OUT = Path("/home/eldi/bench/ollama/LFM_RANKING.md")
    with OUT.open("w") as f:
        f.write("# LFM2.5-8B-A1B Variant Tie-Break — 2026-07-04\n\n")
        f.write("Task: codeq summary (3 prompts). All variants leak thinking; `<think>` stripped before scoring.\n")
        f.write("Range: -5 to +10. Higher = better.\n\n")
        f.write("| # | Score | Avg TPS | sum_async | sum_state | sum_lifecycle | Model |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for i, (m, avg, tps, scores) in enumerate(ranked, 1):
            s_str = " | ".join(f"{s:.2f}" for s in scores)
            f.write(f"| {i} | {avg:.2f} | {tps} | {s_str} | `{m}` |\n")
    print(f"\nWrote {OUT}", flush=True)

if __name__ == "__main__":
    main()