#!/usr/bin/env python3
"""Multi-iteration quality bench: composer v2 quants on bug-finding (quality-first criterion).

N runs per model → per-bug hit matrix (does each quant reliably find B1..B6?) + mean recall
+ cleanliness + tok/s. Quality discrimination needs hit-rate across runs, NOT a single shot
(single-shot recall is noisy ±2 at temp=0.2 — proven in run1/run2 of bench_composer_quants.py).
"""
from __future__ import annotations
import json, time, urllib.request, urllib.error, sys, subprocess
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
MODELS = [
    ("Q4_K_M", "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest"),
    ("Q6_K",   "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q6_K"),
    ("Q8_0",   "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0"),
]
OUT = Path("/home/eldi/bench/ollama/results_composer_quants/multi")
OUT.mkdir(parents=True, exist_ok=True)

DIFF = r"""diff --git a/src/orders/service.py b/src/orders/service.py
+def find_nth_occurrence(haystack, needle, n):
+    idx = haystack.find(needle)
+    for _ in range(n):
+        idx = haystack.find(needle, idx + 1)
+    return idx
+async def fetch_user_orders(conn, user_id):
+    query = f"SELECT * FROM orders WHERE user_id = '{user_id}' ORDER BY created_at"
+    rows = conn.execute(query).fetchall()
+    return rows
+def parse_config(raw):
+    def coerce(v, typ=int):
+        try:
+            return typ(v)
+        except:
+            return v
+    return {k: coerce(v) for k, v in raw.items()}
+def load_translations(path, cache={}):
+    f = open(path)
+    data = json.load(f)
+    cache[path] = data
+    return data
+async def cancel_order(order_id):
+    order = await get_order(order_id)
+    charge = order["payment"]["charge_id"]
+    stripe.refund(charge)
"""

# Improved rubric (fixed B1/B5 phrasing misses). B6 uses concrete "payment"/"charge_id" = high precision.
BUGS = [
    ("B1 off-by-one/find_nth", ["off-by-one","off by one","returns -1","return -1","returns a -1","no match","not found","invalid index","corrupts subsequent","boundary","first occurrence","n=0","n = 0"]),
    ("B2 SQL injection",       ["injection","parameteri","placeholder","f-string","format string","parameterized"]),
    ("B3 bare except",         ["bare except","bare","except:","swallow","catch-all","catches everything","systemexit","keyboardinterrupt"]),
    ("B4 mutable default",     ["mutable default","default arg","cache={}","mutable","same dict","persists across","shared"]),
    ("B5 resource leak",       ["never closes","not closed","closes","context manager","leak","file handle","unclosed","open(path)","without closing","resource leak"]),
    ("B6 None/KeyError deref", ["keyerror",".get(","key exist","missing key","unchecked","malformed","payment","charge_id","order is none","returns none"]),
]
LEAKS = ["<think","</think","<|think|","<|tool_call","<|channel","0000","let me think","i'll analyze","first, let"]

SYSTEM = ("You review code diffs. Reply with plain text only. Format each finding as "
          "`[SEV] file: detail` where SEV is HIGH/MED/LOW. Max 8 findings, most severe first. "
          "If clean, output exactly: CLEAN. No preamble, no code fences, no JSON.")
PROMPT = ("You are a pragmatic code reviewer. Review the DIFF and report ONLY real issues a "
          "careful engineer would want fixed before merge. Focus on: logic bugs, off-by-one/null/"
          "edge cases, missing error handling, resource leaks, security (injection, auth), and "
          "correctness. Skip pure style nits unless they hide a bug. For each finding output one "
          "line: `[SEV] file: detail` where SEV is HIGH/MED/LOW. Max 8 findings, most severe "
          "first. If clean, output exactly: CLEAN. No preamble.\n\n"
          "Languages: python\nStatic findings already caught (don't repeat verbatim):\n(none)\n\n"
          f"DIFF:\n{DIFF}")


