# vs-soft-allow  — end-to-end pipeline (smoke_one → cmd_smoke → add_parser).
"""smoke - 1-prompt leak gate per model.

Fast first-pass filter. ~3s/model. Use to disqualify broken/leaky/empty models
BEFORE running the slower deep bench. Output: TSV of (name, status, dt, tps,
len, done, head).
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

from ollama_bench.shared.gpu import wait_gpu_cool
from ollama_bench.shared.ollama import CallOpts, call, get_model_names
from ollama_bench.shared.paths import result_path
from ollama_bench.shared.scorer import detect_leaks, leaks_are_strippable

SMOKE_PROMPT = "Reply in ONE sentence: what is the difference between a Python list and a tuple?"
NUM_PREDICT = 80
# Smoke is the light/fast gate, so cooldown defaults to 0 (the temp-gate still
# protects a hot card). Pass --cooldown N to pace model loads. The heavy deep
# bench carries the long cooldown by default. See memory: bench-gpu-safety.
DEFAULT_COOLDOWN = 0
GPU_TEMP_LIMIT = 75
_SMOKE_KEYS = ["name", "status", "strippable", "dt_s", "tps", "etoks", "len", "done", "head"]


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


def _append_smoke_row(row: dict, out_path: Path) -> None:
    """Append one smoke result; write the header if the file is new.

    Incremental (kill-safe): each model is flushed before the next starts, so a
    kill/crash never loses already-smoked models.
    """
    write_header = not out_path.exists()
    with out_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=_SMOKE_KEYS, delimiter="\t")
        if write_header:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in _SMOKE_KEYS})


def _smoke_completed(out_path: Path) -> set[str]:
    """Names already present in the smoke TSV (for --resume skip)."""
    if not out_path.exists():
        return set()
    names: set[str] = set()
    with out_path.open(newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("name"):
                names.add(r["name"])
    return names


def _is_embedding_model(name: str) -> bool:
    """Heuristic: embedding models can't /api/generate (they return HTTP 400).
    Skip them in smoke (they have no generative output to leak-check)."""
    low = name.lower()
    return "embed" in low or low.startswith("bge-") or "/bge-" in low


def cmd_smoke(args):
    names = args.models if args.models else get_model_names()
    # Skip embedding models — they error on /api/generate and have no output to gate.
    names = [n for n in names if not _is_embedding_model(n)]
    resume = bool(getattr(args, "resume", False))
    cooldown = int(getattr(args, "cooldown", DEFAULT_COOLDOWN))
    temp_limit = int(getattr(args, "temp_limit", GPU_TEMP_LIMIT))
    out_path = Path(args.output) if args.output else result_path("smoke_all")

    # Fresh (non-resume) run starts clean so appends don't stack on stale rows.
    if not resume and out_path.exists():
        out_path.unlink()

    # Resume: skip models already smoked.
    completed = _smoke_completed(out_path) if resume else set()
    if resume and completed:
        before = len(names)
        names = [n for n in names if n not in completed]
        skipped = before - len(names)
        if skipped:
            print(f"# Resume: skipping {skipped} already-smoked models", file=sys.stderr)
    if not names:
        print("# Resume: all models already smoked", file=sys.stderr)
        return 0

    print(f"# Smoke pass over {len(names)} models (cooldown={cooldown}s)", file=sys.stderr)
    for i, name in enumerate(names, 1):
        # GPU safety: temp-gate every model (a hot card waits); pace between
        # models only when --cooldown is set. No cooldown before the first.
        wait_gpu_cool(temp_limit)
        if i > 1:
            time.sleep(cooldown)
        r = smoke_one(name)
        _append_smoke_row(r, out_path)  # incremental save (kill-safe)
        flag = r["status"].split(":")[0]
        print(
            f"[{i:2d}/{len(names)}] {flag:10s} {r.get('dt_s', 0):6.2f}s "
            f"tps={r.get('tps', 0):4.1f} len={r.get('len', 0):4d} {name[:60]}",
            file=sys.stderr,
        )
    print(f"\nWrote {out_path} ({len(names)} new rows)", file=sys.stderr)
    return 0


def add_parser(sub, parent):
    p = sub.add_parser(
        "smoke", parents=[parent], help="1-prompt leak gate per model (fast filter)."
    )
    p.add_argument("-m", "--models", nargs="*", help="Models to smoke (default: all installed).")
    p.add_argument("-o", "--output", help="Output TSV path (default: cache dir).")
    p.add_argument(
        "--resume",
        action="store_true",
        help="Skip models already present in the output TSV (incremental run).",
    )
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
    p.set_defaults(cmd=cmd_smoke)
