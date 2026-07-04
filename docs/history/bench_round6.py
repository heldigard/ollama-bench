#!/usr/bin/env python3
"""Round 6: Validate top 5 new qwen3.5 variants vs current 9 keepers.
14 models × 16 tests = 224 runs, ~60 min."""
from __future__ import annotations
import json, subprocess, time, urllib.request, urllib.error
from pathlib import Path

OLLAMA = "http://localhost:11434"
TIMEOUT = 300
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_round6")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    # NEW qwen3.5 winners from quick test (top 5)
    "vaultbox/qwen3.5-uncensored:4b",
    "ZimaBlueAI/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:latest",
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b",
    "carstenuhlig/omnicoder-9b:Q4_K_M",
    "fredrezones55/Qwopus3.5:4b",
    # Current keepers (top 9)
    "qwen3.5:4b",
    "MobiusDevelopment/gemma4-E2B-it-qat-Q4-unsloth-heretic:latest",
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
    "maxwellb/gemma4-12b-it-dn:latest",
    "batiai/gemma4-12b:q4",
    "SetneufPT/Gemma4-12B_Q4_64K_16GB-GPU:latest",
    "VladimirGav/gemma4-26b-16GB-VRAM-Uncensored:latest",  # note: should be deleted but still here
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest",
    "gemma4:12b",
]

# 16 tests (same as round 5)
TESTS = [
    ("improve_simple", "improve",
     "Rewrite as structured agent spec (GOAL, FILES, STEPS, ACCEPTANCE). Input: 'fix the auth bug'"),
    ("improve_es_vague", "improve",
     "Rewrite as structured agent spec. Input: 'oye el test ese falla a veces, no se que onda, mira a ver que pasa'"),
    ("improve_code_focused", "improve",
     "Rewrite as structured agent spec. Input: 'add retry logic to the HTTP client, sometimes the requests timeout'"),
    ("compact_short", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). User added conftest.py. pytest collected 12 tests but 3 fail on import 'No module named app'. User stayed on uv. Plan: check sys.path, reinstall."),
    ("compact_medium", "compact",
     "Summarize as 5-bullet handoff. Azure Function cold-start 4s. Plan: zip package excluding .venv/__pycache__/local.settings.json, push via az functionapp deploy. Use --build-native-deps."),
    ("compact_long", "compact",
     "Summarize as 5-bullet handoff. Python packaging: pip vs uv vs poetry. uv chosen. PYTHONPATH removed. Cross-platform wheels: manylinux2014. pytest broken: missing conftest.py. Plan: add conftest.py, uv pip install -e '.[dev]', re-run. ruff also failing. Decision: stay on uv."),
    ("compact_es", "compact",
     "Resume en 5 viñetas handoff (tarea/decisiones/actual/bloqueos/siguiente). Usuario editando pyproject.toml. Test 'test_payments' falla timeout. Sospechoso: pool conexiones async DB. Aumentó pool de 5 a 10. Plan: añadir tracing con loguru."),
    ("compact_debug", "compact",
     "Summarize as 5-bullet handoff. User debugged Flask app. Error: circular import between models.py and routes.py. Moved imports to bottom of models.py. Test now passes 12/12. Decision: keep this pattern for all future models. Blockers: none. Next: commit fix and run full pytest suite."),
    ("longctx_8k", "longctx",
     "Below is a session transcript (~8K tokens). Produce a comprehensive handoff preserving key decisions.\n\n" +
     ("[Session turn] User investigating flaky payment test. test_payment_flow sometimes times out. Suspect: race condition in async DB pool. Changed pool size 5→10. Test passes 8/10 runs. Next: add tracing. Decided: use loguru. Will commit to branch fix/payment-flake. " * 20)),
    ("longctx_16k", "longctx",
     "Below is a long session transcript (~16K tokens). Produce a comprehensive handoff.\n\n" +
     ("[Session turn] User investigating flaky payment test. test_payment_flow sometimes times out. Suspect: race condition in async DB pool. Changed pool size 5→10. Test passes 8/10 runs. Next: add tracing to identify slow acquire. Decided: use loguru instead of stdlib logging. Will commit test fixes in branch fix/payment-flake. " * 40)),
    ("longctx_24k", "longctx",
     "Below is a very long session transcript (~24K tokens). Produce a comprehensive handoff.\n\n" +
     ("[Session turn] User investigating flaky payment test. test_payment_flow sometimes times out. Suspect: race condition in async DB pool. Changed pool size 5→10. Test passes 8/10 runs. Next: add tracing. Decided: use loguru. Will commit to branch fix/payment-flake. " * 60)),
    ("code_validate", "code",
     "Write Python validate_email(s: str) -> bool using stdlib only. Handle None/empty/whitespace. Brief explanation."),
    ("code_async", "code",
     "Write Python async fetch_all(urls: list[str]) -> list[dict] using aiohttp. Semaphore cap 10. Preserve input order. Per-URL exception handling."),
    ("code_algorithm", "code",
     "Write Python chunk_text(text: str, max_tokens: int) -> list[str] splitting on sentence boundaries. No external deps."),
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
print(f"[round6] {len(MODELS)} models × {len(TESTS)} tests = {total} runs\n")
results = []
done = 0
for m in MODELS:
    print(f"\n=== {m} ===")
    r = run(m, "hi", num_predict=10, num_ctx=512)
    time.sleep(2)
    for tid, domain, prompt in TESTS:
        done += 1
        print(f"[{done:>3}/{total}] {tid} ...", end=" ", flush=True)
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