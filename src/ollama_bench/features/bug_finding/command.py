"""bug_finding — present a diff with known bugs, count how many the model finds.

Each PROMPTS entry is a diff snippet with N planted bugs. The scorer counts
how many of the EXPECTED_BUGS keywords appear in the model's response.

# vs-soft-allow  — end-to-end pipeline (diff -> call -> count hits -> rank).
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path

# Each entry: (id, prompt, expected_bug_keywords).
# Bugs planted: B1 mutable default, B2 off-by-one, B3 None-deref, B4 bare except,
# B5 race (no lock), B6 SQL injection (string format).
PROMPTS: list[dict] = [
    {
        "id": "diff_v1",
        "n_bugs": 6,
        "expected": (
            "mutable default", "off-by-one", "none", "attributeerror",
            "bare except", "swallow", "race", "lock", "sql injection",
            "format", "execute",
        ),
        "prompt": """Review this diff. List ALL bugs you find. Be specific (line + why).

```diff
--- a/service.py
+++ b/service.py
@@ def process(items=None, db):
-    if items is None:
-        items = []
+    items = items or []            # B1: mutable default ref shared across calls
     for i in range(1, len(items)):  # B2: off-by-one skips first element
         val = items[i].lower()      # B3: items[i] could be None -> AttributeError
-        try:
+        try:
             db.save(val)
-        except:                     # B4: bare except swallows KeyboardInterrupt etc
+        except Exception:
             pass
     if not lock_acquired:
         update_shared_state()       # B5: race — no lock around shared state
     cursor.execute(
         f"SELECT * FROM users WHERE name = '{user_input}'"  # B6: SQL injection
     )
```

For each bug, output a line like: `BUG: <one-line description>`. Then `COUNT: <n>`.""",
    },
    {
        "id": "diff_v2",
        "n_bugs": 5,
        "expected": (
            "none", "typeerror", "keyerror", "index", "division", "zero",
            "modulo", "negative", "infinity",
        ),
        "prompt": """Review this diff. List ALL bugs. Be specific.

```diff
--- a/calc.py
+++ b/calc.py
@@ def ratio(a, b):
+    return a / b                    # B1: ZeroDivisionError if b == 0
@@ def get(data, key, default=None):
+    return data[key] or default     # B2: KeyError if key missing, ignores falsy default
@@ def chunk(lst, n):
+    return [lst[i:i+n] for i in range(0, len(lst), n+1)]  # B3: skips items (n+1 stride)
@@ def normalize(x, lo=None, hi=None):
+    lo = lo or 0                    # B4: lo=0 silently becomes falsy, can't distinguish
+    hi = hi or 100
+    return (x - lo) / (hi - lo)     # B5: division — if hi==lo, ZeroDivision
```

For each bug: `BUG: <one-line description>`. Then `COUNT: <n>`.""",
    },
]


def _count_hits(out: str, expected: tuple[str, ...]) -> int:
    """Count how many distinct expected-bug keywords appear in output."""
    L = out.lower()
    return sum(1 for kw in expected if kw.lower() in L)


def _score(res: dict, n_bugs: int, expected: tuple[str, ...]) -> float:
    """Score = 2 * hits - 0.5 * leaks_penalty + tps_bonus. Range -10 to ~14."""
    if "err" in res:
        return -100.0
    out = res["out"]
    L = out.lower()
    s = 0.0
    if "<think>" in L or "thinking process" in L:
        s -= 5
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if not out.strip():
        s -= 10
    hits = _count_hits(out, expected)
    s += 2.0 * hits  # 2 points per bug found
    # Bonus if model produced a COUNT line
    if "count:" in L:
        s += 1.0
    s += min(res.get("tps", 0) / 15.0, 2.0)
    return round(s, 2)


def run_model(model: str, opts: CallOpts) -> dict:
    out: list = []
    for p in PROMPTS:
        res = call(model, p["prompt"], opts=opts)
        out.append({"id": p["id"], "sc": _score(res, p["n_bugs"], p["expected"])})
    return {model: out}


def cmd_bug_finding(args: argparse.Namespace) -> int:
    """`ollama-bench bug-finding` entry point."""
    candidates = args.models or []
    if not candidates:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    print(f"# Bug-finding bench: {len(candidates)} models × {len(PROMPTS)} diffs", file=sys.stderr)
    opts = CallOpts(num_predict=400, num_ctx=8192)

    results: dict = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m, opts): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(candidates)}] {m[:55]}  done", file=sys.stderr, flush=True)

    # Aggregate
    ranked = []
    for m, r in results.items():
        if not isinstance(r, list) or not r:
            continue
        scores = [it["sc"] for it in r if "sc" in it]
        avg = round(sum(scores) / len(scores), 2) if scores else -100.0
        ranked.append((m, avg))
    ranked.sort(key=lambda x: -x[1])

    out_path = Path(args.output) if args.output else result_path("bug_finding", ext="md")
    with out_path.open("w") as f:
        f.write("# Bug-Finding Bench — diff-review task\n\n")
        f.write(f"Scoring: 2 * (bugs found) - leak_penalty + tps_bonus. {len(PROMPTS)} diffs per model.\n\n")
        f.write("| # | Score | Model |\n|---|---|---|\n")
        for i, (m, sc) in enumerate(ranked, 1):
            f.write(f"| {i} | {sc:.2f} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser("bug-finding", parents=[parent],
                       help="Diff-review bench (count bugs found).")
    p.add_argument("-m", "--models", nargs="+", required=True,
                   help="Models to bench (space-separated).")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_bug_finding)