def call(model: str) -> dict:
    payload = json.dumps({"model": model, "prompt": PROMPT, "system": SYSTEM,
        "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_ctx": 8192}, "cache": False}).encode()
    t0 = time.time()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        data = json.load(r)
    wall = time.time() - t0
    out = (data.get("response") or "").strip()
    ec, ed = data.get("eval_count", 0), data.get("eval_duration", 1)
    return {"output": out, "wall_s": round(wall, 1), "tok_s": round(ec / (ed / 1e9), 1) if ed else 0,
            "done": data.get("done_reason"), "n_findings": sum(1 for l in out.splitlines() if l.strip().startswith("["))}


def found_set(out: str) -> set[int]:
    low = out.lower()
    return {i for i, (_, toks) in enumerate(BUGS) if any(t.lower() in low for t in toks)}


def leaks_in(out: str) -> list[str]:
    low = out.lower()
    return [p for p in LEAKS if p in low]


def vram() -> int:
    try:
        return int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                                           stderr=subprocess.DEVNULL, text=True).strip())
    except Exception:
        return -1


def main():
    agg = {}
    for label, model in MODELS:
        runs = []
        for i in range(N):
            print(f"[{time.strftime('%H:%M:%S')}] {label} run {i+1}/{N}...", flush=True)
            r = call(model)
            (OUT / f"{label}_run{i+1}.txt").write_text(r["output"])
            runs.append({**r, "found": sorted(found_set(r["output"])), "leaks": leaks_in(r["output"])})
            print(f"   recall={len(runs[-1]['found'])}/6 tok/s={r['tok_s']} wall={r['wall_s']} done={r['done']}", flush=True)
        bug_hits = [sum(1 for r in runs if b in r["found"]) for b in range(len(BUGS))]
        agg[label] = {"model": model,
            "bug_hits": dict(zip([b[0] for b in BUGS], bug_hits)),
            "mean_recall": round(sum(len(r["found"]) for r in runs) / (N * len(BUGS)), 2),
            "mean_findings": round(sum(r["n_findings"] for r in runs) / N, 1),
            "mean_tok_s": round(sum(r["tok_s"] for r in runs) / N, 1),
            "mean_wall_s": round(sum(r["wall_s"] for r in runs) / N, 1),
            "any_leak": any(r["leaks"] for r in runs),
            "done_length_any": any(r["done"] == "length" for r in runs)}
        print()

    print("\n" + "=" * 72)
    print(f"PER-BUG HIT MATRIX (hits out of {N})  — quality discrimination")
    print("=" * 72)
    hdr = f"{'BUG':<26}" + "".join(f"{m:>8}" for m, _ in MODELS)
    print(hdr)
    for bi, (bname, _) in enumerate(BUGS):
        row = f"{bname:<26}"
        for label, _ in MODELS:
            h = agg[label]["bug_hits"][bname]
            row += f"{h}/{N}".rjust(8)
        print(row)
    print("-" * 72)
    print(f"{'MEAN recall (/6)':<26}" + "".join(f"{agg[m]['mean_recall']:>8}" for m, _ in MODELS))
    print(f"{'MEAN findings count':<26}" + "".join(f"{agg[m]['mean_findings']:>8}" for m, _ in MODELS))
    print(f"{'MEAN tok/s':<26}" + "".join(f"{agg[m]['mean_tok_s']:>8}" for m, _ in MODELS))
    print(f"{'MEAN wall s':<26}" + "".join(f"{agg[m]['mean_wall_s']:>8}" for m, _ in MODELS))
    print(f"{'any reasoning leak':<26}" + "".join(f"{str(agg[m]['any_leak']):>8}" for m, _ in MODELS))
    print(f"{'any done=length':<26}" + "".join(f"{str(agg[m]['done_length_any']):>8}" for m, _ in MODELS))
    (OUT / "summary.json").write_text(json.dumps(agg, indent=2))
    print(f"\nRaw per-run outputs → {OUT}/{model}_run*.txt")


if __name__ == "__main__":
    main()
