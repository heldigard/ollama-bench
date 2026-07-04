#!/usr/bin/env python3
"""Head-to-head bench: composer v2 quants on the bug-finding task (its championship use).

Replicates diff-review.py's REAL prompt + system on a planted-bug diff, then scores
recall (bugs found), false positives, cleanliness (reasoning/tool-token leaks), tok/s,
and done_reason across: Q4_K_M (current) vs Q6_K vs Q8_0, + a rep_pen=1.1 variant.

Lesson from prior sessions (durable): Q-scores HIDE reasoning leaks. So we capture the
RAW output verbatim per run for manual inspection, and check done_reason=length.
"""
from __future__ import annotations
import json, time, urllib.request, urllib.error, sys, subprocess
from pathlib import Path

OLLAMA = "http://localhost:11434/api/generate"
MODELS = [
    ("Q4_K_M_current", "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest"),
    ("Q4_K_M_reppen",  "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest"),  # same, rep_pen=1.1
    ("Q6_K",           "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q6_K"),
    ("Q8_0",           "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0"),
]
OUT = Path("/home/eldi/bench/ollama/results_composer_quants")
OUT.mkdir(exist_ok=True)

# ---- Diff with 6 planted bugs (Python, realistic) -------------------------
DIFF = r"""diff --git a/src/orders/service.py b/src/orders/service.py
index 1111111..2222222 100644
--- a/src/orders/service.py
+++ b/src/orders/service.py
@@ -10,9 +10,32 @@ async def get_order(order_id):
+def find_nth_occurrence(haystack, needle, n):
+    idx = haystack.find(needle)
+    for _ in range(n):
+        idx = haystack.find(needle, idx + 1)
+    return idx
+
+async def fetch_user_orders(conn, user_id):
+    query = f"SELECT * FROM orders WHERE user_id = '{user_id}' ORDER BY created_at"
+    rows = conn.execute(query).fetchall()
+    return rows
+
+def parse_config(raw):
+    def coerce(v, typ=int):
+        try:
+            return typ(v)
+        except:
+            return v
+    return {k: coerce(v) for k, v in raw.items()}
+
+def load_translations(path, cache={}):
+    f = open(path)
+    data = json.load(f)
+    cache[path] = data
+    return data
+
+async def cancel_order(order_id):
+    order = await get_order(order_id)
+    charge = order["payment"]["charge_id"]
+    stripe.refund(charge)
"""

# ---- Rubric: planted bugs + trigger tokens (found if ANY token, ci) -------
BUGS = [
    ("B1 off-by-one (find_nth over-counts, ignores n=0/missing)",
     ["off-by-one", "off by one", "range(n)", "n = 0", "first occurrence", "idx = -1", "not found"]),
    ("B2 SQL injection (f-string user_id into query)",
     ["injection", "parameteri", "placeholder", "f-string", "format string", "?", "sql"]),
    ("B3 bare except swallows (parse_config.coerce)",
     ["bare except", "except:", "swallow", "bare", "catch-all", "catches everything"]),
    ("B4 mutable default arg (cache={})",
     ["mutable default", "default arg", "cache={}", "shared across", "mutable", "dict default"]),
    ("B5 resource leak (open() no close/with)",
     ["with open", "context manager", "leak", "not closed", "close()", "finally", "file handle"]),
    ("B6 None/KeyError deref (order['payment']['charge_id'] unchecked)",
     ["none", "keyerror", ".get(", "key exist", "missing", "nonexistent", "null", "unchecked"]),
]

SYSTEM = (
    "You review code diffs. Reply with plain text only. Format each "
    "finding as `[SEV] file: detail` where SEV is HIGH/MED/LOW. "
    "Max 8 findings, most severe first. If the diff is clean, output "
    "exactly: CLEAN. No preamble, no code fences, no JSON."
)
PROMPT = (
    "You are a pragmatic code reviewer. Review the DIFF and report ONLY real "
    "issues a careful engineer would want fixed before merge. Focus on: logic "
    "bugs, off-by-one/null/edge cases, missing error handling, resource leaks, "
    "security (injection, auth), and correctness. Skip pure style nits unless "
    "they hide a bug. For each finding output one line: "
    "`[SEV] file: detail` where SEV is HIGH/MED/LOW. Max 8 findings, most "
    "severe first. If the diff is clean, output exactly: CLEAN. No preamble.\n\n"
    "Languages: python\n"
    "Static findings already caught (don't repeat these verbatim):\n(none)\n\n"
    f"DIFF:\n{DIFF}"
)

LEAK_PATTERNS = ["<think", "</think", "<|think|", "<|tool_call", "<|channel",
                 "0000", "let me think", "i'll analyze", "first, let"]


def call(model: str, rep_pen: float | None) -> dict:
    opts = {"temperature": 0.2, "num_ctx": 8192}
    if rep_pen is not None:
        opts["repeat_penalty"] = rep_pen
    payload = json.dumps({
        "model": model, "prompt": PROMPT, "system": SYSTEM,
        "stream": False, "think": False, "options": opts, "cache": False,
    }).encode()
    t0 = time.time()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}
    wall = time.time() - t0
    out = (data.get("response") or "").strip()
    ec = data.get("eval_count", 0)
    ed = data.get("eval_duration", 1)
    tps = ec / (ed / 1e9) if ed else 0
    return {
        "output": out, "wall_s": round(wall, 1),
        "tok_s": round(tps, 1), "eval_count": ec,
        "done_reason": data.get("done_reason"), "raw": data,
    }


def score(out: str) -> dict:
    low = out.lower()
    found, missed = [], []
    for name, toks in BUGS:
        if any(t.lower() in low for t in toks):
            found.append(name)
        else:
            missed.append(name)
    leaks = [p for p in LEAK_PATTERNS if p in low]
    # false-positive proxy: findings lines that don't map to any planted bug
    fp_lines = [ln for ln in out.splitlines() if ln.strip().startswith("[")
                and not any(t.lower() in low for _, ts in BUGS for t in ts if t.startswith("["))]
    return {
        "recall": f"{len(found)}/{len(BUGS)}", "found": found, "missed": missed,
        "leaks": leaks, "fp_proxy": len(fp_lines),
        "clean": out.strip().upper() == "CLEAN",
    }


def vram() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader"],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "?"


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    results = {}
    print(f"{'MODEL':<18} {'recall':<8} {'leaks':<14} {'tok/s':<7} {'wall':<6} {'done':<10} VRAM")
    print("-" * 80)
    for label, model in MODELS:
        if only and label not in only and model.split(":")[-1] not in only:
            continue
        rep_pen = 1.1 if label == "Q4_K_M_reppen" else None
        print(f"[{time.strftime('%H:%M:%S')}] running {label} ({model}) rep_pen={rep_pen}...")
        sys.stdout.flush()
        r = call(model, rep_pen)
        if "error" in r:
            print(f"  ERROR: {r['error']}")
            results[label] = r
            continue
        sc = score(r["output"])
        results[label] = {"model": model, "rep_pen": rep_pen, **sc,
                          "tok_s": r["tok_s"], "wall_s": r["wall_s"],
                          "done_reason": r["done_reason"], "eval_count": r["eval_count"],
                          "output": r["output"]}
        print(f"{label:<18} {sc['recall']:<8} {str(sc['leaks'] or '-'):<14} "
              f"{r['tok_s']:<7} {r['wall_s']:<6} {str(r['done_reason']):<10} {vram()}")
        (OUT / f"{label}.txt").write_text(r["output"])
    (OUT / "summary.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nRaw outputs → {OUT}/*.txt\nSummary → {OUT}/summary.json")


if __name__ == "__main__":
    main()
