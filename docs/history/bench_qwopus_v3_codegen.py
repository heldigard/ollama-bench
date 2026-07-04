#!/usr/bin/env python3
"""Quick code-gen probe: 2 clean qwopus35-v3 coder variants vs baselines.

1-shot retry-with-backoff task (the 2026-06-30 code-gen fixture). Judges: type hints,
TypeVar, jitter, backoff correctness, clean (no leak). think=False, temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
MODELS = [
    ("v3_4b_coder_mtp", "qwopus35-4b-coder-mtp:latest"),
    ("v3_4b_coder",     "qwopus35-4b-coder:latest"),
    ("setneuf_4b_mtp",  "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU"),
    ("qwen35_4b",       "qwen3.5:4b"),
]
OUT = Path("/home/eldi/bench/ollama/results_qwopus_v3")

PROMPT = ("Write a Python function `retry_with_backoff(fn, *, retries=3, base_delay=0.5, "
          "jitter=True)` that calls an async `fn()` and retries on `Exception` with exponential "
          "backoff (base_delay * 2**attempt) plus optional random jitter. Return the result on "
          "success; raise the last exception after exhausting retries. Full type hints "
          "(Use typing.TypeVar/ParamSpec/Awaitable where appropriate). No preamble, just the code.")
LEAKS = ["<think","</think","<|think|","let me think","i'll","first, let","i need to",
         "the user wants","step 1","thinking","here is","here's","```python"]


def gen(model):
    payload = json.dumps({"model": model, "prompt": PROMPT, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 600}, "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=200) as r:
        d = json.load(r)
    wall = time.time() - t0
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec/(ed/1e9),1) if ed else 0), round(wall,1), d.get("done_reason")


def main():
    agg = {}
    for label, model in MODELS:
        out, tps, wall, done = gen(model)
        (OUT / f"{label}_codegen.txt").write_text(out)
        low = out.lower()
        leaks = [p for p in LEAKS if p in low]
        # code-gen quality signals
        sig = {
            "typevar": "typevar" in low or "paramspec" in low,
            "awaitable": "awaitable" in low,
            "hints_return": "->" in out,
            "jitter": "jitter" in low or "random.uniform" in low or "random.random" in low,
            "exponential": "2 **" in out or "2**" in out or "base_delay *" in low,
            "async_def": "async def" in low,
            "raises_last": "raise" in low,
            "done": done,
            "leaks": leaks,
            "tps": tps, "wall": wall, "len": len(out),
        }
        score = sum(1 for k in ["typevar","awaitable","hints_return","jitter",
                                 "exponential","async_def","raises_last"] if sig[k])
        agg[label] = {"model": model, "signals": sig, "score": f"{score}/7"}
        print(f"[{label}] code-gen: {score}/7 tps={tps} done={done} leaks={leaks or '-'}", flush=True)
        print(f"   typevar={sig['typevar']} awaitable={sig['awaitable']} jitter={sig['jitter']} "
              f"exp={sig['exponential']} raise={sig['raises_last']}", flush=True)
    print("\n" + "=" * 60)
    print(f"{'MODEL':<20}{'score':>8}{'tok/s':>8}{'done':>10}{'leak':>6}")
    for label, _ in MODELS:
        s = agg[label]["signals"]
        print(f"{label:<20}{agg[label]['score']:>8}{s['tps']:>8}{str(s['done']):>10}{str(bool(s['leaks'])):>6}")


if __name__ == "__main__":
    main()
