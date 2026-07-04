#!/usr/bin/env python3
"""
Ollama benchmark - Triage pass.
4 prompts per model × 16 models = 64 tests, ~10-15 min on RTX 5080.
Then deep-pass on winners.
"""
from __future__ import annotations
import json
import subprocess
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

OLLAMA = "http://localhost:11434"
TIMEOUT = 300
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_triage")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 4 prompts, one per domain. Concise enough to fit in 256 tokens.
TRIAGE_TESTS = [
    ("improve_1", "improve",
     "Rewrite this vague request as a structured agent spec (GOAL, FILES, STEPS, ACCEPTANCE). One-line input: 'fix the auth bug'"),
    ("compact_1", "compact",
     "Summarize this session as a 5-bullet handoff: task, decisions, current step, blockers, next. Session: User added conftest.py at /home/eldi/proj. pytest collected 12 tests but 3 fail on import 'No module named app'. Root cause being investigated. User decided to stay on uv. Plan next: check sys.path, reinstall app in editable mode, re-run pytest."),
    ("code_1", "code",
     "Write Python `validate_email(s: str) -> bool` using stdlib only. Handle None/empty/whitespace. 3 lines max."),
    ("reason_1", "reason",
     "If A > B, B > C, C = D-2, D = 10: what is A? Show 3 steps. End with ANSWER: <number>"),
]


def get_installed_models() -> list[dict[str, Any]]:
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        data = json.load(r)
    seen: set[str] = set()
    out = []
    skip_patterns = ["embed", "-mlx"]  # skip embeddings + Apple MLX format
    for m in data.get("models", []):
        name = m["name"]
        if any(p in name.lower() for p in skip_patterns):
            continue
        # dedupe by ID
        mid = m.get("digest") or m.get("id") or name
        if mid in seen:
            continue
        seen.add(mid)
        size_gb = m.get("size", 0) / (1024 ** 3)
        det = m.get("details", {})
        out.append({
            "name": name,
            "id": mid,
            "size_gb": round(size_gb, 2),
            "param": det.get("parameter_size", "?"),
            "quant": det.get("quantization_level", "?"),
        })
    return out


def get_gpu_mem() -> int:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            timeout=5, text=True
        ).strip()
        return int(out)
    except Exception:
        return -1


@dataclass
class BenchResult:
    model: str
    test_id: str
    domain: str
    status: str
    error: str = ""
    ttft_s: float = 0.0
    total_s: float = 0.0
    eval_tokens: int = 0
    prompt_tokens: int = 0
    tok_per_s: float = 0.0
    gpu_mem_peak_mib: int = 0
    output: str = ""


def run_generate(model: str, prompt: str, num_predict: int = 512) -> dict:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        # think=False: matches how improve-prompt / smart-trim call Ollama,
        # prevents the model from spending num_predict on hidden thinking tokens.
        "think": False,
        "options": {"temperature": 0.2, "num_predict": num_predict, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/generate", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    t1 = time.perf_counter()
    # Some models (gemma4 thinking, qwen3 thinking) put answer in "thinking" or
    # "message.content" instead of "response". Capture all three.
    response = data.get("response", "")
    thinking = data.get("thinking", "")
    msg = data.get("message", {})
    content = msg.get("content", "") if isinstance(msg, dict) else ""
    output = response or content or thinking or ""
    return {
        "total_s": t1 - t0,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "eval_tokens": data.get("eval_count", 0),
        "ttft_s": (data.get("prompt_eval_duration", 0) / 1e9) if data.get("prompt_eval_duration") else 0.0,
        "output": output,
        "response_field": response,
        "thinking_field": thinking,
        "content_field": content,
        "done_reason": data.get("done_reason", "?"),
    }


def bench_one(model: dict, test_id: str, domain: str, prompt: str) -> BenchResult:
    name = model["name"]
    res = run_generate(name, prompt)
    mem_peak = get_gpu_mem()
    if "error" in res:
        return BenchResult(model=name, test_id=test_id, domain=domain, status="error",
                           error=res["error"], gpu_mem_peak_mib=mem_peak)
    tps = res["eval_tokens"] / res["total_s"] if res["total_s"] > 0 else 0
    return BenchResult(
        model=name, test_id=test_id, domain=domain, status="ok",
        ttft_s=round(res["ttft_s"], 3),
        total_s=round(res["total_s"], 3),
        eval_tokens=res["eval_tokens"], prompt_tokens=res["prompt_tokens"],
        tok_per_s=round(tps, 2), gpu_mem_peak_mib=mem_peak,
        output=res["output"],
    )


def unload(model: str):
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                f"{OLLAMA}/api/generate",
                data=json.dumps({"model": model, "keep_alive": 0}).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            ), timeout=10,
        )
    except Exception:
        pass


def main():
    models = get_installed_models()
    print(f"[bench] {len(models)} models × {len(TRIAGE_TESTS)} tests = {len(models)*len(TRIAGE_TESTS)} runs\n")
    for m in models:
        print(f"  {m['name']:<58} {m['size_gb']:.2f}GB  {m['quant']}")

    results: list[BenchResult] = []
    total = len(models) * len(TRIAGE_TESTS)
    done = 0
    for m in models:
        for test_id, domain, prompt in TRIAGE_TESTS:
            done += 1
            print(f"[{done:>3}/{total}] {m['name'][:35]:<35} {test_id} ...", end=" ", flush=True)
            r = bench_one(m, test_id, domain, prompt)
            if r.status == "ok":
                print(f"OK  {r.tok_per_s:>5.1f} tok/s  {r.total_s:>5.1f}s  vram={r.gpu_mem_peak_mib}MiB")
            else:
                print(f"ERR {r.error[:60]}")
            results.append(r)
            unload(m["name"])
            out = OUTPUT_DIR / f"{m['name'].replace('/', '__').replace(':', '_')}.jsonl"
            with out.open("a") as f:
                f.write(json.dumps(asdict(r)) + "\n")

    # Per-model summary
    print(f"\n{'='*90}\nSUMMARY\n{'='*90}")
    by_model: dict[str, list[BenchResult]] = {}
    for r in results:
        by_model.setdefault(r.model, []).append(r)
    print(f"{'model':<58} {'ok':>3} {'err':>3} {'avg_tps':>8} {'avg_ttft':>8} {'peak_vram':>10} {'avg_total':>9}")
    for mname, rs in sorted(by_model.items()):
        ok = [r for r in rs if r.status == "ok"]
        err = [r for r in rs if r.status == "error"]
        if ok:
            avg_tps = sum(r.tok_per_s for r in ok) / len(ok)
            avg_ttft = sum(r.ttft_s for r in ok) / len(ok)
            avg_total = sum(r.total_s for r in ok) / len(ok)
        else:
            avg_tps = avg_ttft = avg_total = 0
        peak_vram = max(r.gpu_mem_peak_mib for r in rs)
        print(f"{mname:<58} {len(ok):>3} {len(err):>3} {avg_tps:>8.2f} {avg_ttft:>8.2f} {peak_vram:>10} {avg_total:>9.2f}")

    # Save
    with (OUTPUT_DIR / "all.json").open("w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\nFull: {OUTPUT_DIR / 'all.json'}")


if __name__ == "__main__":
    main()