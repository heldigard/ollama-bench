#!/usr/bin/env python3
"""Code-gen N=3: 2 clean qwopus35-v3 coder variants vs setneuf + composer Q8 (real code champ).

Harder fixture (2 tasks) to break the 7/7 saturation. N=3 for variance. Manual correctness
inspection is the real judge (rubric hid setneuf's invalid `Awaitable[P] -> R` signature).
think=False, temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = 3
MODELS = [
    ("v3_4b_coder_mtp", "qwopus35-4b-coder-mtp:latest"),
    ("v3_4b_coder",     "qwopus35-4b-coder:latest"),
    ("setneuf_4b_mtp",  "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU"),
    ("composer_q8",     "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0"),  # code champ
]
OUT = Path("/home/eldi/bench/ollama/results_qwopus_v3")

# Task 1: async retry w/ generics (discriminates type-signature correctness)
T1 = ("Write a Python function `retry_with_backoff(fn, *, retries=3, base_delay=0.5, jitter=True)` "
      "that calls an async `fn()` and retries on Exception with exponential backoff "
      "(base_delay * 2**attempt) plus optional random jitter. Return the result on success; raise the "
      "last exception after exhausting retries. Full type hints. No preamble, just the code.")
# Task 2: a small generic container w/ edge cases (discriminates correctness over flashiness)
T2 = ("Write a Python class `LRUCache[K, V]` (generic) with `get(key) -> V | None`, "
      "`put(key, value) -> None`, capacity limit, and O(1) operations using OrderedDict. "
      "Handle: empty cache, capacity=0 (raise ValueError), updating existing key (moves to end). "
      "Full type hints, Generic[K,V]. No preamble, just the code.")
TASKS = [("retry", T1), ("lru", T2)]


def gen(model, prompt):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 700}, "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=240) as r:
        d = json.load(r)
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec/(ed/1e9),1) if ed else 0), d.get("done_reason")


def main():
    agg = {}
    for label, model in MODELS:
        agg[label] = {"model": model, "tasks": {}}
        for tname, prompt in TASKS:
            runs = []
            for i in range(N):
                out, tps, done = gen(model, prompt)
                (OUT / f"{label}_code_{tname}_{i+1}.txt").write_text(out)
                low = out.lower()
                # correctness red-flags (manual-inspect the rest)
                flags = {
                    "invalid_awaitable_arrow": "awaitable[" in low and "-> r" in out.replace(" ", ""),
                    "raises_valueerror_0": "valueerror" in low and ("capacity" in low or "0" in low),
                    "ordereddict": "ordereddict" in low or "ordered_dict" in low or "OrderedDict" in out,
                    "generic_kv": ("generic" in low or "[k, v]" in out.replace(" ","").lower() or "typevar" in low),
                    "moves_to_end": "move_to_end" in low or "movetoend" in low,
                    "done_length": done == "length",
                }
                runs.append({"done": done, "tps": tps, "flags": flags, "len": len(out)})
                print(f"  [{label}] {tname} {i+1}/{N}: done={done} tps={tps} "
                      f"orddict={flags['ordereddict']} valerr={flags['raises_valueerror_0']}", flush=True)
            agg[label]["tasks"][tname] = runs
    print("\n" + "=" * 70)
    print("Code-gen N=3 — INSPECT RAW FILES for correctness (rubric is indicative only):")
    print("=" * 70)
    for label, _ in MODELS:
        for tname, _ in TASKS:
            lens = [r["len"] for r in agg[label]["tasks"][tname]]
            doneanylen = any(r["done"] == "length" for r in agg[label]["tasks"][tname])
            print(f"  {label:<18} {tname}: lens={lens} any_length={doneanylen}")
    print(f"\nRaw outputs -> {OUT}/{label}_code_{tname}_*.txt  (read these for correctness verdict)")


if __name__ == "__main__":
    main()
