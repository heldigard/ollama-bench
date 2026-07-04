#!/usr/bin/env python3
"""
Quick test for untested models before prune.
3 tests per model × 7 models = 21 runs, ~5 min.
"""
from __future__ import annotations
import json, subprocess, time, urllib.request, urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path

OLLAMA = "http://localhost:11434"
TIMEOUT = 180
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_quicktest")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Models to test (untested in earlier bench)
TARGETS = [
    "jessegross/gemma4:12b-mlx",
    "mannix/omnimerge-v4:Q3_K_L",
    "mannix/omnimerge-v4:IQ3_M",
    "mannix/omnimerge-v4:Q3_K_M",
    "mannix/omnimerge-v4:Q2_K_L",
    "mannix/omnimerge-v4-mtp:IQ4_XS",
    "fredrezones55/Qwen3.6-35B-A3B-APEX:I-Mini",
]

# Quick smoke: improve + compact + code (3 domains)
TESTS = [
    ("improve_1", "improve",
     "Rewrite this vague request as a structured agent spec. Input: 'fix the auth bug'"),
    ("compact_1", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). Session: User added conftest.py at /home/eldi/proj. pytest collected 12 tests but 3 fail on import 'No module named app'. Root cause being investigated. User decided to stay on uv. Plan next: check sys.path, reinstall app in editable mode, re-run pytest."),
    ("code_1", "code",
     "Write Python validate_email(s: str) -> bool using stdlib only. Handle None/empty. 3 lines."),
]


def gpu_mem() -> int:
    try:
        return int(subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            timeout=5, text=True).strip())
    except Exception:
        return -1


def run(model: str, prompt: str, num_predict: int = 512) -> dict:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_predict": num_predict, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            d = json.load(r)
        return {
            "ok": True, "total_s": time.perf_counter() - t0,
            "eval_tokens": d.get("eval_count", 0),
            "prompt_tokens": d.get("prompt_eval_count", 0),
            "output": d.get("response", ""),
            "done_reason": d.get("done_reason", "?"),
        }
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def unload(model: str):
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"{OLLAMA}/api/generate",
            data=json.dumps({"model": model, "keep_alive": 0}).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        ), timeout=10)
    except Exception:
        pass


def main():
    print(f"Quick-testing {len(TARGETS)} untested models × {len(TESTS)} tests\n")
    for m in TARGETS:
        print(f"\n=== {m} ===")
        for test_id, domain, prompt in TESTS:
            r = run(m, prompt)
            if not r["ok"]:
                print(f"  {test_id} ... ERR {r['error'][:60]}")
                continue
            tps = r["eval_tokens"] / r["total_s"] if r["total_s"] > 0 else 0
            vram = gpu_mem()
            out_preview = r["output"][:80].replace("\n", " ")
            print(f"  {test_id} ... OK {tps:>5.1f} tok/s  {r['total_s']:>5.1f}s  vram={vram}MiB  done={r['done_reason']}  | {out_preview}")
            Path(OUTPUT_DIR / f"{m.replace('/', '__').replace(':', '_')}.jsonl").open("a").write(
                json.dumps({"model": m, "test_id": test_id, "domain": domain,
                            "tps": tps, "total_s": r["total_s"], "vram": vram,
                            "output": r["output"], "done_reason": r["done_reason"]}) + "\n")
            unload(m)


if __name__ == "__main__":
    main()