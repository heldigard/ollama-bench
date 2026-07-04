#!/usr/bin/env python3
"""qwopus35-v3 family smoke + leak gate on its REAL role: LONGCTX (recall) + REASON (objective math).

5 new models (qwopus35-*-v3) vs 3 baselines: SetneufPT 4B-Coder-MTP (current longctx/reason
champ), fredrezones55:9b (reason alt), qwen3.5:4b (universal). 1 rep each, think=False (ecosystem
match), temp=0.2. LEAK GATE is the hard filter — reasoning-tuned Qwopus variants historically
leak preamble/orphan `</think>` under think=False. Drop leakers before deep bench.
"""
from __future__ import annotations
import json, time, urllib.request, subprocess
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
MODELS = [
    ("v3_9b",          "qwopus35-9b-v3:latest"),
    ("v3_4b_mtp",      "qwopus35-4b-v3-mtp:latest"),
    ("v3_4b",          "qwopus35-4b-v3:latest"),
    ("v3_4b_coder_mtp","qwopus35-4b-coder-mtp:latest"),
    ("v3_4b_coder",    "qwopus35-4b-coder:latest"),
    # baselines
    ("setneuf_4b_mtp", "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU"),
    ("fred_9b",        "fredrezones55/Qwopus3.5:9b"),
    ("qwen35_4b",      "qwen3.5:4b"),
]
OUT = Path("/home/eldi/bench/ollama/results_qwopus_v3")
OUT.mkdir(exist_ok=True)

# ---- REASON test (objective) — same as bench_qwopus.py ----
REASON_PROMPT = (
    "A sprint has capacity of 40 story points per sprint. The backlog has 200 points of work remaining. "
    "There are 3 sprints left before a hard deadline. The team's velocity over the last 3 sprints was "
    "35, 42, and 38 points (average 38.3). Question: Can they finish the entire backlog in the 3 remaining "
    "sprints at current velocity? If not, what is the MINIMUM velocity per sprint they would need to finish "
    "exactly 200 points in 3 sprints, and how much extra per sprint is that over their current average? "
    "Show the arithmetic, then give a one-line final answer.")
REASON_KEY = ["66", "67", "66.6", "66.7", "28", "29", "28.3"]
REASON_NO = ["no", "cannot", "can't", "not finish", "cannot finish", "short", "won't"]

# ---- LONGCTX test: transcript with 10 planted facts ----
FACTS = [
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

# Leak gate: tagged think, orphan tags, chat-template tokens, un-tagged reasoning preambles, 0000 repeat
LEAKS = ["<think", "</think", "<|think|", "<|tool_call", "<|channel", "0000",
         "let me think", "i'll analyze", "first, let", "i need to",
         "the user wants", "let me parse", "step 1", "thinking process",
         "thinking:", "reasoning:"]


def gen(model, prompt, num_predict=600, system=None):
    body = {"model": model, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": 0.2, "num_ctx": 16384, "num_predict": num_predict},
            "cache": False}
    if system:
        body["system"] = system
    payload = json.dumps(body).encode()
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
    res = {}
    # REASON
    out, tps, wall, done = gen(model, REASON_PROMPT)
    low = out.lower()
    reason_ok = any(k in out for k in REASON_KEY) and any(n in low for n in REASON_NO)
    rleaks = [p for p in LEAKS if p in low]
    (OUT / f"{label}_reason.txt").write_text(out)
    res["reason"] = {"ok": reason_ok, "tps": tps, "wall": wall, "done": done,
                     "len": len(out), "leaks": rleaks}
    print(f"  [{label}] reason: {'OK' if reason_ok else 'MISS'} tps={tps} wall={wall}s "
          f"done={done} leaks={rleaks or '-'}", flush=True)
    # LONGCTX
    out, tps, wall, done = gen(model, TRANSCRIPT, num_predict=800)
    low = out.lower()
    hits = sum(1 for _, toks in FACTS if any(t.lower() in low for t in toks))
    lleaks = [p for p in LEAKS if p in low]
    (OUT / f"{label}_longctx.txt").write_text(out)
    res["longctx"] = {"recall": f"{hits}/{len(FACTS)}", "hits": hits, "leaks": lleaks,
                      "tps": tps, "wall": wall, "done": done}
    print(f"  [{label}] longctx: recall={hits}/{len(FACTS)} leaks={lleaks or '-'} "
          f"tps={tps} wall={wall}s done={done}", flush=True)
    res["any_leak"] = bool(rleaks or lleaks)
    res["any_length"] = (done == "length") or res["reason"]["done"] == "length"
    res["vram_after_load"] = vram_mib()
    return res


def main():
    agg = {}
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        agg[label] = {"model": model, **run_model(label, model)}
    print("\n" + "=" * 92)
    print(f"{'MODEL':<18}{'reason':>8}{'longctx/10':>12}{'tok/s':>8}{'leak':>6}{'len':>6}{'VRAM_MiB':>10}")
    print("-" * 92)
    for label, _ in MODELS:
        r = agg[label]
        tps = round((r["reason"]["tps"] + r["longctx"]["tps"]) / 2, 1)
        print(f"{label:<18}{str(r['reason']['ok']):>8}{r['longctx']['hits']:>12}{tps:>8}"
              f"{str(r['any_leak']):>6}{str(r['any_length']):>6}{r['vram_after_load']:>10}")
    (OUT / "summary.json").write_text(json.dumps(agg, indent=2, default=str))
    # list survivors (clean = no leak, no length-burn)
    survivors = [l for l, _ in MODELS if not agg[l]["any_leak"]]
    leakers = [l for l, _ in MODELS if agg[l]["any_leak"]]
    print(f"\nLEAKERS (drop): {leakers or 'none'}")
    print(f"CLEAN (deep bench): {survivors}")
    print(f"\nOutputs -> {OUT}/")


if __name__ == "__main__":
    main()
