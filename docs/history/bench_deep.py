#!/usr/bin/env python3
"""
Deep benchmark for the survivors. Multiple prompts per domain, longer outputs,
per-domain winner ranking.
"""
from __future__ import annotations
import json, subprocess, time, urllib.request, urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path

OLLAMA = "http://localhost:11434"
TIMEOUT = 300
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_deep")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 7 survivors + 1 baseline
MODELS = [
    "qwen3.5:4b",
    "maxwellb/gemma4-12b-it-dn:latest",
    "batiai/gemma4-12b:q4",
    "batiai/gemma4-12b:iq3",
    "SetneufPT/Gemma4-12B_Q4_64K_16GB-GPU:latest",
    "MobiusDevelopment/gemma4-E2B-it-qat-Q4-unsloth-heretic:latest",
    "gemma4:12b",  # official baseline
]

# Test prompts per domain
TESTS = [
    # IMPROVE: 4 vague prompts at varying complexity
    ("improve_simple", "improve",
     "Rewrite as a structured agent spec (GOAL, FILES, STEPS, ACCEPTANCE). Input: 'fix the auth bug'"),
    ("improve_medium", "improve",
     "Rewrite as a structured agent spec. Input: 'haz que el dashboard cargue mas rapido, tarda 8 segundos y es muy lento para los usuarios'"),
    ("improve_vague_es", "improve",
     "Rewrite as a structured agent spec. Input: 'el test falla a veces, no se porque, mira a ver'"),
    ("improve_vague_en", "improve",
     "Rewrite as a structured agent spec. Input: 'i need a thing that converts csv to json, like the file thing but better'"),

    # COMPACT: 3 prompts with varying context lengths (short/medium/long)
    ("compact_short", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). Session: User added conftest.py at /home/eldi/proj. pytest collected 12 tests but 3 fail on import 'No module named app'. Root cause being investigated. User decided to stay on uv. Plan next: check sys.path, reinstall app in editable mode, re-run pytest."),
    ("compact_medium", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). Session transcript: User reported Azure Function cold-start of 4s is unacceptable. Assistant suggested premium EP1 plan + always-on. Tested locally with func start: 1.2s no-warmup. User wants deploy. Plan: zip package excluding .venv/__pycache__/local.settings.json, push via az functionapp deploy. Concern: storage conn string must not be in zip. Decision: use --build-native-deps for cryptography wheels. Next: build pkg.zip then deploy. Blockers: none."),
    ("compact_long", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). Session transcript:\n" + "\n".join(
         [f"[Turn {i}] Discussion point about Python packaging: pip vs uv vs poetry. User had pip-workflow with PYTHONPATH=/usr/lib/python3 path manipulation. Issue: site-packages conflict with .venv/lib. Resolution: dropped PYTHONPATH override. Tested uv: 3x faster installs. User asked about cross-platform wheels: manylinux2014 vs musllinux. Decision: pin --python 3.12 --platform manylinux2014. Tested cross-platform install: works. Then pytest broken: 3 of 12 tests fail with ImportError. Root cause: tests dir missing __init__.py or conftest.py not at root. Plan: add conftest.py at root, reinstall dev deps in .venv. ruff also failing: No module named 'ruff' - same .venv path issue. Decision: stay on uv, drop pip completely. Will edit pyproject.toml to add [tool.ruff] section. Blockers: none. Next: write conftest.py, run uv pip install -e '.[dev]', re-run pytest + ruff. Note: also need to update .gitignore to exclude .venv. Earlier in session: discussed difference between hatchling vs setuptools as build backend. Chose hatchling (modern, faster). User mentioned they prefer flit but hatchling is more standard in 2026." for i in range(3)]) + "\nEnd of transcript."),

    # CODE: 3 tasks (validation, async, algorithm)
    ("code_validate", "code",
     "Write Python validate_email(s: str) -> bool using stdlib only. Handle None/empty/whitespace. Brief explanation."),
    ("code_async", "code",
     "Write Python async fetch_all(urls: list[str]) -> list[dict] using aiohttp. Semaphore cap 10. Preserve input order. Per-URL exception handling."),
    ("code_algorithm", "code",
     "Write Python chunk_text(text: str, max_tokens: int) -> list[str] splitting on sentence boundaries. No external deps."),

    # LONGCTX: 4K token session summary (tests 64K context advantage)
    ("longctx_summary", "longctx",
     "Below is a long session transcript. Produce a comprehensive structured handoff note that preserves all key decisions, root causes, and action items. Aim for completeness over brevity.\n\n" + ("[Session content with code changes, debugging steps, decisions, and current state. The user is investigating a flaky test in /home/eldi/proj/tests/. Test test_payment_flow sometimes fails with timeout. Suspect: race condition in async DB connection pool. User changed pool size from 5 to 10 yesterday. Test passed 8/10 runs today. Still flaky. Next: add tracing to identify which pool acquire is slow. Decided to use loguru instead of stdlib logging for structured output. Will commit test fixes in branch fix/payment-flake. ]\n" * 30)),

    # REASON: 2 prompts
    ("reason_basic", "reason",
     "If A > B, B > C, C = D - 2, D = 10: what is A? Show 3 steps. End with ANSWER: <number>"),
    ("reason_probability", "reason",
     "Box has 3 red, 2 blue, 5 green balls. P(red then green without replacement)? Show work. End with ANSWER: <fraction>"),
]


