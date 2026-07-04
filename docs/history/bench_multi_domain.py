#!/usr/bin/env python3
"""
Ollama benchmark harness — Gemma4/Qwen3.6 selection
Tests: load time, tok/s, TTFT, VRAM, quality across 3 domains.
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
TIMEOUT = 600  # 10min per gen, generous
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Test prompts -----------------------------------------------------------

# A) Prompt-improvement: vague → structured spec
IMPROVE_PROMPTS = [
    ("improve_vague_1",
     "fix the auth bug"),
    ("improve_vague_2",
     "haz que el dashboard cargue mas rapido"),
    ("improve_vague_3",
     "i need a thing that converts csv to json, like the file thing"),
    ("improve_vague_4",
     "el test falla a veces, no se porque"),
]

# B) Smart-compact: transcript → handoff
COMPACT_PROMPTS = [
    ("compact_1", """Session transcript (condensed). Goal: summarize as handoff note preserving task, decisions, current step, blockers, next action.

[Earlier] User asked about Python venv setup on WSL2. Assistant explained uv vs pip, recommended uv. Created .venv via 'uv venv'. Activated.
[Earlier] Discussion about why their existing imports broke. Root cause: site-packages vs .venv/lib conflict. Fixed by removing PYTHONPATH override.
[Earlier] User asked about cross-platform wheel compatibility. Assistant noted manylinux2014 vs musllinux. Decided to pin --python 3.12 --platform manylinux2014.
[Now] User: 'pero ahora pytest no encuentra los tests'. Assistant running pytest --collect-only. Output shows 'collected 0 items'.
[Now] Root cause being investigated: tests/ dir missing __init__.py, or conftest.py not at root. Will check next.
[Now] User: 'tambien falla ruff, dice no module'. Same root cause - ruff needs the .venv on path.
[Next] Plan: add conftest.py at project root, reinstall dev deps in .venv, re-run pytest + ruff.
[Decision] Stay on uv, drop pip completely.
[Blocked] No blockers."""),
    ("compact_2", """Session transcript. Goal: handoff summary.

[Earlier] Discussing Azure Function cold-start. 4s baseline unacceptable. User wants <500ms.
[Earlier] Options: premium plan, always-on, native deps. Decided always-on + premium EP1.
[Earlier] Tested locally with func start. Got 1.2s with no warmup.
[Now] User: 'deploy it'. Need to: zip package, push via az functionapp deploy. Auth via az login already done.
[Now] Concern: storage account connection string in local.settings.json - must NOT include in zip.
[Decision] Use --build-native-deps flag for cryptography native wheels.
[Blocked] None.
[Next] Build pkg.zip (exclude .venv, __pycache__, Tests, .git, local.settings.json). Then az functionapp deploy."""),
    ("compact_3", """Session transcript. Goal: handoff summary.

