#!/usr/bin/env python3
"""Deep bench for the 4 new families. Reuses bench_deep.py logic."""
import json, subprocess, time, urllib.request, urllib.error
from pathlib import Path

OLLAMA = "http://localhost:11434"
TIMEOUT = 300
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_round2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NEW_FAMILIES = [
    "scorpion7slayer/gemma-4-12b-it-claude-4.6-4.8-opus:latest",
    "igorls/gemma-4-12B-it-qat-q4_0-unquantized-heretic:Q4_K_M",
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest",
]

# Reuse the same 13 tests as bench_deep.py
TESTS = [
    ("improve_simple", "improve",
     "Rewrite as a structured agent spec (GOAL, FILES, STEPS, ACCEPTANCE). Input: 'fix the auth bug'"),
    ("improve_medium", "improve",
     "Rewrite as a structured agent spec. Input: 'haz que el dashboard cargue mas rapido, tarda 8 segundos y es muy lento para los usuarios'"),
    ("improve_vague_es", "improve",
     "Rewrite as a structured agent spec. Input: 'el test falla a veces, no se porque, mira a ver'"),
    ("improve_vague_en", "improve",
     "Rewrite as a structured agent spec. Input: 'i need a thing that converts csv to json, like the file thing but better'"),
    ("compact_short", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). Session: User added conftest.py at /home/eldi/proj. pytest collected 12 tests but 3 fail on import 'No module named app'. Root cause being investigated. User decided to stay on uv. Plan next: check sys.path, reinstall app in editable mode, re-run pytest."),
    ("compact_medium", "compact",
     "Summarize as 5-bullet handoff. Azure Function cold-start 4s unacceptable. Plan: zip package excluding .venv/__pycache__/local.settings.json, push via az functionapp deploy. Use --build-native-deps."),
    ("compact_long", "compact",
     "Summarize as 5-bullet handoff. Session: discussed Python packaging pip vs uv vs poetry. uv chosen. PYTHONPATH removed. Cross-platform wheels: manylinux2014. pytest broken: missing conftest.py. Plan: add conftest.py, uv pip install -e '.[dev]', re-run. ruff also failing. Decision: stay on uv. Next: write conftest.py."),
    ("code_validate", "code",
     "Write Python validate_email(s: str) -> bool using stdlib only. Handle None/empty/whitespace. Brief explanation."),
    ("code_async", "code",
     "Write Python async fetch_all(urls: list[str]) -> list[dict] using aiohttp. Semaphore cap 10. Preserve input order. Per-URL exception handling."),
    ("code_algorithm", "code",
     "Write Python chunk_text(text: str, max_tokens: int) -> list[str] splitting on sentence boundaries. No external deps."),
    ("longctx_summary", "longctx",
     "Below is a long session transcript. Produce a comprehensive structured handoff.\n\n" + ("[Session content with code changes, debugging steps, decisions, and current state. User investigating flaky test in /home/eldi/proj/tests/. Test test_payment_flow sometimes fails with timeout. Suspect: race condition in async DB connection pool. User changed pool size from 5 to 10 yesterday. Test passed 8/10 runs today. Still flaky. Next: add tracing to identify which pool acquire is slow. Decided to use loguru instead of stdlib logging. Will commit test fixes in branch fix/payment-flake. ]\n" * 30)),
    ("reason_basic", "reason",
     "If A > B, B > C, C = D - 2, D = 10: what is A? Show 3 steps. End with ANSWER: <number>"),
    ("reason_probability", "reason",
     "Box has 3 red, 2 blue, 5 green balls. P(red then green without replacement)? Show work. End with ANSWER: <fraction>"),
]


def gpu_mem():
    try: return int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],timeout=5,text=True).strip())
    except: return -1


def run(model, prompt, num_predict=1024, num_ctx=4096):
    body = json.dumps({"model":model,"prompt":prompt,"stream":False,"think":False,
                       "options":{"temperature":0.2,"num_predict":num_predict,"num_ctx":num_ctx}}).encode()
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",data=body,headers={"Content-Type":"application/json"},method="POST"),timeout=TIMEOUT) as r:
            d = json.load(r)
        return {"ok":True,"total_s":time.perf_counter()-t0,
                "eval_tokens":d.get("eval_count",0),
                "output":d.get("response","") or d.get("thinking",""),
                "done_reason":d.get("done_reason","?")}
    except urllib.error.HTTPError as e:
        return {"ok":False,"error":f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"ok":False,"error":str(e)}


def unload(model):
    try: urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",data=json.dumps({"model":model,"keep_alive":0}).encode(),headers={"Content-Type":"application/json"},method="POST"),timeout=10)
    except: pass


total = len(NEW_FAMILIES) * len(TESTS)
print(f"[round2] {len(NEW_FAMILIES)} new families × {len(TESTS)} tests = {total} runs\n")

results = []
done = 0
for m in NEW_FAMILIES:
    print(f"\n=== {m} ===")
    # Warmup
    run(m, "hi", num_predict=10)
    time.sleep(2)
    for tid, domain, prompt in TESTS:
        done += 1
        print(f"[{done:>3}/{total}] {tid} ...", end=" ", flush=True)
        num_ctx = 8192 if tid == "longctx_summary" else 4096
        num_predict = 768 if tid == "compact_long" else 1024
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
                           "eval_tokens":r["eval_tokens"],"vram":vram,
                           "output":r["output"],"done_reason":r["done_reason"]})
        unload(m)
        time.sleep(1)
        out = OUTPUT_DIR / f"{m.replace('/', '__').replace(':', '_')}.jsonl"
        with out.open("a") as f:
            f.write(json.dumps(results[-1]) + "\n")

# Save combined
(OUTPUT_DIR / "all.json").write_text(json.dumps(results, indent=2))
print(f"\nSaved: {OUTPUT_DIR / 'all.json'}")