#!/usr/bin/env python3
"""Quick smoke test for all 28 new qwen3.5 variants."""
from __future__ import annotations
import json, subprocess, time, urllib.request, urllib.error
from pathlib import Path

OLLAMA = "http://localhost:11434"
TIMEOUT = 180
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_qwen35_quick")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# All 28 new qwen3.5 variants
MODELS = [
    # 9b variants
    "qwen3.5:9b",  # official baseline
    "qwen3.5:9b-q8_0",
    "aravhawk/qwen3.5-opus-4.6:9b",
    "sorc/qwen3.5-claude-4.6-opus:9b",
    "sorc/qwen3.5-claude-4.6-opus-q4:9b",
    "fredrezones55/Qwopus3.5:9b",
    "carstenuhlig/omnicoder-9b:q8_0",
    "carstenuhlig/omnicoder-9b:Q4_K_M",
    "pdurugyan/qwen3.5-9b-deepseek-v4-flash-Q4_K_M-v_2:latest",
    "ZimaBlueAI/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:latest",
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:9b",
    "kiwi_kiwi/qwen3.5-9b-code:q4k",
    "oamazonasgabriel/qwen3.5-9b:q4-16gbGPU",
    "huihui_ai/qwen3.5-abliterated:9b",
    "jaahas/qwen3.5-uncensored:9b",
    "vaultbox/qwen3.5-uncensored:9b",
    "richardyoung/qwythos-9b-abliterated:Q8_0",
    "richardyoung/qwythos-9b-abliterated:Q4_K_M",
    "richardyoung/qwythos-9b-abliterated:IQ4_XS",
    "aratan/qwen3.5-9b-abliterated-flash:latest",
    "rafw007/qwen35-claude-coder:9b",

    # 4b variants
    "qwen3.5:4b-bf16",
    "fredrezones55/Qwopus3.5:4b",
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b",
    "huihui_ai/qwen3.5-abliterated:4b",
    "jaahas/qwen3.5-uncensored:4b",
    "vaultbox/qwen3.5-uncensored:4b",
    "sorc/qwen3.5-claude-4.6-opus-q4:4b",
]

# 4 quick tests (one per main domain)
TESTS = [
    ("improve", "improve",
     "Rewrite as structured agent spec (GOAL, FILES, STEPS, ACCEPTANCE). Input: 'fix the auth bug'"),
    ("compact", "compact",
     "Summarize as 5-bullet handoff (task/decisions/current/blockers/next). User added conftest.py. pytest collected 12 tests but 3 fail on import 'No module named app'. User stayed on uv. Plan: check sys.path."),
    ("code", "code",
     "Write Python validate_email(s: str) using stdlib only. Handle None/empty. Brief explanation."),
    ("reason", "reason",
     "If A > B, B > C, C = D - 2, D = 10: what is A? End with ANSWER: <number>"),
]


def gpu_mem():
    try: return int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],timeout=5,text=True).strip())
    except: return -1


def run(model, prompt, num_predict=512, num_ctx=4096):
    body = json.dumps({"model":model,"prompt":prompt,"stream":False,"think":False,
                       "options":{"temperature":0.2,"num_predict":num_predict,"num_ctx":num_ctx}}).encode()
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",data=body,headers={"Content-Type":"application/json"},method="POST"),timeout=TIMEOUT) as r:
            d = json.load(r)
        return {"ok":True,"total_s":time.perf_counter()-t0,"eval_tokens":d.get("eval_count",0),
                "output":d.get("response","") or d.get("thinking",""),"done_reason":d.get("done_reason","?")}
    except urllib.error.HTTPError as e:
        return {"ok":False,"error":f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"ok":False,"error":str(e)}


def unload(model):
    try: urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",data=json.dumps({"model":model,"keep_alive":0}).encode(),headers={"Content-Type":"application/json"},method="POST"),timeout=10)
    except: pass


total = len(MODELS) * len(TESTS)
print(f"[qwen35_quick] {len(MODELS)} new models × {len(TESTS)} tests = {total} runs\n")
results = []
done = 0
for m in MODELS:
    print(f"\n=== {m} ===")
    for tid, domain, prompt in TESTS:
        done += 1
        print(f"[{done:>3}/{total}] {tid} ...", end=" ", flush=True)
        r = run(m, prompt)
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

(OUTPUT_DIR / "all.json").write_text(json.dumps(results, indent=2))
print(f"\nSaved: {OUTPUT_DIR / 'all.json'}")