#!/usr/bin/env python3
"""Deep bug-finding bench: 2 clean qwopus35-v3 survivors vs the bug-finding champions.

6-bug diff fixture, N=3 reps, per-bug hit matrix — the diff-review discriminator
(longctx/reason saturated at 9/10, can't rank). think=False, temp=0.2.

Refs: Mobius 1.00 (gold), crow 0.94, qwen3.5 0.39, SetneufPT 4B-Coder-MTP 0.33.
"""
from __future__ import annotations
import json, time, urllib.request, subprocess
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = 3
MODELS = [
    ("v3_4b_coder_mtp", "qwopus35-4b-coder-mtp:latest"),
    ("v3_4b_coder",     "qwopus35-4b-coder:latest"),
    ("setneuf_4b_mtp",  "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU"),  # current longctx champ
    ("qwen35_4b",       "qwen3.5:4b"),                                         # universal
    ("crow_9b",         "jaahas/crow:9b"),                                     # bug-finding ref 0.94
    ("mobius",          "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf"),    # gold 1.00
]
OUT = Path("/home/eldi/bench/ollama/results_qwopus_v3")
OUT.mkdir(exist_ok=True)

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
+"""
BUGS = [
    ("B1 off-by-one/find_nth", ["off-by-one","off by one","returns -1","return -1","no match","not found","invalid index","corrupts subsequent","first occurrence","n=0"]),
    ("B2 SQL injection",       ["injection","parameteri","placeholder","f-string","format string","parameterized"]),
    ("B3 bare except",         ["bare except","bare","except:","swallow","catch-all","catches everything","systemexit","keyboardinterrupt"]),
    ("B4 mutable default",     ["mutable default","default arg","cache={}","mutable","same dict","persists across","shared"]),
    ("B5 resource leak",       ["never closes","not closed","closes","context manager","leak","file handle","unclosed","open(path)","without closing","resource leak"]),
    ("B6 None/KeyError deref", ["keyerror",".get(","key exist","missing key","unchecked","malformed","payment","charge_id","order is none","returns none"]),
]
SYSTEM = ("You review code diffs. Reply with plain text only. Format each finding as "
          "`[SEV] file: detail` (SEV HIGH/MED/LOW). Max 8 findings, most severe first. "
          "If clean, output: CLEAN. No preamble, no fences, no JSON.")
PROMPT = ("You are a pragmatic code reviewer. Review the DIFF and report ONLY real issues a careful "
          "engineer would want fixed before merge. Focus on logic bugs, off-by-one/null/edge cases, missing "
          "error handling, resource leaks, security, correctness. For each finding: `[SEV] file: detail`. "
          "Max 8 findings, most severe first. If clean: CLEAN. No preamble.\n\n"
          "Languages: python\nStatic findings already caught:\n(none)\n\nDIFF:\n" + DIFF)
LEAKS = ["<think","</think","<|think|","let me think","i'll analyze","first, let","i need to",
         "the user wants","let me parse","step 1","thinking process","0000"]


def gen(model):
    payload = json.dumps({"model": model, "prompt": PROMPT, "system": SYSTEM, "stream": False,
        "think": False, "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 500},
        "cache": False}).encode()
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
        runs = []
        for i in range(N):
            print(f"[{time.strftime('%H:%M:%S')}] {label} run {i+1}/{N}...", flush=True)
            out, tps, wall, done = gen(model)
            (OUT / f"{label}_bug_{i+1}.txt").write_text(out)
            low = out.lower()
            found = {bi for bi,(_,t) in enumerate(BUGS) if any(x.lower() in low for x in t)}
            leaks = [p for p in LEAKS if p in low]
            runs.append({"found": sorted(found), "leaks": leaks, "tps": tps, "done": done})
            print(f"   recall={len(found)}/6 leaks={leaks or '-'} tps={tps} done={done}", flush=True)
        hits = [sum(bi in r["found"] for r in runs) for bi in range(len(BUGS))]
        agg[label] = {"model": model, "bug_hits": dict(zip([b[0] for b in BUGS], hits)),
            "mean_recall": round(sum(len(r["found"]) for r in runs)/(N*len(BUGS)),2),
            "mean_tps": round(sum(r["tps"] for r in runs)/N,1), "any_leak": any(r["leaks"] for r in runs)}
    print("\n" + "=" * 92)
    print(f"PER-BUG HIT MATRIX (/{N})  + mean recall + tok/s + leak")
    print("=" * 92)
    print(f"{'BUG':<26}" + "".join(f"{m[:11]:>11}" for m,_ in MODELS))
    for bi,(bn,_) in enumerate(BUGS):
        print(f"{bn:<26}" + "".join(f"{agg[m]['bug_hits'][bn]}/{N}".rjust(11) for m,_ in MODELS))
    print("-" * 92)
    print(f"{'MEAN recall':<26}" + "".join(f"{agg[m]['mean_recall']:>11}" for m,_ in MODELS))
    print(f"{'MEAN tok/s':<26}" + "".join(f"{agg[m]['mean_tps']:>11}" for m,_ in MODELS))
    print(f"{'any leak':<26}" + "".join(f"{str(agg[m]['any_leak']):>11}" for m,_ in MODELS))
    # merge into the smoke summary.json
    sm = OUT / "summary.json"
    if sm.exists():
        data = json.loads(sm.read_text())
        for label, _ in MODELS:
            if label in data:
                data[label]["bugfinding"] = agg[label]
        sm.write_text(json.dumps(data, indent=2, default=str))
    print(f"\nOutputs -> {OUT}/  (bug-finding merged into summary.json)")


if __name__ == "__main__":
    main()
