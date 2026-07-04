#!/usr/bin/env python3
"""Fast smoke pass across ALL installed Ollama models.

One short prompt per model. Goal: surface the broken/leaky/empty ones FAST.
Records: time, tokens, output length, leak-flag, first 100 chars.
NO deletion. Output is a CSV-like table the controller classifies from.
"""
from __future__ import annotations
import json, time, urllib.request, urllib.error, sys
from pathlib import Path

OLLAMA = "http://localhost:11434"
OUT = Path("/home/eldi/bench/ollama/results_smoke_all.tsv")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Skip embeddings + duplicates of base (we keep both, but tag separately)
SMOKE_PROMPT = (
    "Reply in ONE sentence: what is the difference between a Python list and a tuple?"
)
NUM_PREDICT = 80   # short; just enough to see leaks
TIMEOUT = 180

def get_models() -> list[str]:
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        data = json.load(r)
    return [m["name"] for m in data.get("models", [])]

def smoke(name: str) -> dict:
    body = json.dumps({
        "model": name,
        "prompt": SMOKE_PROMPT,
        "stream": False,
        "think": False,   # TOP-LEVEL, critical for qwen3.x + gemma4 (suppresses thinking)
        "options": {
            "temperature": 0.2,
            "num_predict": NUM_PREDICT,
            "num_ctx": 2048,
        },
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/generate",
        data=body, headers={"Content-Type": "application/json"}, method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return {"name": name, "status": "http_error",
                "err": f"HTTP {e.code}: {e.read().decode(errors='replace')[:120]}"}
    except Exception as e:
        return {"name": name, "status": "net_error",
                "err": f"{type(e).__name__}: {str(e)[:120]}"}
    dt = time.perf_counter() - t0
    out = data.get("response", "") or ""
    ptoks = data.get("prompt_eval_count", 0)
    etoks = data.get("eval_count", 0)
    done = data.get("done_reason", "?")
    tps = (etoks / dt) if dt > 0 and etoks > 0 else 0.0

    # leak gates (v2 — "len=0 + non-zero tps" with think=False at top-level
    # is a HARD leak: the model produced tokens but no usable response)
    out_lower = out.lower()
    leaks = []
    if "<think>" in out_lower or "</think>" in out_lower:
        leaks.append("think_tag")
    if "thinking process:" in out_lower:
        leaks.append("thinking_process")
    if "as an ai" in out_lower or "i cannot" in out_lower:
        leaks.append("refusal_pattern")
    if out.strip() == "" and etoks > 0:
        leaks.append("empty_response")
    if out.strip() == "" and etoks == 0:
        leaks.append("no_eval_tokens")
    if done == "length" and etoks >= NUM_PREDICT - 1 and len(out) > NUM_PREDICT * 3:
        # done=length AND we hit num_predict AND output is wildly long → budget burn
        leaks.append("budget_burn")

    return {
        "name": name,
        "status": "ok" if not leaks else "leak:" + ",".join(leaks),
        "dt_s": round(dt, 2),
        "tps": round(tps, 1),
        "ptoks": ptoks,
        "etoks": etoks,
        "len": len(out),
        "done": done,
        "head": out.strip()[:120].replace("\n", " "),
    }

def main():
    models = get_models()
    print(f"# Smoke pass over {len(models)} models", file=sys.stderr)
    rows = []
    for i, name in enumerate(models, 1):
        r = smoke(name)
        rows.append(r)
        # compact progress to stderr
        flag = r.get("status", "?").split(":")[0]
        print(f"[{i:2d}/{len(models)}] {flag:7s} "
              f"{r.get('dt_s', 0):6.2f}s "
              f"tps={r.get('tps', 0):4.1f} "
              f"len={r.get('len', 0):4d} "
              f"{name[:60]}", file=sys.stderr)

    # write TSV
    keys = ["name", "status", "dt_s", "tps", "ptoks", "etoks", "len", "done", "head"]
    with OUT.open("w") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    print(f"\nWrote {OUT} ({len(rows)} rows)", file=sys.stderr)

if __name__ == "__main__":
    main()