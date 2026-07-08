"""bug_finding — present a diff with known bugs, count how many the model finds.

Each PROMPTS entry is a diff snippet with N planted bugs. The scorer counts
how many of the EXPECTED_BUGS keywords appear in the model's response.

# vs-soft-allow  — end-to-end pipeline (diff -> call -> count hits -> rank).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ollama_bench.shared.gpu import paced
from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import prepare_scored_response

DEFAULT_COOLDOWN = 60  # seconds between models (GPU safety; sequential, never parallel)
GPU_TEMP_LIMIT = 75

# Each entry: id, prompt, expected keywords, and optional expected_groups.
# Bugs planted: B1 mutable default, B2 off-by-one, B3 None-deref, B4 bare except,
# B5 race (no lock), B6 SQL injection (string format).
PROMPTS: list[dict] = [
    {
        "id": "diff_v1",
        "n_bugs": 6,
        "expected": (
            "mutable default",
            "off-by-one",
            "none",
            "attributeerror",
            "bare except",
            "swallow",
            "race",
            "lock",
            "sql injection",
            "format",
            "execute",
        ),
        "expected_groups": (
            ("mutable default", "shared across calls"),
            ("off-by-one", "skips first"),
            ("none", "attributeerror"),
            ("bare except", "swallow"),
            ("race", "lock"),
            ("sql injection", "format", "execute"),
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
            "none",
            "typeerror",
            "keyerror",
            "index",
            "division",
            "zero",
            "modulo",
            "negative",
            "infinity",
        ),
        "expected_groups": (
            ("division", "zero", "zerodivision"),
            ("keyerror", "missing key"),
            ("n+1", "stride", "skips"),
            ("lo = lo or", "falsy", "zero"),
            ("hi==lo", "hi == lo", "division"),
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
    {
        "id": "diff_v3",
        "n_bugs": 6,
        "expected": (
            "path traversal",
            "zip slip",
            "timeout",
            "infinite",
            "resource leak",
            "close",
            "decode",
            "unicode",
            "overwrite",
            "atomic",
            "permission",
        ),
        "expected_groups": (
            ("path traversal", "zip slip", "../"),
            ("timeout", "hang", "infinite"),
            ("resource leak", "close", "with open"),
            ("decode", "unicode", "encoding"),
            ("overwrite", "atomic", "partial write"),
            ("permission", "chmod", "mode"),
        ),
        "prompt": """Review this diff. List ALL bugs. Be specific.

```diff
--- a/archive.py
+++ b/archive.py
@@ def unpack(zf, dest):
+    for name in zf.namelist():
+        target = os.path.join(dest, name)       # B1: path traversal / zip slip
+        data = zf.read(name)                    # B2: no size/timeout guard
+        f = open(target, "w")                   # B3: leaked file handle on error
+        f.write(data.decode())                  # B4: implicit encoding may fail
+        os.chmod(target, 0o777)                 # B5: unsafe permissions
+    return True                                 # B6: partial extraction not atomic
```

For each bug: `BUG: <one-line description>`. Then `COUNT: <n>`.""",
    },
    {
        "id": "diff_v4",
        "n_bugs": 5,
        "expected": (
            "timezone",
            "naive",
            "retry",
            "backoff",
            "idempotency",
            "duplicate",
            "secret",
            "token",
            "log",
            "status",
            "429",
        ),
        "expected_groups": (
            ("timezone", "naive", "utc"),
            ("retry", "backoff", "429"),
            ("idempotency", "duplicate"),
            ("secret", "token", "log"),
            ("status", "http", "raise"),
        ),
        "prompt": """Review this diff. List ALL bugs. Be specific.

```diff
--- a/payments.py
+++ b/payments.py
@@ def charge(client, user, amount, token):
+    expires = datetime.now() + timedelta(minutes=5)  # B1: naive local time
+    print("charging", user.id, token)                # B2: logs secret token
+    r = client.post("/charge", json={"u": user.id, "a": amount})
+    if r.status_code == 429:
+        return charge(client, user, amount, token)   # B3: recursive retry no backoff/limit
+    client.post("/receipt", json={"u": user.id})     # B4: non-idempotent duplicate side effect
+    return r.json()["id"]                            # B5: ignores non-2xx/missing id
```

For each bug: `BUG: <one-line description>`. Then `COUNT: <n>`.""",
    },
    {
        "id": "diff_v5_async",
        "n_bugs": 5,
        "expected": (
            "race",
            "concurrent",
            "gather",
            "shared",
            "mutable",
            "lock",
            "await",
            "exception",
            "cancel",
            "shield",
        ),
        "expected_groups": (
            ("race", "concurrent", "shared state"),
            ("gather", "return_exceptions", "cancel"),
            ("mutable", "shared", "append"),
            ("lock", "asyncio.lock"),
            ("shield", "timeout", "cancel"),
        ),
        "prompt": """Review this diff. List ALL bugs. Be specific.

```diff
--- a/async_workers.py
+++ b/async_workers.py
@@ async def process_batch(items):
+    results = []                              # B1: shared mutable list
+    async def process_one(item):
+        r = await aiohttp.get(item.url)
+        results.append(r.json())              # B2: concurrent append, no lock
+        return r
+    tasks = [process_one(i) for i in items]
+    responses = await asyncio.gather(*tasks)  # B3: no return_exceptions, one failure kills all
+    for r in responses:
+        if r.status == 429:
+            await asyncio.gather(process_one(r.item))  # B4: recursive gather, no backoff
+    return results
@@ async def fetch_with_timeout(url, timeout):
+    return await asyncio.wait_for(           # B5: timeout cancels inner task
+        aiohttp.get(url),                     #    but doesn't shield cleanup
+        timeout=timeout
+    )
```