def gpu_mem() -> int:
    try:
        return int(subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            timeout=5, text=True).strip())
    except Exception:
        return -1


def run(model: str, prompt: str, num_predict: int = 1024, num_ctx: int = 4096) -> dict:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_predict": num_predict, "num_ctx": num_ctx},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            d = json.load(r)
        return {
            "ok": True,
            "total_s": time.perf_counter() - t0,
            "eval_tokens": d.get("eval_count", 0),
            "prompt_tokens": d.get("prompt_eval_count", 0),
            "ttft_s": (d.get("prompt_eval_duration", 0) / 1e9) if d.get("prompt_eval_duration") else 0.0,
            "output": d.get("response", "") or d.get("thinking", ""),
            "done_reason": d.get("done_reason", "?"),
        }
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
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
    total = len(MODELS) * len(TESTS)
    print(f"[deep] {len(MODELS)} models × {len(TESTS)} tests = {total} runs\n")

    results = []
    done = 0
    for m in MODELS:
        print(f"\n=== {m} ===")
        for tid, domain, prompt in TESTS:
            done += 1
            print(f"[{done:>3}/{total}] {tid} ({domain}) ...", end=" ", flush=True)
            # Use larger context for longctx test
            num_ctx = 8192 if tid == "longctx_summary" else 4096
            num_predict = 1024 if tid != "compact_long" else 768
            r = run(m, prompt, num_predict=num_predict, num_ctx=num_ctx)
            if not r["ok"]:
                print(f"ERR {r['error'][:60]}")
                results.append({"model": m, "test_id": tid, "domain": domain, "status": "error", "error": r["error"]})
            else:
                tps = r["eval_tokens"] / r["total_s"] if r["total_s"] > 0 else 0
                vram = gpu_mem()
                out_chars = len(r["output"])
                print(f"OK {tps:>5.1f} tok/s {r['total_s']:>5.1f}s vram={vram}MiB out={out_chars}ch done={r['done_reason']}")
                results.append({
                    "model": m, "test_id": tid, "domain": domain, "status": "ok",
                    "tps": round(tps, 2), "total_s": round(r["total_s"], 3),
                    "ttft_s": round(r["ttft_s"], 3),
                    "eval_tokens": r["eval_tokens"], "prompt_tokens": r["prompt_tokens"],
                    "vram": vram, "output": r["output"],
                    "out_chars": out_chars, "done_reason": r["done_reason"],
                })
            unload(m)
            out = OUTPUT_DIR / f"{m.replace('/', '__').replace(':', '_')}.jsonl"
            with out.open("a") as f:
                f.write(json.dumps(results[-1]) + "\n")

    # Summary
    print(f"\n{'='*90}\nSUMMARY\n{'='*90}")
    by_model: dict[str, list[dict]] = {}
    for r in results:
        by_model.setdefault(r["model"], []).append(r)
    print(f"{'model':<58} {'ok':>3} {'err':>4} {'avg_tps':>8} {'avg_ttft':>8} {'peak_vram':>10}")
    for m, rs in sorted(by_model.items()):
        ok = [r for r in rs if r["status"] == "ok"]
        err = [r for r in rs if r["status"] == "error"]
        if ok:
            avg_tps = sum(r["tps"] for r in ok) / len(ok)
            avg_ttft = sum(r["ttft_s"] for r in ok) / len(ok)
            peak = max(r["vram"] for r in rs)
        else:
            avg_tps = avg_ttft = 0
            peak = 0
        print(f"{m[:57]:<58} {len(ok):>3} {len(err):>4} {avg_tps:>8.2f} {avg_ttft:>8.2f} {peak:>10}")

    # Per-domain ranking
    print(f"\n{'='*90}\nPER-DOMAIN (avg tok/s, lower time = better)\n{'='*90}")
    domains = sorted({r["domain"] for r in results if r["status"] == "ok"})
    for d in domains:
        dom_rs = [r for r in results if r["status"] == "ok" and r["domain"] == d]
        by_m = {}
        for r in dom_rs:
            by_m.setdefault(r["model"], []).append(r)
        ranked = sorted(by_m.items(),
                        key=lambda kv: sum(r["tps"] for r in kv[1]) / len(kv[1]),
                        reverse=True)
        print(f"\n[{d.upper()}]")
        for m, rs in ranked:
            tps = sum(r["tps"] for r in rs) / len(rs)
            tt = sum(r["total_s"] for r in rs) / len(rs)
            print(f"  {m[:55]:<55} avg {tps:5.1f} tok/s  avg {tt:5.1f}s  ({len(rs)} tests)")

    (OUTPUT_DIR / "all.json").write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {OUTPUT_DIR / 'all.json'}")


if __name__ == "__main__":
    main()