[Earlier] Bug: agent repeating last tool call. User noticed in claude code session.
[Earlier] Suspected duplicate-command-guard hook issue.
[Earlier] Investigated ~/.claude/hooks/duplicate-command-guard.py. Found: matches on normalized command, but bash chained commands with ; were split incorrectly.
[Now] Fix attempt: use shlex.split instead of regex. User approved.
[Now] Re-tested: hook now catches 95% of dupes. Edge case: heredocs still slip through.
[Decision] ship fix, log heredoc as known gap in dead-ends.md.
[Blocked] Heredoc dedup needs different approach (stateful hash?). Defer.
[Next] Commit fix to ~/.claude/hooks/. Update memory bank note."""),
]

# C) Code: small Python tasks
CODE_PROMPTS = [
    ("code_1",
     "Write a Python function `validate_email(s: str) -> bool` using ONLY stdlib (re or email.utils). Handle None/empty/whitespace. Explain edge cases in 2 lines."),
    ("code_2",
     "Write a Python async function `fetch_all(urls: list[str]) -> list[dict]` using aiohttp. Use semaphore to cap concurrency at 10. Return results preserving input order. Include exception handling per URL."),
    ("code_3",
     "Write a Python function `chunk_text(text: str, max_tokens: int) -> list[str]` that splits text into chunks of approx max_tokens, splitting on sentence boundaries when possible. No external deps."),
]

# D) Reasoning (small, deterministic scoring)
REASON_PROMPTS = [
    ("reason_1",
     "If A > B and B > C, and C = D - 2, and D = 10, what is A? Show reasoning in 3 steps max. End with: ANSWER: <number>"),
    ("reason_2",
     "A box has 3 red, 2 blue, 5 green balls. P(red then green without replacement)? Show work. End with: ANSWER: <fraction>"),
]

ALL_TESTS = (
    [(f"improve_{n}", "improve", p) for n, p in IMPROVE_PROMPTS] +
    [(f"compact_{n}", "compact", p) for n, p in COMPACT_PROMPTS] +
    [(f"code_{n}", "code", p) for n, p in CODE_PROMPTS] +
    [(f"reason_{n}", "reason", p) for n, p in REASON_PROMPTS]
)

# ---- Ollama helpers ---------------------------------------------------------

def get_installed_models() -> list[dict[str, Any]]:
    """Get unique models by ID with name mapping."""
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        data = json.load(r)
    seen_ids: set[str] = set()
    out = []
    for m in data.get("models", []):
        mid = m.get("digest", m.get("id", ""))
        if mid in seen_ids:
            continue
        seen_ids.add(mid)
        # Skip embeddings
        name = m["name"]
        if "embed" in name.lower():
            continue
        size_gb = m.get("size", 0) / (1024 ** 3)
        det = m.get("details", {})
        out.append({
            "name": name,
            "id": mid,
            "size_gb": round(size_gb, 2),
            "family": det.get("family", "?"),
            "param": det.get("parameter_size", "?"),
            "quant": det.get("quantization_level", "?"),
            "context": det.get("context_length", "?"),
        })
    return out


def get_gpu_mem() -> int:
    """Return GPU mem used (MiB)."""
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
    prompt_chars: int
    status: str  # ok | error | timeout
    error: str = ""
    load_s: float = 0.0
    ttft_s: float = 0.0
    total_s: float = 0.0
    eval_tokens: int = 0
    prompt_tokens: int = 0
    tok_per_s: float = 0.0
    gpu_mem_before_mib: int = 0
    gpu_mem_peak_mib: int = 0
    output: str = ""
    output_chars: int = 0


def run_generate(model: str, prompt: str, *, timeout: int = TIMEOUT) -> dict:
    """Single Ollama /api/generate call, non-streaming. Returns timing+output."""
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 512,  # cap so slow models don't hang
            "num_ctx": 4096,
        }
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    t1 = time.perf_counter()
    return {
        "total_s": t1 - t0,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "eval_tokens": data.get("eval_count", 0),
        "ttft_s": (data.get("prompt_eval_duration", 0) / 1e9) if data.get("prompt_eval_duration") else 0.0,
        "output": data.get("response", ""),
    }


def bench_one(model: dict, test_id: str, domain: str, prompt: str) -> BenchResult:
    name = model["name"]
    res = run_generate(name, prompt)
    mem_peak = get_gpu_mem()
    if "error" in res:
        return BenchResult(
            model=name, test_id=test_id, domain=domain,
            prompt_chars=len(prompt), status="error", error=res["error"],
            gpu_mem_before_mib=mem_before, gpu_mem_peak_mib=mem_peak,
        )
    total_s = res["total_s"]
    eval_tokens = res["eval_tokens"]
    tps = eval_tokens / total_s if total_s > 0 else 0.0
    output = res["output"]
    return BenchResult(
        model=name, test_id=test_id, domain=domain,
        prompt_chars=len(prompt), status="ok",
        ttft_s=round(res["ttft_s"], 3),
        total_s=round(total_s, 3),
        eval_tokens=eval_tokens, prompt_tokens=res["prompt_tokens"],
        tok_per_s=round(tps, 2),
        gpu_mem_before_mib=mem_before, gpu_mem_peak_mib=mem_peak,
        output=output, output_chars=len(output),
    )


def main():
    models = get_installed_models()
    print(f"[bench] {len(models)} unique models")
    for m in models:
        print(f"  - {m['name']:<60} {m['size_gb']:.2f}GB  param={m['param']}  quant={m['quant']}")

    results: list[BenchResult] = []
    total = len(models) * len(ALL_TESTS)
    done = 0
    for m in models:
        print(f"\n[bench] === {m['name']} ===")
        for test_id, domain, prompt in ALL_TESTS:
            done += 1
            print(f"  [{done}/{total}] {test_id} ({domain}, {len(prompt)} chars) ...", end=" ", flush=True)
            r = bench_one(m, test_id, domain, prompt)
            tag = "OK" if r.status == "ok" else "ERR"
            extra = f"  {r.tok_per_s:.1f} tok/s  {r.total_s:.1f}s  vram={r.gpu_mem_peak_mib}MiB" if r.status == "ok" else f"  {r.error[:60]}"
            print(f"{tag}{extra}")
            results.append(r)
            # Save each result incrementally
            out = OUTPUT_DIR / f"{m['name'].replace('/', '__').replace(':', '_')}.jsonl"
            with out.open("a") as f:
                f.write(json.dumps(asdict(r)) + "\n")
            # Unload model after each test to free VRAM for next
            try:
                urllib.request.urlopen(
                    urllib.request.Request(
                        f"{OLLAMA}/api/generate",
                        data=json.dumps({"model": m["name"], "keep_alive": 0}).encode(),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    ),
                    timeout=10,
                )
            except Exception:
                pass

    # Summary
    print("\n[bench] === SUMMARY ===")
    by_model: dict[str, list[BenchResult]] = {}
    for r in results:
        by_model.setdefault(r.model, []).append(r)
    print(f"{'model':<55} {'ok':>4} {'err':>4} {'avg_tps':>8} {'avg_ttft':>9} {'peak_vram':>10}")
    for mname, rs in by_model.items():
        ok = [r for r in rs if r.status == "ok"]
        err = [r for r in rs if r.status == "error"]
        avg_tps = sum(r.tok_per_s for r in ok) / len(ok) if ok else 0
        avg_ttft = sum(r.ttft_s for r in ok) / len(ok) if ok else 0
        peak_vram = max(r.gpu_mem_peak_mib for r in rs)
        print(f"{mname:<55} {len(ok):>4} {len(err):>4} {avg_tps:>8.2f} {avg_ttft:>9.2f} {peak_vram:>10}")

    # Save full results
    with (OUTPUT_DIR / "all.json").open("w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\n[bench] Full results: {OUTPUT_DIR / 'all.json'}")


if __name__ == "__main__":
    main()