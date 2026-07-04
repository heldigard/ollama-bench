#!/usr/bin/env python3
"""HauhauCS family bench. Role: IMPROVE (rewrite vague prompts → structured agent spec).

Current fredrezones55/...HauhauCS-Aggressive:4b is the fast improve-alt (Mobius is primary).
Test if :9b beats it on improve quality (structure + actionability), gate = no leak.
N iterations, think=False, temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request, sys
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
MODELS = [
    ("hauhau_4b_current", "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b"),
    ("hauhau_9b",         "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:9b"),
]
OUT = Path("/home/eldi/bench/ollama/results_hauhau")
OUT.mkdir(exist_ok=True)

VAGUE = [
    "fix the auth bug",
    "make the dashboard load faster",
]
SYSTEM = ("You rewrite vague coding requests into structured agent specs. Output sections: "
          "GOAL, FILES, STEPS, EDGE CASES, ACCEPTANCE. Be specific, actionable, technical. "
          "No preamble, plain text.")
STRUCT_KEYS = ["GOAL", "FILES", "STEPS", "EDGE", "ACCEPTANCE", "VERIFY", "TEST"]
LEAKS = ["<think", "</think", "<|think|", "let me think", "i'll analyze", "first, let",
         "the user wants", "step 1", "thinking process", "0000"]


def gen(model, prompt):
    payload = json.dumps({"model": model, "prompt": prompt, "system": SYSTEM, "stream": False,
        "think": False, "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 700},
        "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    wall = time.time() - t0
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec / (ed / 1e9), 1) if ed else 0), round(wall, 1), d.get("done_reason")


def run_model(label, model):
    res = {"runs": []}
    for i in range(N):
        for v in VAGUE:
            out, tps, wall, done = gen(model, f"Request: \"{v}\"\n\nStructured spec:")
            low = out.lower()
            struct = sum(1 for k in STRUCT_KEYS if k.lower() in low)
            leaks = [p for p in LEAKS if p in low]
            (OUT / f"{label}_{v.split()[0]}_{i+1}.txt").write_text(out)
            res["runs"].append({"vague": v, "struct": struct, "leaks": leaks, "tps": tps,
                                "wall": wall, "done": done, "len": len(out), "out": out})
            print(f"  [{label}] '{v}' {i+1}/{N}: struct={struct}/{len(STRUCT_KEYS)} "
                  f"len={len(out)} leaks={leaks or '-'} tps={tps} done={done}", flush=True)
    res["mean_struct"] = round(sum(r["struct"] for r in res["runs"]) / len(res["runs"]), 2)
    res["mean_len"] = round(sum(r["len"] for r in res["runs"]) / len(res["runs"]), 0)
    res["mean_tps"] = round(sum(r["tps"] for r in res["runs"]) / len(res["runs"]), 1)
    res["any_leak"] = any(r["leaks"] for r in res["runs"])
    res["any_length"] = any(r["done"] == "length" for r in res["runs"])
    return res


def main():
    agg = {}
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        agg[label] = {"model": model, **run_model(label, model)}
    print("\n" + "=" * 78)
    print(f"{'MODEL':<20}{'struct/7':>10}{'mean_len':>10}{'tok/s':>8}{'LEAK':>7}{'len':>6}")
    print("-" * 78)
    for label, _ in MODELS:
        r = agg[label]
        print(f"{label:<20}{r['mean_struct']:>10}{r['mean_len']:>10}{r['mean_tps']:>8}"
              f"{str(r['any_leak']):>7}{str(r['any_length']):>6}")
    (OUT / "summary.json").write_text(json.dumps(agg, indent=2, default=str))
    print(f"\nOutputs → {OUT}/  (inspect raw for actionability/quality)")


if __name__ == "__main__":
    main()
