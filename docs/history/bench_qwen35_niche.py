#!/usr/bin/env python3
"""Niche bench: search-ai on retrieval-rerank + pii-v4 on PII-scrub vs qwen3.5:4b baseline.

Tests whether the task-specific fine-tunes beat the universal default on their NICHE
(the only place a fine-tune should win). N=3, think=False, temp=0.2.
"""
from __future__ import annotations
import json, time, urllib.request, sys
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
OUT = Path("/home/eldi/bench/ollama/results_qwen35_niche")
OUT.mkdir(exist_ok=True)

# ---- RERANK task: 5 snippets, rank by relevance to query. Correct order known. ----
QUERY = "how to refresh an expired JWT access token using a refresh token"
SNIPPETS = [
    "S1: To refresh an expired access token, POST your refresh_token to /auth/refresh; the server verifies it and issues a new JWT access token pair.",  # rank 1
    "S2: JWT (JSON Web Token) is a compact, URL-safe means of representing claims between two parties, defined in RFC 7519.",  # rank 5 (definition, not refresh)
    "S3: When the access token expires, the client should call the refresh endpoint silently to obtain a new token without forcing the user to log in again.",  # rank 2
    "S4: OAuth 2.0 grants include authorization_code, client_credentials, and password; each has a different token issuance flow.",  # rank 4 (oauth, adjacent)
    "S5: Refresh tokens are long-lived credentials used to obtain new access tokens; they should be stored securely and rotated on use.",  # rank 3
]
CORRECT_ORDER = ["S1", "S3", "S5", "S4", "S2"]
RERANK_PROMPT = ("Rank these snippets by relevance to the query (most relevant first). "
    "Output ONLY the snippet IDs in order, comma-separated, e.g. S3,S1,S4,S5,S2. No explanation.\n\n"
    f"Query: {QUERY}\n\n" + "\n".join(SNIPPETS))

# ---- PII SCRUB task: redact planted PII ----
PII_TEXT = ("Ticket #4821: Customer John Reyes (email: j.reyes@acmecorp.io, phone: +1-415-555-0192) "
    "reported a charge of $1,240.77 on card ending 8821. SSN on file: 412-77-6301. "
    "Reach him at john.reyes.work@protonmail.com or backup 0917-555-884. Account ID: AC-99213.")
PII_PLANTED = 7  # j.reyes@acmecorp.io, +1-415-555-0192, 412-77-6301, john.reyes.work@protonmail.com, 0917-555-884, 8821(card), AC-99213(account)
PII_REDACT_TOKENS = ["[email", "[phone", "[ssn", "[card", "[account", "redacted", "***", "rex", "[name", "xxx", "hidden"]
PII_PROMPT = ("Redact ALL personally identifiable information (emails, phone numbers, SSN, card digits, "
    "account IDs, names) from the text below. Replace each with a tag like [EMAIL], [PHONE], [SSN], "
    "[CARD], [ACCOUNT], [NAME]. Preserve the rest. Output ONLY the redacted text.\n\n" + PII_TEXT)

LEAKS = ["<think","</think","let me think","i need to","the user wants","thinking process","0000"]


def gen(model, prompt, num_predict=400):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.0, "num_ctx": 8192, "num_predict": num_predict},
        "cache": False}).encode()  # temp=0 for deterministic ranking/redaction
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=200) as r:
            d = json.load(r)
    except Exception as e:
        return None, 0, f"ERR:{type(e).__name__}"
    out = (d.get("response") or "").strip()
    ec, ed = d.get("eval_count", 0), d.get("eval_duration", 1)
    return out, (round(ec/(ed/1e9),1) if ed else 0), round(time.time()-t0,1)


def rerank_score(out):
    """Extract ordered IDs, score vs correct (top-1 correct + kendall-ish positional hits)."""
    import re
    ids = re.findall(r"S[1-5]", out)
    if not ids:
        return 0, "no-ids"
    # positional correctness: how many of 5 are in correct position
    pos = sum(1 for i, x in enumerate(ids[:5]) if i < len(CORRECT_ORDER) and x == CORRECT_ORDER[i])
    top1 = 1 if ids[0] == CORRECT_ORDER[0] else 0
    return pos + top1, ",".join(ids[:5])


def pii_score(out):
    low = out.lower()
    redacted = sum(1 for t in PII_REDACT_TOKENS if t.lower() in low)
    # raw PII leaked? (email pattern, ssn pattern present = failure)
    leaked_email = bool(__import__("re").search(r"[\w.]+@[\w.]+", out))
    leaked_ssn = bool(__import__("re").search(r"\d{3}-\d{2}-\d{4}", out))
    leaked_phone = bool(__import__("re").search(r"\d{3}[-.]?\d{3}[-.]?\d{3,4}", out))
    leaks_raw = sum([leaked_email, leaked_ssn, leaked_phone])
    return redacted, leaks_raw


def run(label, model, task, prompt, scorer):
    res = []
    for i in range(N):
        out, tps, wall = gen(model, prompt)
        if out is None:
            res.append({"fail": tps}); print(f"  [{label}] {task} {i+1}: FAIL {tps}"); continue
        score, detail = scorer(out)
        (OUT / f"{label}_{task}_{i+1}.txt").write_text(out)
        res.append({"score": score, "detail": detail, "tps": tps})
        print(f"  [{label}] {task} {i+1}/{N}: score={score} detail={detail} tps={tps}", flush=True)
    ok = [r for r in res if "score" in r]
    return round(sum(r["score"] for r in ok)/len(ok), 2) if ok else None


def main():
    print("=== RERANK (search_V2 vs baseline) — score=positional hits + top1, max 6 ===")
    r_base = run("qwen35_base", "qwen3.5:4b", "rerank", RERANK_PROMPT, rerank_score)
    r_search = run("search_V2", "jbaptistedaniel/search-ai-qwen3.5-4B-V2-q4", "rerank", RERANK_PROMPT, rerank_score)
    r_crow = run("crow_9b", "jaahas/crow:9b", "rerank", RERANK_PROMPT, rerank_score)
    print(f"\n  RERANK mean: base={r_base}  search_V2={r_search}  crow_9b={r_crow}  (max 6)")
    print("\n=== PII SCRUB (pii_v4 vs baseline) — score=redact-tags(more=better), raw_leaks(lower=better) ===")
    p_base = run("qwen35_base", "qwen3.5:4b", "pii", PII_PROMPT, pii_score)
    p_pii = run("pii_v4", "wwydmanski/qwen3.5-4b-pii-v4:q4_0", "pii", PII_PROMPT, pii_score)
    p_crow = run("crow_9b", "jaahas/crow:9b", "pii", PII_PROMPT, pii_score)
    print(f"\n  PII mean: base={p_base}  pii_v4={p_pii}  crow_9b={p_crow}  (score=tags, detail=raw_leaks)")
    (OUT / "summary.json").write_text(json.dumps({"rerank": {"base":r_base,"search_V2":r_search,"crow_9b":r_crow},
        "pii": {"base":p_base,"pii_v4":p_pii,"crow_9b":p_crow}}, indent=2))


if __name__ == "__main__":
    main()
