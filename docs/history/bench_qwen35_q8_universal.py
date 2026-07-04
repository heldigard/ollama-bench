#!/usr/bin/env python3
"""Universal-default battery: qwen3.5:4b-q8_0 vs qwen3.5:4b (Q4) across the 4 roles the
universal default serves: bug-finding (N=3), rerank (N=3), PII scrub (N=3), smart-trim.

User mandate: is Q8 a better UNIVERSAL default? Q8 is the most-critical slot (DEFAULT_GEN_MODEL,
smart-trim primary, commit-draft/diff-review CODE_MODEL, rerank, web_research extract).
Quality > speed. think=False; temp=0.2 for bug/smart-trim, temp=0 for rerank/PII (deterministic).
"""
from __future__ import annotations
import json, re, time, urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
MODELS = [("qwen35_q8", "qwen3.5:4b-q8_0"), ("qwen35_q4", "qwen3.5:4b")]
OUT = Path("/home/eldi/bench/ollama/results_new4")
OUT.mkdir(exist_ok=True)

# ---------- BUG-FINDING (6-bug diff) ----------
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
BUGS = [
    ("B1 off-by-one", ["off-by-one","off by one","returns -1","return -1","no match","not found","n=0","first occurrence"]),
    ("B2 SQLi", ["injection","parameteri","placeholder","f-string","parameterized"]),
    ("B3 bare except", ["bare except","bare","except:","swallow","catch-all","catches everything"]),
    ("B4 mutable default", ["mutable default","default arg","cache={}","mutable","persists across","shared"]),
    ("B5 resource leak", ["never closes","not closed","context manager","leak","file handle","unclosed","resource leak"]),
    ("B6 None deref", ["keyerror",".get(","key exist","missing key","unchecked","charge_id","order is none"]),
]
BUG_SYS = ("You review code diffs. Reply plain text. Format `[SEV] file: detail`. "
           "Max 8 findings. If clean: CLEAN. No preamble, no fences.")
BUG_PROMPT = ("Review the DIFF, report real issues (logic bugs, off-by-one/null, missing error "
              "handling, leaks, security). `[SEV] file: detail` per finding. If clean: CLEAN.\n\nDIFF:\n" + DIFF)

# ---------- RERANK ----------
QUERY = "how to refresh an expired JWT access token using a refresh token"
SNIPPETS = [
    "S1: To refresh an expired access token, POST your refresh_token to /auth/refresh; the server verifies it and issues a new JWT access token pair.",
    "S2: JWT (JSON Web Token) is a compact, URL-safe means of representing claims between two parties, defined in RFC 7519.",
    "S3: When the access token expires, the client should call the refresh endpoint silently to obtain a new token without forcing the user to log in again.",
    "S4: OAuth 2.0 grants include authorization_code, client_credentials, and password; each has a different token issuance flow.",
    "S5: Refresh tokens are long-lived credentials used to obtain new access tokens; they should be stored securely and rotated on use.",
]
CORRECT = ["S1", "S3", "S5", "S4", "S2"]
RERANK_PROMPT = ("Rank these snippets by relevance (most relevant first). Output ONLY snippet IDs "
    "comma-separated, e.g. S3,S1,S4,S5,S2. No explanation.\n\nQuery: " + QUERY + "\n\n" + "\n".join(SNIPPETS))

# ---------- PII ----------
PII_TEXT = ("Ticket #4821: Customer John Reyes (email: j.reyes@acmecorp.io, phone: +1-415-555-0192) "
    "reported a charge of $1,240.77 on card ending 8821. SSN on file: 412-77-6601. "
    "Reach him at john.reyes.work@protonmail.com or backup 0917-555-884. Account ID: AC-99213.")
PII_PROMPT = ("Redact ALL PII (emails, phones, SSN, card digits, account IDs, names). Replace each "
    "with [EMAIL],[PHONE],[SSN],[CARD],[ACCOUNT],[NAME]. Preserve the rest. Output ONLY redacted text.\n\n" + PII_TEXT)

# ---------- SMART-TRIM (5-bullet entity preservation) ----------
TRIM_TEXT = (
    "We migrated the billing service from Node 18 to Node 22 LTS. The Stripe webhook handler was "
    "rewritten in TypeScript and moved to /src/webhooks/stripe.ts. The old handler in billing.js is "
    "DELETED. Webhook signature verification now uses STRIPE_WEBHOOK_SECRET (was STRIPE_SECRET_KEY). "
    "Added retry with exponential backoff (max 5 retries, base 200ms). Tests live in "
    "__tests__/stripe.test.ts and require the STRIPE_TEST_KEY env var. Deploy via the azure-pipelines.yml "
    "'deploy-billing' stage. Rollback = revert the commit; the old handler is gone so no shadow mode.")
TRIM_ENTITIES = ["node 22", "stripe.ts", "billing.js", "stripe_webhook_secret", "stripe_secret_key",
                 "5 retries", "200ms", "stripe.test.ts", "stripe_test_key", "deploy-billing", "rollback"]
TRIM_PROMPT = ("Summarize the following technical note as EXACTLY 5 bullet points. Preserve every "
    "specific identifier (file paths, env vars, numbers, commands). Plain text bullets, no preamble.\n\n" + TRIM_TEXT)