For each bug: `BUG: <one-line description>`. Then `COUNT: <n>`.""",
    },
    {
        "id": "diff_v6_types",
        "n_bugs": 5,
        "expected": (
            "type",
            "dict",
            "list",
            "none",
            "falsy",
            "zero",
            "bytes",
            "str",
            "encode",
            "keyerror",
        ),
        "expected_groups": (
            ("dict", "list", "type error"),
            ("none", "falsy", "zero"),
            ("bytes", "str", "encode"),
            ("keyerror", "missing key", "get"),
            ("isinstance", "type check"),
        ),
        "prompt": """Review this diff. List ALL bugs. Be specific.

```diff
--- a/transform.py
+++ b/transform.py
@@ def merge_records(old, new):
+    for key in new:                           # B1: if new is a dict, iterates keys not items
+        old[key] = new[key]                   #    if new is a list, TypeError on key
@@ def safe_divide(a, b):
+    result = a / b if b else 0               # B2: b=0 is falsy, returns 0 instead of handling
@@ def process_payload(data):
+    body = data["body"]                       # B3: KeyError if "body" missing; use .get()
+    if body:                                  # B4: empty bytes b"" is falsy, valid payload lost
+        return body.decode("utf-8")           # B5: already str? .decode() AttributeError
+    return ""
```

For each bug: `BUG: <one-line description>`. Then `COUNT: <n>`.""",
    },
]


def _count_hits(out: str, expected: tuple) -> int:
    """Count distinct expected bugs.

    `expected` may be a flat tuple of keywords or grouped synonym tuples. Grouped
    scoring prevents one bug from being counted multiple times just because the
    model used several synonyms.
    """
    L = out.lower()
    if expected and isinstance(expected[0], tuple):
        return sum(1 for group in expected if any(str(kw).lower() in L for kw in group))
    return sum(1 for kw in expected if str(kw).lower() in L)


def _score(res: dict, n_bugs: int, expected: tuple) -> float:
    """Score = grouped recall + count calibration - leak penalty + tps bonus."""
    if "err" in res:
        return -100.0
    res, policy = prepare_scored_response(res)
    out = res["out"]
    L = out.lower()
    s = 0.0
    if policy["policy"] == "unsafe" and ("<think>" in L or "thinking process" in L):
        s -= 10
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if not out.strip():
        s -= 10
    hits = _count_hits(out, expected)
    recall = hits / max(n_bugs, 1)
    s += 12.0 * recall
    # Bonus for a calibrated COUNT line close to the planted bug count.
    m = __import__("re").search(r"count:\s*(\d+)", L)
    if m:
        reported = int(m.group(1))
        s += max(0.0, 2.0 - abs(reported - n_bugs) * 0.5)
    s += min(res.get("tps", 0) / 15.0, 2.0)
    return round(s, 2)


def run_model(model: str, opts: CallOpts) -> dict:
    out: list = []
    for p in PROMPTS:
        res = call(model, p["prompt"], opts=opts)
        expected = p.get("expected_groups", p["expected"])
        out.append({"id": p["id"], "sc": _score(res, p["n_bugs"], expected)})
    return {model: out}


def cmd_bug_finding(args: argparse.Namespace) -> int:
    """`ollama-bench bug-finding` entry point."""
    candidates = args.models or []
    if not candidates:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    cooldown = int(getattr(args, "cooldown", DEFAULT_COOLDOWN))
    temp_limit = int(getattr(args, "temp_limit", GPU_TEMP_LIMIT))
    print(
        f"# Bug-finding bench: {len(candidates)} models × {len(PROMPTS)} diffs "
        f"(cooldown={cooldown}s)",
        file=sys.stderr,
    )
    opts = CallOpts(num_predict=400, num_ctx=8192)

    # Sequential + GPU-paced (never parallel — the old ThreadPoolExecutor pool
    # oversaturated the GPU). run_model returns {model: [...]}; paced keys by model.
    results = paced(
        candidates, lambda m: run_model(m, opts)[m], cooldown=cooldown, temp_limit=temp_limit
    )

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
        f.write(
            "Scoring: grouped bug recall + COUNT calibration - leak_penalty + "
            f"tps_bonus. {len(PROMPTS)} diffs per model.\n\n"
        )
        f.write("| # | Score | Model |\n|---|---|---|\n")
        for i, (m, sc) in enumerate(ranked, 1):
            f.write(f"| {i} | {sc:.2f} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser(
        "bug-finding", parents=[parent], help="Diff-review bench (count bugs found)."
    )
    p.add_argument(
        "-m", "--models", nargs="+", required=True, help="Models to bench (space-separated)."
    )
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.add_argument(
        "--cooldown",
        type=int,
        default=DEFAULT_COOLDOWN,
        help=f"Seconds to wait between models (default: {DEFAULT_COOLDOWN}).",
    )
    p.add_argument(
        "--temp-limit",
        type=int,
        default=GPU_TEMP_LIMIT,
        help=f"Max GPU °C before forced wait (default: {GPU_TEMP_LIMIT}).",
    )
    p.set_defaults(cmd=cmd_bug_finding)
