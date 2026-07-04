#!/usr/bin/env python3
"""crow:4b (new, 3.1GB) vs crow:9b (synth+bug-finding champ, 6.5GB). Can the 4b match the 9b
as a LIGHTER co-loadable alt? Tests the 2 roles crow serves: web_research synth (6pt rubric)
+ bug-finding (6-bug N=3). think=False, temp 0.2 (synth/bug) — uses oc.generate (strip-think).
"""
from __future__ import annotations
import json, sys, time, re
from pathlib import Path

sys.path.insert(0, "/home/eldi/bench/ollama")
sys.path.insert(0, "/home/eldi/.claude/scripts")
import bench_webresearch as bw  # noqa: E402
import ollama_client as oc  # noqa: E402

MODELS = [("crow_4b", "jaahas/crow:4b"), ("crow_9b", "jaahas/crow:9b")]
OUT = Path("/home/eldi/bench/ollama/results_new4")
N_BUG = 3

# ---- SYNTH (Acme fixture, reuse from bench_webresearch) ----
SYNTH_KEYS = {
    "s1_128k": ["128,000", "128k", "128 000"],
    "s2_contra": ["200k", "200,000", "retract", "wrong", "incorrect", "disagree", "contradict"],
    "s3_not_stable": ["not stable", "not fully stable", "no", "unstable", "partially unstable", "inconsistent", "varies"],
    "s4_64k": ["64k", "64,000", "low-memory", "low memory", "preset"],
}
PRICING = ["pricing", "$2", "per million", "price"]
LEAK = ["<think", "</think", "let me think", "i need to", "the user wants", "first, let"]

# ---- BUG-FINDING (6-bug diff) ----
DIFF = r"""+def find_nth_occurrence(haystack, needle, n):
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
BUGS = [("B1 off-by-one", ["off-by-one","off by one","returns -1","return -1","no match","n=0","first occurrence"]),
    ("B2 SQLi", ["injection","parameteri","placeholder","f-string","parameterized"]),
    ("B3 bare except", ["bare except","bare","except:","swallow","catch-all"]),
    ("B4 mutable default", ["mutable default","default arg","cache={}","mutable","persists across","shared"]),
    ("B5 resource leak", ["never closes","not closed","context manager","leak","file handle","unclosed","resource leak"]),
    ("B6 None deref", ["keyerror",".get(","key exist","missing key","unchecked","charge_id","order is none"])]
BUG_SYS = ("You review code diffs. Reply plain text. Format `[SEV] file: detail`. Max 8 findings. If clean: CLEAN. No preamble, no fences.")
BUG_PROMPT = ("Review the DIFF, report real issues (logic bugs, off-by-one/null, missing error handling, "
              "leaks, security). `[SEV] file: detail` per finding. If clean: CLEAN.\n\nDIFF:\n" + DIFF)


def synth_score(text):
    low = text.lower()
    s = {k: any(t in low for t in v) for k, v in SYNTH_KEYS.items()}
    s["no_pricing"] = not any(p in low for p in PRICING)
    s["clean"] = not any(k in low for k in LEAK)
    s["score"] = sum(v for v in s.values() if isinstance(v, bool))
    return s


def bug_find(text):
    low = text.lower()
    return {bn for bn, t in BUGS if any(x.lower() in low for x in t)}


def oc_gen(model, prompt, system=None, num_predict=500, temp=0.2):
    full = f"{system}\n\n{prompt}" if system else prompt
    t0 = time.time()
    out = oc.generate(full, model=model, temperature=temp, num_ctx=16384 if system is None else 8192,
                      cache=False, base_url="http://localhost:11434") or ""
    return out, round(time.time() - t0, 1)


def main():
    agg = {}
    sp, ss = bw.synth_prompt()
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        # synth
        out, dt = oc_gen(model, sp, num_predict=700)
        (OUT / f"{label}_synth.txt").write_text(out)
        sc = synth_score(out)
        print(f"  [{label}] synth: {sc['score']}/6 {dt}s clean={sc['clean']} "
              f"128k={sc['s1_128k']} contra={sc['s2_contra']} notStable={sc['s3_not_stable']} cave64k={sc['s4_64k']}", flush=True)
        # bug-finding N=3
        bug_runs = []
        for i in range(N_BUG):
            out, dt = oc_gen(model, BUG_PROMPT, BUG_SYS, num_predict=500)
            (OUT / f"{label}_bug_{i+1}.txt").write_text(out)
            found = bug_find(out)
            low = out.lower()
            leaks = [k for k in LEAK if k in low]
            bug_runs.append({"n": len(found), "found": sorted(found), "leaks": leaks})
            print(f"  [{label}] bug {i+1}/{N_BUG}: {len(found)}/6 leaks={leaks or '-'}", flush=True)
        agg[label] = {"synth": sc, "bug": {"mean": round(sum(r["n"] for r in bug_runs)/N_BUG, 2), "runs": bug_runs}}
    print("\n" + "=" * 70)
    print(f"{'MODEL':<10}{'synth/6':>8}{'clean':>7}{'bug_mean/6':>11}")
    for label, _ in MODELS:
        print(f"{label:<10}{agg[label]['synth']['score']:>8}{str(agg[label]['synth']['clean']):>7}{agg[label]['bug']['mean']:>11}")
    sm = OUT / "summary.json"
    if sm.exists():
        data = json.loads(sm.read_text())
        for label, _ in MODELS:
            data[label] = {"crow_roles": agg[label]}
        sm.write_text(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