LEAKS = ["<think", "</think", "let me think", "i need to", "the user wants", "thinking process", "0000"]


def gen(model, prompt, system=None, num_predict=500, temp=0.2):
    body = {"model": model, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": temp, "num_ctx": 8192, "num_predict": num_predict}, "cache": False}
    if system:
        body["system"] = system
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=200) as r:
        d = json.load(r)
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec/(ed/1e9),1) if ed else 0), d.get("done_reason")


def run_bugs(label, model):
    runs = []
    for i in range(3):
        out, tps, done = gen(model, BUG_PROMPT, BUG_SYS, temp=0.2)
        (OUT / f"{label}_bug_{i+1}.txt").write_text(out)
        low = out.lower()
        found = {bn for bn, _ in BUGS if any(t.lower() in low for t in _)}
        leaks = [p for p in LEAKS if p in low]
        runs.append({"found": sorted(found), "n": len(found), "tps": tps, "done": done, "leaks": leaks})
        print(f"  [{label}] bug {i+1}/3: {len(found)}/6 done={done} leaks={leaks or '-'}", flush=True)
    return {"mean": round(sum(r["n"] for r in runs)/6, 2), "runs": runs}


def run_rerank(label, model):
    runs = []
    for i in range(3):
        out, tps, done = gen(model, RERANK_PROMPT, temp=0.0, num_predict=120)
        (OUT / f"{label}_rerank_{i+1}.txt").write_text(out)
        ids = re.findall(r"S[1-5]", out)
        pos = sum(1 for j, x in enumerate(ids[:5]) if x == CORRECT[j])
        runs.append({"order": ",".join(ids[:5]), "pos_correct": pos, "tps": tps})
        print(f"  [{label}] rerank {i+1}/3: pos={pos}/5 order={','.join(ids[:5])}", flush=True)
    return {"mean_pos": round(sum(r["pos_correct"] for r in runs)/3, 2), "runs": runs}


def run_pii(label, model):
    runs = []
    for i in range(3):
        out, tps, done = gen(model, PII_PROMPT, temp=0.0, num_predict=400)
        (OUT / f"{label}_pii_{i+1}.txt").write_text(out)
        # raw PII leaked = failure
        leaked_email = len(re.findall(r"[\w.]+@[\w.]+\.\w+", out))
        leaked_ssn = len(re.findall(r"\d{3}-\d{2}-\d{4}", out))
        leaked_phone = len(re.findall(r"\d[\d.-]{7,}\d", out))
        total_leak = leaked_email + leaked_ssn + leaked_phone
        runs.append({"raw_leaks": total_leak, "tps": tps})
        print(f"  [{label}] pii {i+1}/3: raw_leaks={total_leak} (email={leaked_email} ssn={leaked_ssn} phone={leaked_phone})", flush=True)
    return {"mean_leaks": round(sum(r["raw_leaks"] for r in runs)/3, 2), "runs": runs}


def run_trim(label, model):
    runs = []
    for i in range(3):
        out, tps, done = gen(model, TRIM_PROMPT, temp=0.2, num_predict=400)
        (OUT / f"{label}_trim_{i+1}.txt").write_text(out)
        low = out.lower()
        pres = sum(1 for e in TRIM_ENTITIES if e in low)
        bullets = out.count("\n- ") + out.count("\n* ") + (1 if out.startswith(("- ", "* ")) else 0)
        runs.append({"entities": f"{pres}/{len(TRIM_ENTITIES)}", "n": pres, "bullets": bullets, "tps": tps, "done": done})
        print(f"  [{label}] trim {i+1}/3: entities={pres}/{len(TRIM_ENTITIES)} bullets~{bullets} done={done}", flush=True)
    return {"mean_ent": round(sum(r["n"] for r in runs)/3, 2), "runs": runs}


def main():
    agg = {}
    for label, model in MODELS:
        print(f"\n=== {label} ({model}) ===", flush=True)
        agg[label] = {"model": model,
                      "bugfinding": run_bugs(label, model),
                      "rerank": run_rerank(label, model),
                      "pii": run_pii(label, model),
                      "smarttrim": run_trim(label, model)}
    print("\n" + "=" * 78)
    print(f"{'MODEL':<12}{'bug/6':>8}{'rerank/5':>10}{'pii_leak':>10}{'trim_ent/11':>13}{'bug_tps':>9}")
    print("-" * 78)
    for label, _ in MODELS:
        a = agg[label]
        bt = round(sum(r["tps"] for r in a["bugfinding"]["runs"])/3, 1)
        print(f"{label:<12}{a['bugfinding']['mean']:>8}{a['rerank']['mean_pos']:>10}"
              f"{a['pii']['mean_leaks']:>10}{a['smarttrim']['mean_ent']:>13}{bt:>9}")
    print("\nInterpretation: bug/rerank/trim HIGHER=better; pii_leak LOWER=better.")
    # merge
    sm = OUT / "summary.json"
    if sm.exists():
        data = json.loads(sm.read_text())
        for label, _ in MODELS:
            if label in data:
                data[label]["universal"] = agg[label]
        sm.write_text(json.dumps(data, indent=2, default=str))
    print(f"\nOutputs -> {OUT}/")


if __name__ == "__main__":
    main()
