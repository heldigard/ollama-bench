#!/usr/bin/env python3
"""IMPROVE bench: baytout3/HauhauCS-9b (new) vs fredrezones55/HauhauCS-4b (current improve alt)
vs Mobius (improve primary). Role: rewrite vague prompts -> structured agent spec
(GOAL/FILES/STEPS/EDGE CASES/ACCEPTANCE). N=3, think=False, temp=0.2. Gate = no leak + reaches ACCEPTANCE.
"""
from __future__ import annotations
import json, time, urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = 3
MODELS = [
    ("hauhau_9b_baytout3", "baytout3/Qwen3.5-Uncensored-HauhauCS-Aggressive:9b"),  # NEW
    ("hauhau_4b_fred",    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b"),  # current alt
    ("mobius",            "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf"),  # primary
]
OUT = Path("/home/eldi/bench/ollama/results_new4")
OUT.mkdir(exist_ok=True)

VAGUE = ["fix the auth bug", "make the dashboard load faster", "add export to csv on the reports page"]
SYSTEM = ("You rewrite vague coding requests into structured agent specs. Output sections: "
          "GOAL, FILES, STEPS, EDGE CASES, ACCEPTANCE. Be specific, actionable, technical. "
          "No preamble, plain text.")
STRUCT_KEYS = ["GOAL", "FILES", "STEPS", "EDGE", "ACCEPTANCE", "VERIFY", "TEST"]
LEAKS = ["<think", "</think", "let me think", "i'll analyze", "first, let", "the user wants",
         "step 1", "thinking process", "0000"]


def gen(model, prompt):
    payload = json.dumps({"model": model, "prompt": prompt, "system": SYSTEM, "stream": False,
        "think": False, "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 800},
        "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec/(ed/1e9), 1) if ed else 0), d.get("done_reason")


def run_model(label, model):
    runs = []
    for i in range(N):
        for v in VAGUE:
            out, tps, done = gen(model, f"Request: \"{v}\"\n\nStructured spec:")
            low = out.lower()
            struct = sum(1 for k in STRUCT_KEYS if k.lower() in low)
            reaches_acc = "acceptance" in low
            leaks = [p for p in LEAKS if p in low]
            (OUT / f"{label}_imp_{v.split()[0]}_{v.split()[-1]}_{i+1}.txt").write_text(out)
            runs.append({"vague": v, "struct": struct, "acc": reaches_acc, "leaks": leaks,
                         "tps": tps, "done": done, "len": len(out)})
            print(f"  [{label}] '{v[:22]}' {i+1}/{N}: struct={struct}/7 acc={reaches_acc} "
                  f"len={len(out)} done={done} leaks={leaks or '-'}", flush=True)
    return {"mean_struct": round(sum(r["struct"] for r in runs)/len(runs), 2),
            "acc_rate": round(sum(r["acc"] for r in runs)/len(runs), 2),
            "mean_len": round(sum(r["len"] for r in runs)/len(runs), 0),
            "any_leak": any(r["leaks"] for r in runs),
            "any_length": any(r["done"] == "length" for r in runs)}


def main():
    agg = {}
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        agg[label] = {"model": model, **run_model(label, model)}
    print("\n" + "=" * 82)
    print(f"{'MODEL':<22}{'struct/7':>9}{'acc_rate':>9}{'mean_len':>9}{'LEAK':>6}{'len':>6}")
    print("-" * 82)
    for label, _ in MODELS:
        r = agg[label]
        print(f"{label:<22}{r['mean_struct']:>9}{r['acc_rate']:>9}{r['mean_len']:>9}"
              f"{str(r['any_leak']):>6}{str(r['any_length']):>6}")
    print("\nstruct/7 + acc_rate HIGHER=better (acc_rate = reaches ACCEPTANCE section, the def-of-done).")
    sm = OUT / "summary.json"
    if sm.exists():
        data = json.loads(sm.read_text())
        for label, _ in MODELS:
            data[label] = {"improve": agg[label]}
        sm.write_text(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
