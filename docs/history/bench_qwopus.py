#!/usr/bin/env python3
"""Qwopus3.5 family bench on its REAL role: LONGCTX (transcript→handoff recall) + REASON (objective math).

Qwopus3.5:4b is the longctx+reason champion (NOT code). SetneufPT variants are "-Coder" tuned
(hypothesis: worse at reason/longctx; fredrezones55:9b is the likely quality upgrade). N iterations,
think=False (ecosystem match), temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request, sys, subprocess
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
MODELS = [
    ("fred_4b_current", "fredrezones55/Qwopus3.5:4b"),
    ("fred_9b",         "fredrezones55/Qwopus3.5:9b"),
    ("setneuf_9B_Q8",   "SetneufPT/Qwopus3.5-9B-Coder_Q8_64k_16GB-GPU"),
    ("setneuf_9B_Q4MTP","SetneufPT/Qwopus3.5-9B-Coder-MTP_Q4_64k_16GB-GPU"),
    ("setneuf_4B_Q4MTP","SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU"),
]
OUT = Path("/home/eldi/bench/ollama/results_qwopus")
OUT.mkdir(exist_ok=True)

# ---- REASON test (objective) ----
REASON_PROMPT = (
    "A sprint has capacity of 40 story points per sprint. The backlog has 200 points of work remaining. "
    "There are 3 sprints left before a hard deadline. The team's velocity over the last 3 sprints was "
    "35, 42, and 38 points (average 38.3). Question: Can they finish the entire backlog in the 3 remaining "
    "sprints at current velocity? If not, what is the MINIMUM velocity per sprint they would need to finish "
    "exactly 200 points in 3 sprints, and how much extra per sprint is that over their current average? "
    "Show the arithmetic, then give a one-line final answer.")
# Objective: 3×38.3=115 < 200 → NO. Need 200/3 = 66.67 pts/sprint. Extra = 66.67-38.33 = 28.33.
REASON_KEY = ["66", "67", "66.6", "66.7", "28", "29", "28.3"]  # any → got the magnitude
REASON_NO = ["no", "cannot", "can't", "not finish", "cannot finish", "short", "won't"]

# ---- LONGCTX test: transcript with 10 planted facts → handoff ----
FACTS = [  # (id, must-appear tokens)
    ("pool 5->10",        ["5 to 10", "5→10", "from 5", "pool size"]),
    ("async db pool",     ["async", "connection pool", "db pool"]),
    ("test_payment_flow", ["test_payment_flow", "payment_flow"]),
    ("timeout",           ["timeout", "time out"]),
    ("8/10 passed",       ["8/10", "8 of 10", "eight"]),
    ("branch fix/payment-flake", ["fix/payment", "payment-flake", "payment_flake"]),
    ("loguru",            ["loguru"]),
    ("conftest root",     ["conftest"]),
    ("pyproject [tool.ruff]", ["tool.ruff", "ruff"]),
    ("hatchling",         ["hatchling"]),
]
TRANSCRIPT = (
    "Produce a structured handoff note (Decisions / Root cause / Next steps / Blockers) that preserves "
    "ALL key facts. Completeness over brevity.\n\n"
    "Session: investigating a flaky test in /home/eldi/proj/tests/test_payment_flow.py. The test "
    "test_payment_flow sometimes fails with a timeout error. Suspected root cause: race condition in the "
    "async DB connection pool. Yesterday the user changed the pool size from 5 to 10 connections. After "
    "the change the test passed 8/10 runs today, but is still flaky. Next step: add tracing to identify "
    "which pool acquire is slow. Decided to switch to loguru for structured logging instead of stdlib "
    "logging. Will commit the test fixes in branch fix/payment-flake. Need to add conftest.py at the repo "
    "root so pytest discovers fixtures. Also need to add a [tool.ruff] section to pyproject.toml. The "
    "project uses hatchling as the build backend (chosen over setuptools for speed). No blockers currently.")

LEAKS = ["<think", "</think", "<|think|", "<|tool_call", "<|channel", "0000"]


def gen(model, prompt, num_predict=600):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_ctx": 16384, "num_predict": num_predict}, "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    wall = time.time() - t0
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, round(ec / (ed / 1e9), 1) if ed else 0, round(wall, 1), d.get("done_reason")


def vram_mib():
    try:
        return int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used",
                   "--format=csv,noheader,nounits"], stderr=subprocess.DEVNULL, text=True).strip())
    except Exception:
        return -1


def run_model(label, model):
    res = {"reason": [], "longctx": []}
    for i in range(N):
        # REASON
        out, tps, wall, done = gen(model, REASON_PROMPT)
        low = out.lower()
        reason_ok = any(k in out for k in REASON_KEY) and any(n in low for n in REASON_NO)
        (OUT / f"{label}_reason_{i+1}.txt").write_text(out)
        res["reason"].append({"ok": reason_ok, "tps": tps, "wall": wall, "done": done, "len": len(out)})
        print(f"  [{label}] reason {i+1}/{N}: {'OK' if reason_ok else 'MISS'} tps={tps} wall={wall}s done={done}", flush=True)
        # LONGCTX
        out, tps, wall, done = gen(model, TRANSCRIPT, num_predict=800)
        low = out.lower()
        hits = sum(1 for _, toks in FACTS if any(t.lower() in low for t in toks))
        leaks = [p for p in LEAKS if p in low]
        (OUT / f"{label}_longctx_{i+1}.txt").write_text(out)
        res["longctx"].append({"recall": f"{hits}/{len(FACTS)}", "hits": hits, "leaks": leaks,
                                "tps": tps, "wall": wall, "done": done})
        print(f"  [{label}] longctx {i+1}/{N}: recall={hits}/{len(FACTS)} leaks={leaks or '-'} tps={tps} wall={wall}s", flush=True)
    res["reason_acc"] = round(sum(r["ok"] for r in res["reason"]) / N, 2)
    res["longctx_mean"] = round(sum(l["hits"] for l in res["longctx"]) / N, 2)
    res["mean_tps"] = round(sum(r["tps"] for r in res["reason"] + res["longctx"]) / (2 * N), 1)
    res["any_leak"] = any(l["leaks"] for l in res["longctx"])
    res["any_length"] = any(r["done"] == "length" for r in res["reason"] + res["longctx"])
    res["vram_after_load"] = vram_mib()
    return res


def main():
    agg = {}
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        agg[label] = {"model": model, **run_model(label, model)}
    print("\n" + "=" * 78)
    print(f"{'MODEL':<20}{'reason_acc':>12}{'longctx/10':>12}{'tok/s':>8}{'leak':>6}{'len':>6}{'VRAM_MiB':>10}")
    print("-" * 78)
    for label, _ in MODELS:
        r = agg[label]
        print(f"{label:<20}{r['reason_acc']:>12}{r['longctx_mean']:>12}{r['mean_tps']:>8}"
              f"{str(r['any_leak']):>6}{str(r['any_length']):>6}{r['vram_after_load']:>10}")
    (OUT / "summary.json").write_text(json.dumps(agg, indent=2, default=str))
    print(f"\nOutputs → {OUT}/  (reason + longctx per run)")


if __name__ == "__main__":
    main()
