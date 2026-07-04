#!/usr/bin/env python3
"""Smoke bench: 18 Qwen3.5-4b candidates vs qwen3.5:4b baseline (universal slot).

1-shot each on compact (10-fact handoff recall) + reason (objective math), gated by
reasoning-leak. Filters leakers/weak models fast; deep-bench only clean survivors.
Tolerant: skips models that fail to load (not-yet-pulled).
"""
from __future__ import annotations
import json, time, urllib.request, sys
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
BASELINE = ("qwen3.5:4b_BASELINE", "qwen3.5:4b")
CANDIDATES = [
    ("q8_0",        "qwen3.5:4b-q8_0"),
    ("bf16",        "qwen3.5:4b-bf16"),
    ("abliterated", "kaineone/qwen3.5-4b-abliterated"),
    ("Dhnanjay_lite","Dhnanjay/qwen3.5-lite"),
    ("schien_lite", "schien/qwen3.5-lite"),
    ("kwang_v2",    "kwangsuklee/Qwen3.5-4B.Q4_K_M-Claude-4.6-Opus-Reasoning-Distilled-v2"),
    ("kwang_gguf",  "kwangsuklee/Qwen3.5-4B-Claude-4.6-Opus-Reasoning-Distilled-GGUF"),
    ("charaf_opus", "charaf/qwen3.5-4b-claude-opus"),
    ("Eve_8B_merged","jeffgreen311/Eve-V2-Unleashed-Qwen3.5-8B-Liberated-4K-4B-Merged"),
    ("search_V2",   "jbaptistedaniel/search-ai-qwen3.5-4B-V2-q4"),
    ("search_V8",   "jbaptistedaniel/search-ai-qwen3.5-4B-q4-V8"),
    ("thinhphan",   "thinhphan97/qwen3.5-4B"),
    ("crow_opus46", "free01/qwen3.5-4b-crow-opus4.6:q8"),
    ("jaahas_crow_4b", "jaahas/crow:4b"),
    ("jaahas_crow_9b", "jaahas/crow:9b"),
    ("eve_solforg3","jeffgreen311/eve-qwen35-4b-solforg3-v2"),
    ("caal",        "coreworxlab/caal-qwen3.5-4b"),
    ("pii_v4",      "wwydmanski/qwen3.5-4b-pii-v4"),
    ("DanyAI",      "DanyaVoredom/DanyAI-qwen3.5-4b"),
    ("phibek",      "hectocorn-labs/phibek-4b"),
]
ALL = [BASELINE] + CANDIDATES
OUT = Path("/home/eldi/bench/ollama/results_qwen35_smoke")
OUT.mkdir(exist_ok=True)

FACTS = [("pool 5->10",["5 to 10","5→10","from 5","pool size"]),("async db pool",["async","connection pool","db pool"]),
    ("test_payment_flow",["test_payment_flow","payment_flow"]),("timeout",["timeout","time out"]),
    ("8/10 passed",["8/10","8 of 10","eight","80%"]),("branch fix/payment",["fix/payment","payment-flake","payment_flake"]),
    ("loguru",["loguru"]),("conftest",["conftest"]),("tool.ruff",["tool.ruff","[tool.ruff]","ruff"]),("hatchling",["hatchling"])]
COMPACT = ("Produce a structured handoff note (Decisions/Root cause/Next steps/Blockers) preserving ALL key "
    "facts. Plain text, no preamble.\n\nSession: flaky test /home/eldi/proj/tests/test_payment_flow.py fails "
    "with timeout. Suspected: race in async DB connection pool. Yesterday pool size changed 5 to 10. Now passes "
    "8/10, still flaky. Next: add tracing for slow pool acquire. Decided: switch to loguru. Commit in branch "
    "fix/payment-flake. Need conftest.py at root. Add [tool.ruff] to pyproject.toml. Build backend hatchling. No blockers.")
REASON = ("Sprint capacity 40pts. Backlog 200pts. 3 sprints left. Velocity last 3: 35,42,38 (avg 38.3). "
    "Can they finish in 3 sprints at current velocity? If not, minimum velocity/sprint to finish 200 in 3, "
    "and extra per sprint over avg? Show arithmetic then one-line final answer.")
RKEY = ["66","67","66.6","66.7","28","29","28.3"]; RNO = ["no","cannot","can't","not finish","short","won't"]
LEAKS = ["<think","</think","<|think|","<|tool_call","<|channel","0000","let me think","i'll analyze",
         "first, let","i need to","the user wants","let me parse","step 1","thinking process","okay, let","alright, let"]


def gen(model, prompt, num_predict=500):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_ctx": 12288, "num_predict": num_predict}, "cache": False}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=200) as r:
            d = json.load(r)
    except Exception as e:
        return None, 0, 0, f"ERR:{type(e).__name__}"
    wall = time.time() - t0
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec / (ed / 1e9), 1) if ed else 0), round(wall, 1), d.get("done_reason")


def main():
    only = set(sys.argv[1:]) if len(sys.argv) > 1 and not sys.argv[1].isdigit() else None
    rows = []
    print(f"{'MODEL':<22}{'compact':>9}{'reason':>8}{'leak':>7}{'tok/s':>7}{'done':>11}")
    print("-" * 70)
    for label, model in ALL:
        if only and label not in only:
            continue
        out, tps, wall, done = gen(model, COMPACT)
        if out is None:
            print(f"{label:<22}{'LOAD_FAIL':>9}{'':>8}{'':>7}{'':>7}{done:>11}")
            rows.append({"label": label, "model": model, "fail": done}); continue
        low = out.lower()
        chits = sum(1 for _, t in FACTS if any(x.lower() in low for x in t))
        cleaks = [p for p in LEAKS if p in low]
        (OUT / f"{label}_compact.txt").write_text(out)
        out2, tps2, wall2, done2 = gen(model, REASON)
        if out2 is None:
            rhits = "ERR"; rleaks = []
        else:
            rlow = out2.lower()
            rok = any(k in out2 for k in RKEY) and any(n in rlow for n in RNO)
            rhits = "OK" if rok else "MISS"
            rleaks = [p for p in LEAKS if p in rlow]
            (OUT / f"{label}_reason.txt").write_text(out2)
        leak = bool(cleaks or rleaks)
        mtps = round((tps + tps2) / 2, 1) if out2 else tps
        rows.append({"label": label, "model": model, "compact": chits, "reason": rhits,
                     "leak": leak, "tps": mtps, "done_compact": done})
        print(f"{label:<22}{chits:>9}{rhits:>8}{('LEAK' if leak else '-'):>7}{mtps:>7}{done:>11}")
    (OUT / "summary.json").write_text(json.dumps(rows, indent=2, default=str))
    clean = [r for r in rows if not r.get("fail") and not r.get("leak")]
    print(f"\nClean survivors (no leak, loaded): {[r['label'] for r in clean]}")
    print(f"Leakers/dominated: {[r['label'] for r in rows if r.get('leak') or r.get('fail')]}")


if __name__ == "__main__":
    main()
