#!/usr/bin/env python3
"""Deep bench: tier-1 Qwen3.5 candidates vs baseline on HARD task (6-bug diff finding).

Compact saturated at 10/10 in smoke (no discrimination). Bug-finding stresses reasoning+code
(qwen3.5 is code-fallback → on-role). Per-bug hit matrix across N runs is the real signal.
think=False, temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request, sys
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
MODELS = [
    ("qwen35_4b_BASE", "qwen3.5:4b"),
    ("q8_0",           "qwen3.5:4b-q8_0"),
    ("search_V2",      "jbaptistedaniel/search-ai-qwen3.5-4B-V2-q4"),
    ("eve_solforg3",   "jeffgreen311/eve-qwen35-4b-solforg3-v2"),
    ("jaahas_crow_9b", "jaahas/crow:9b"),
    ("thinhphan_q4km", "thinhphan97/qwen3.5-4B:q4km"),
]
OUT = Path("/home/eldi/bench/ollama/results_qwen35_deep")
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
            (OUT / f"{label}_run{i+1}.txt").write_text(out)
            low = out.lower()
            found = {bi for bi,(_,t) in enumerate(BUGS) if any(x.lower() in low for x in t)}
            leaks = [p for p in LEAKS if p in low]
            runs.append({"found": sorted(found), "leaks": leaks, "tps": tps, "done": done})
            print(f"   recall={len(found)}/6 leaks={leaks or '-'} tps={tps} done={done}", flush=True)
        hits = [sum(bi in r["found"] for r in runs) for bi in range(len(BUGS))]
        agg[label] = {"model": model, "bug_hits": dict(zip([b[0] for b in BUGS], hits)),
            "mean_recall": round(sum(len(r["found"]) for r in runs)/(N*len(BUGS)),2),
            "mean_tps": round(sum(r["tps"] for r in runs)/N,1), "any_leak": any(r["leaks"] for r in runs)}
    print("\n" + "=" * 74)
    print(f"PER-BUG HIT MATRIX (/{N})  + recall + tok/s")
    print("=" * 74)
    print(f"{'BUG':<24}" + "".join(f"{m[:9]:>10}" for m,_ in MODELS))
    for bi,(bn,_) in enumerate(BUGS):
        print(f"{bn:<24}" + "".join(f"{agg[m]['bug_hits'][bn]}/{N}".rjust(10) for m,_ in MODELS))
    print("-" * 74)
    print(f"{'MEAN recall':<24}" + "".join(f"{agg[m]['mean_recall']:>10}" for m,_ in MODELS))
    print(f"{'MEAN tok/s':<24}" + "".join(f"{agg[m]['mean_tps']:>10}" for m,_ in MODELS))
    print(f"{'any leak':<24}" + "".join(f"{str(agg[m]['any_leak']):>10}" for m,_ in MODELS))
    (OUT / "summary.json").write_text(json.dumps(agg, indent=2, default=str))


if __name__ == "__main__":
    main()
