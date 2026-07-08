# vs-soft-allow  — end-to-end pipeline (smoke_one → cmd_smoke → add_parser).
"""smoke - 1-prompt leak gate per model.

Fast first-pass filter. ~3s/model. Use to disqualify broken/leaky/empty models
BEFORE running the slower deep bench. Output: TSV of (name, status, dt, tps,
len, done, head).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from ollama_bench.shared.ollama import CallOpts, call, get_model_names
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import detect_leaks, leaks_are_strippable

SMOKE_PROMPT = "Reply in ONE sentence: what is the difference between a Python list and a tuple?"
NUM_PREDICT = 80


def _status_from(res, out):
    """Return (status, strippable). strippable='1' if leaks are thinking-trace
    only (salvageable via strip_reasoning); '0' otherwise (clean, refusal, or error)."""
    if "err" in res:
        return res["err"].split(":")[0], "0"
    leaks = detect_leaks(out)
    if not out.strip() and res.get("etoks", 0) > 0:
        leaks.append("empty_response")
    if not leaks:
        return "ok", "0"
    strippable = "1" if leaks_are_strippable(leaks) else "0"
    return "leak:" + ",".join(leaks), strippable


def smoke_one(name):
    res = call(name, SMOKE_PROMPT, opts=CallOpts(num_predict=NUM_PREDICT, num_ctx=2048))
    out = res.get("out", "")
    status, strippable = _status_from(res, out)
    return {
        "name": name,
        "status": status,
        "strippable": strippable,
        "dt_s": res.get("dt", 0),
        "tps": res.get("tps", 0),
        "etoks": res.get("etoks", 0),
        "len": len(out),
        "done": res.get("done", "?"),
        "head": out.strip()[:120].replace("\n", " "),
    }


def _write_tsv(rows, out_path):
    keys = ["name", "status", "strippable", "dt_s", "tps", "etoks", "len", "done", "head"]
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def _is_embedding_model(name: str) -> bool:
    """Heuristic: embedding models can't /api/generate (they return HTTP 400).
    Skip them in smoke (they have no generative output to leak-check)."""
    low = name.lower()
    return "embed" in low or low.startswith("bge-") or "/bge-" in low


def cmd_smoke(args):
    names = args.models if args.models else get_model_names()
    # Skip embedding models — they error on /api/generate and have no output to gate.
    names = [n for n in names if not _is_embedding_model(n)]
    print(f"# Smoke pass over {len(names)} models", file=sys.stderr)
    rows = []
    for i, name in enumerate(names, 1):
        r = smoke_one(name)
        rows.append(r)
        flag = r["status"].split(":")[0]
        print(
            f"[{i:2d}/{len(names)}] {flag:10s} {r.get('dt_s', 0):6.2f}s "
            f"tps={r.get('tps', 0):4.1f} len={r.get('len', 0):4d} {name[:60]}",
            file=sys.stderr,
        )
    out_path = Path(args.output) if args.output else result_path("smoke_all")
    _write_tsv(rows, out_path)
    print(f"\nWrote {out_path} ({len(rows)} rows)", file=sys.stderr)
    return 0


def add_parser(sub, parent):
    p = sub.add_parser(
        "smoke", parents=[parent], help="1-prompt leak gate per model (fast filter)."
    )
    p.add_argument("-m", "--models", nargs="*", help="Models to smoke (default: all installed).")
    p.add_argument("-o", "--output", help="Output TSV path (default: cache dir).")
    p.set_defaults(cmd=cmd_smoke)
