#!/usr/bin/env python3
"""web_research SYNTH probe: 2 clean qwopus35-v3 coder variants vs crow:9b (synth champ).

Reuses the exact SYNTH fixture from bench_webresearch.py (Acme-LLM: 128k default, 200k
contradiction, 64k preset caveat). crow:9b is the validated 6/6 synth default. Judge:
does v3 coder detect the contradiction ("stable? NO") + 64k caveat + cite, cleanly?
Uses oc.generate (strip-think + think=False, ecosystem match). temp=0.2.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

sys.path.insert(0, "/home/eldi/bench/ollama")
sys.path.insert(0, "/home/eldi/.claude/scripts")
import bench_webresearch as bw  # noqa: E402  (fixture source)
import ollama_client as oc  # noqa: E402

CANDIDATES = [
    "qwopus35-4b-coder-mtp:latest",
    "qwopus35-4b-coder:latest",
    "jaahas/crow:9b",  # synth champ ref
]
OUT = Path("/home/eldi/bench/ollama/results_qwopus_v3")

# Rubric (controller judgment over raw text):
#   S1 default 128k cited [1][2]        (1pt)
#   S2 contradiction 200k noted         (1pt)
#   S3 "stable?" answered NO             (1pt) — the judgment
#   S4 64k preset caveat mentioned       (1pt)
#   S5 NO pricing/tool-calling leak      (1pt)
#   S6 clean (no think-leak)             (1pt)
#   Total /6
KEYS = {
    "s1_128k": ["128,000", "128k", "128 000"],
    "s2_200k_contra": ["200k", "200,000", "retract", "wrong", "incorrect", "disagree", "contradict"],
    "s3_not_stable": ["not stable", "not fully stable", "no", "isn't stable", "are not stable",
                       "unstable", "partially unstable", "inconsistent", "varies"],
    "s4_64k_caveat": ["64k", "64,000", "low-memory", "low memory", "preset"],
    "s5_no_pricing": None,  # absence check
}
LEAK = ["<think", "</think", "let me think", "i need to", "the user wants", "first, let"]
PRICING = ["pricing", "$2", "per million", "price"]


def score(text: str) -> dict:
    low = text.lower()
    s = {}
    s["s1_128k"] = any(k in low for k in KEYS["s1_128k"])
    s["s2_200k_contra"] = any(k in low for k in KEYS["s2_200k_contra"])
    s["s3_not_stable"] = any(k in low for k in KEYS["s3_not_stable"])
    s["s4_64k_caveat"] = any(k in low for k in KEYS["s4_64k_caveat"])
    s["s5_no_pricing"] = not any(k in low for k in PRICING)
    s["s6_clean"] = not any(k in low for k in LEAK)
    s["score"] = sum(v for k, v in s.items() if isinstance(v, bool))
    s["leaks"] = [k for k in LEAK if k in low]
    return s


def main():
    prompt, system = bw.synth_prompt()
    full = f"{system}\n\n{prompt}"
    agg = {}
    for m in CANDIDATES:
        label = m.split("/")[0].replace(":", "_").replace("-","_")
        t0 = time.time()
        try:
            out = oc.generate(full, model=m, temperature=0.2, num_ctx=16384, cache=False,
                              base_url="http://localhost:11434") or ""
        except Exception as e:  # noqa: BLE001
            out = f"[ERR {e}]"
        dt = time.time() - t0
        sc = score(out)
        (OUT / f"{label}_synth.txt").write_text(out)
        agg[m] = {"dt": round(dt, 1), "chars": len(out), **sc}
        print(f"[{m}] synth: {sc['score']}/6 {dt:.1f}s chars={len(out)} leaks={sc['leaks'] or '-'}", flush=True)
        print(f"   128k={sc['s1_128k']} contra200k={sc['s2_200k_contra']} notStable={sc['s3_not_stable']} "
              f"caveat64k={sc['s4_64k_caveat']} noPricing={sc['s5_no_pricing']} clean={sc['s6_clean']}", flush=True)
    print("\n" + "=" * 64)
    print(f"{'MODEL':<40}{'score':>7}{'clean':>7}")
    for m in CANDIDATES:
        print(f"{m:<40}{agg[m]['score']}/6{str(agg[m]['s6_clean']):>7}")
    # merge
    sm = OUT / "summary.json"
    if sm.exists():
        data = json.loads(sm.read_text())
        data[m.split(":")[0]] = {"synth": agg[m]}
        sm.write_text(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
