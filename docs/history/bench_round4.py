#!/usr/bin/env python3
"""
Round 4: Rigorous test for top-2-per-task selection.
14 tests × 11 models = 154 runs, ~45 min.
Focus: real-world prompts, longer context, multiple scenarios per domain.
"""
from __future__ import annotations
import json, subprocess, time, urllib.request, urllib.error
from pathlib import Path

OLLAMA = "http://localhost:11434"
TIMEOUT = 300
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_round4")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    "qwen3.5:4b",
    "MobiusDevelopment/gemma4-E2B-it-qat-Q4-unsloth-heretic:latest",
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
    "maxwellb/gemma4-12b-it-dn:latest",
    "batiai/gemma4-12b:iq3",
    "VladimirGav/gemma4-26b-16GB-VRAM-Uncensored:latest",
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest",
    "cyborgxx101/gemma-4-12b-opus-finetuned-mlx:4bit",
    "igorls/gemma-4-12B-it-qat-q4_0-unquantized-heretic:Q4_K_M",
    "gemma4:12b",
]

# 14 tests, 2-3 per domain
TESTS = [
    # IMPROVE (3 scenarios)
    ("improve_simple", "improve",
     "Rewrite as structured agent spec (GOAL, FILES, STEPS, ACCEPTANCE). Input: 'fix the auth bug'"),
    ("improve_es_vague", "improve",
     "Rewrite as structured agent spec. Input: 'oye el test ese falla a veces, no se que onda, mira a ver que pasa'"),
    ("improve_code_focused", "improve",
     "Rewrite as structured agent spec. Input: 'add retry logic to the HTTP client, sometimes the requests timeout'"),

    # COMPACT (3 scenarios)
    ("compact_short", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). User added conftest.py. pytest collected 12 tests but 3 fail on import 'No module named app'. User stayed on uv. Plan: check sys.path, reinstall."),
    ("compact_medium", "compact",
     "Summarize as 5-bullet handoff. Azure Function cold-start 4s. Plan: zip package excluding .venv/__pycache__/local.settings.json, push via az functionapp deploy. Use --build-native-deps."),
    ("compact_long", "compact",
     "Summarize as 5-bullet handoff. Python packaging: pip vs uv vs poetry. uv chosen. PYTHONPATH removed. Cross-platform wheels: manylinux2014. pytest broken: missing conftest.py. Plan: add conftest.py, uv pip install -e '.[dev]', re-run. ruff also failing. Decision: stay on uv."),

    # LONGCTX (3 scenarios at increasing context sizes)
    ("longctx_8k", "longctx",
     "Below is a session transcript (~8K tokens). Produce a comprehensive handoff preserving key decisions.\n\n" +
     ("[Session turn] User investigating flaky payment test. test_payment_flow sometimes times out. Suspect: race condition in async DB pool. Changed pool size 5→10. Test passes 8/10 runs. Next: add tracing. Decided: use loguru. Will commit to branch fix/payment-flake. " * 20)),
    ("longctx_16k", "longctx",
     "Below is a long session transcript (~16K tokens). Produce a comprehensive handoff.\n\n" +
     ("[Session turn] User investigating flaky payment test. test_payment_flow sometimes times out. Suspect: race condition in async DB pool. Changed pool size 5→10. Test passes 8/10 runs. Next: add tracing to identify slow acquire. Decided: use loguru instead of stdlib logging. Will commit test fixes in branch fix/payment-flake. " * 40)),
    ("longctx_24k", "longctx",
     "Below is a very long session transcript (~24K tokens). Produce a comprehensive handoff.\n\n" +
     ("[Session turn] User investigating flaky payment test. test_payment_flow sometimes times out. Suspect: race condition in async DB pool. Changed pool size 5→10. Test passes 8/10 runs. Next: add tracing. Decided: use loguru. Will commit to branch fix/payment-flake. " * 60)),

    # CODE (3 scenarios)
    ("code_validate", "code",
     "Write Python validate_email(s: str) -> bool using stdlib only. Handle None/empty/whitespace. Brief explanation."),
    ("code_async", "code",
     "Write Python async fetch_all(urls: list[str]) -> list[dict] using aiohttp. Semaphore cap 10. Preserve input order. Per-URL exception handling."),
    ("code_algorithm", "code",
     "Write Python chunk_text(text: str, max_tokens: int) -> list[str] splitting on sentence boundaries. No external deps."),

    # REASON (2 scenarios)
    ("reason_basic", "reason",
     "If A > B, B > C, C = D - 2, D = 10: what is A? Show 3 steps. End with ANSWER: <number>"),
    ("reason_probability", "reason",
     "Box has 3 red, 2 blue, 5 green balls. P(red then green without replacement)? Show work. End with ANSWER: <fraction>"),
]


