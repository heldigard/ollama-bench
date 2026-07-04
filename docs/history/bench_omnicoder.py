#!/usr/bin/env python3
"""OmniCoder family bench. Role: compact (handoff) + code. GATE = cleanliness (no reasoning leak).

carstenuhlig/omnicoder-9b was DEMOTED (leaks reasoning under think=False, empties under think=True).
Test whether the user's new candidates (Q8_0, studiobrn/modOmniCoder, zfujicute-Opus-v2) are CLEAN
and beat Q4_K_M. A model that leaks is DISQUALIFIED regardless of quality (hook pollution).
N iterations, think=False, temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request, sys, subprocess, re
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
MODELS = [
    ("carstenuhlig_Q4_KM", "carstenuhlig/omnicoder-9b:Q4_K_M"),
    ("carstenuhlig_Q8_0",  "carstenuhlig/omnicoder-9b:Q8_0"),
    ("studiobrn_modOmni",  "studiobrn/modOmniCoder:latest"),
    ("zfujicute_Opus_v2",  "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest"),
]
OUT = Path("/home/eldi/bench/ollama/results_omnicoder")
OUT.mkdir(exist_ok=True)

FACTS = [("pool 5->10",["5 to 10","5→10","from 5","pool size"]),("async db pool",["async","connection pool","db pool"]),
    ("test_payment_flow",["test_payment_flow","payment_flow"]),("timeout",["timeout","time out"]),
    ("8/10 passed",["8/10","8 of 10","eight","80%"]),("branch fix/payment-flake",["fix/payment","payment-flake","payment_flake"]),
    ("loguru",["loguru"]),("conftest root",["conftest"]),("pyproject [tool.ruff]",["tool.ruff","ruff"]),("hatchling",["hatchling"])]
COMPACT_PROMPT = ("Produce a structured handoff note (Decisions / Root cause / Next steps / Blockers) preserving "
    "ALL key facts. Completeness over brevity. Plain text only, no preamble.\n\n"
    "Session: investigating a flaky test in /home/eldi/proj/tests/test_payment_flow.py. The test "
    "test_payment_flow sometimes fails with a timeout error. Suspected root cause: race condition in the "
    "async DB connection pool. Yesterday the user changed the pool size from 5 to 10. After the change "
    "the test passed 8/10 runs today, still flaky. Next: add tracing to identify which pool acquire is "
    "slow. Decided to switch to loguru for structured logging. Will commit fixes in branch "
    "fix/payment-flake. Need conftest.py at repo root. Also add [tool.ruff] to pyproject.toml. Build "
    "backend is hatchling. No blockers.")
CODE_PROMPT = ("Write a Python async function retry_with_backoff(fn, max_attempts=3, base_delay=0.5) that "
    "retries fn on ConnectionError or TimeoutError with exponential backoff and jitter. Return the result "
    "on success, raise the last exception after max_attempts. Include type hints and a docstring. "
    "Output ONLY the code, no explanation.")
CODE_KEY = ["async def", "retry_with_backoff", "max_attempts", "base_delay", "backoff", "exponential",
            "jitter", "random", "ConnectionError", "TimeoutError", "->", "raise"]
LEAKS = ["<think", "</think", "<|think|", "<|tool_call", "<|channel", "0000", "let me think",
         "i'll analyze", "first, let", "i need to", "the user wants", "let me parse", "step 1"]


def gen(model, prompt, num_predict=700):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_ctx": 12288, "num_predict": num_predict}, "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}]", 0, 0, "http_error"
    wall = time.time() - t0
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec / (ed / 1e9), 1) if ed else 0), round(wall, 1), d.get("done_reason")


def run_model(label, model):
    res = {"compact": [], "code": []}
    for i in range(N):
        out, tps, wall, done = gen(model, COMPACT_PROMPT)
        low = out.lower()
        hits = sum(1 for _, toks in FACTS if any(t.lower() in low for t in toks))
        leaks = [p for p in LEAKS if p in low]
        (OUT / f"{label}_compact_{i+1}.txt").write_text(out)
        res["compact"].append({"recall": hits, "leaks": leaks, "tps": tps, "wall": wall, "done": done})
        print(f"  [{label}] compact {i+1}/{N}: {hits}/10 leaks={leaks or '-'} tps={tps} done={done}", flush=True)
        out, tps, wall, done = gen(model, CODE_PROMPT)
        low = out.lower()
        ckeys = sum(1 for k in CODE_KEY if k.lower() in low)
        leaks = [p for p in LEAKS if p in low]
        (OUT / f"{label}_code_{i+1}.txt").write_text(out)
        res["code"].append({"keys": ckeys, "leaks": leaks, "tps": tps, "wall": wall, "done": done})
        print(f"  [{label}] code    {i+1}/{N}: {ckeys}/{len(CODE_KEY)} keys leaks={leaks or '-'} tps={tps} done={done}", flush=True)
    res["compact_recall"] = round(sum(c["recall"] for c in res["compact"]) / N, 2)
    res["code_keys"] = round(sum(c["keys"] for c in res["code"]) / N, 2)
    res["any_leak"] = any(c["leaks"] for c in res["compact"] + res["code"])
    res["mean_tps"] = round(sum(c["tps"] for c in res["compact"] + res["code"]) / (2 * N), 1)
    res["any_length"] = any(c["done"] == "length" for c in res["compact"] + res["code"])
    return res


def main():
    agg = {}
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        agg[label] = {"model": model, **run_model(label, model)}
    print("\n" + "=" * 82)
    print(f"{'MODEL':<22}{'compact/10':>12}{'code_keys/12':>13}{'tok/s':>8}{'LEAK':>7}{'len':>6}{'QUALIFIED':>11}")
    print("-" * 82)
    for label, _ in MODELS:
        r = agg[label]
        qual = "YES" if not r["any_leak"] else "NO-LEAK"
        print(f"{label:<22}{r['compact_recall']:>12}{r['code_keys']:>13}{r['mean_tps']:>8}"
              f"{str(r['any_leak']):>7}{str(r['any_length']):>6}{qual:>11}")
    (OUT / "summary.json").write_text(json.dumps(agg, indent=2, default=str))
    print(f"\nOutputs → {OUT}/")


if __name__ == "__main__":
    main()