def gpu_mem():
    try: return int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],timeout=5,text=True).strip())
    except: return -1


def run(model, prompt, num_predict=1024, num_ctx=8192):
    body = json.dumps({"model":model,"prompt":prompt,"stream":False,"think":False,
                       "options":{"temperature":0.2,"num_predict":num_predict,"num_ctx":num_ctx}}).encode()
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",data=body,headers={"Content-Type":"application/json"},method="POST"),timeout=TIMEOUT) as r:
            d = json.load(r)
        return {"ok":True,"total_s":time.perf_counter()-t0,
                "ttft_s":(d.get("prompt_eval_duration",0)/1e9) if d.get("prompt_eval_duration") else 0.0,
                "eval_tokens":d.get("eval_count",0),"prompt_tokens":d.get("prompt_eval_count",0),
                "output":d.get("response","") or d.get("thinking",""),
                "done_reason":d.get("done_reason","?")}
    except urllib.error.HTTPError as e:
        return {"ok":False,"error":f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"ok":False,"error":str(e)}


def unload(model):
    try: urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",data=json.dumps({"model":model,"keep_alive":0}).encode(),headers={"Content-Type":"application/json"},method="POST"),timeout=10)
    except: pass


total = len(MODELS) * len(TESTS)
print(f"[round4] {len(MODELS)} models × {len(TESTS)} tests = {total} runs (~45 min)\n")
results = []
done = 0
for m in MODELS:
    print(f"\n=== {m} ===")
    # Warmup
    r = run(m, "hi", num_predict=10, num_ctx=512)
    time.sleep(2)
    for tid, domain, prompt in TESTS:
        done += 1
        print(f"[{done:>3}/{total}] {tid} ...", end=" ", flush=True)
        # Long context tests need bigger num_ctx
        num_ctx = 32768 if tid.startswith("longctx") else 8192
        num_predict = 768 if tid in ("compact_long", "longctx_24k") else 1024
        r = run(m, prompt, num_predict=num_predict, num_ctx=num_ctx)
        if not r["ok"]:
            print(f"ERR {r['error'][:60]}")
            results.append({"model":m,"test_id":tid,"domain":domain,"status":"error","error":r["error"]})
        else:
            tps = r["eval_tokens"]/r["total_s"] if r["total_s"]>0 else 0
            vram = gpu_mem()
            print(f"OK {tps:>5.1f} tok/s  {r['total_s']:>5.1f}s  vram={vram}MiB  done={r['done_reason']}")
            results.append({"model":m,"test_id":tid,"domain":domain,"status":"ok",
                           "tps":round(tps,2),"total_s":round(r["total_s"],3),
                           "ttft_s":round(r["ttft_s"],3),
                           "eval_tokens":r["eval_tokens"],"prompt_tokens":r["prompt_tokens"],
                           "vram":vram,"output":r["output"],
                           "done_reason":r["done_reason"]})
        unload(m)
        time.sleep(1)
        out = OUTPUT_DIR / f"{m.replace('/', '__').replace(':', '_')}.jsonl"
        with out.open("a") as f:
            f.write(json.dumps(results[-1]) + "\n")

(OUTPUT_DIR / "all.json").write_text(json.dumps(results, indent=2))
print(f"\nSaved: {OUTPUT_DIR / 'all.json'}")