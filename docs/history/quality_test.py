#!/usr/bin/env python3
"""
QUALITY TEST - Real prompt evaluation.
7 final-lineup models × 5 realistic prompts.
Outputs saved for Claude (me) to grade.
"""
from __future__ import annotations
import json, time, urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434"
OUTPUT = Path("/home/eldi/bench/ollama/quality_test")
OUTPUT.mkdir(parents=True, exist_ok=True)

MODELS = [
    "qwen3.5:4b",
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b",
    "fredrezones55/Qwopus3.5:4b",
    "carstenuhlig/omnicoder-9b:Q4_K_M",
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest",
    "gemma3:4b" if False else "MobiusDevelopment/gemma4-E2B-it-qat-Q4-unsloth-heretic:latest",  # E2B-heretic (TINY)
]

# 5 realistic prompts - one per task
PROMPTS = [
    ("IMPROVE", "improve",
     "I have this bug where the auth middleware crashes randomly. Stack trace points to jwt.js line 47 sometimes. Need to fix it. Tests pass locally but fail in CI 1/5 times. Can you help me fix the auth bug?"),
    ("COMPACT", "compact",
     """Compress this debug session into a 5-bullet handoff.

[User] My pytest is failing with ModuleNotFoundError for `app.auth.routes` after I added a new tests/ directory.
[Assistant] Check if there's __init__.py in tests/. Also verify pytest config (pytest.ini or pyproject.toml).
[User] I added __init__.py. Still fails. pytest finds the file but errors on import.
[Assistant] Likely PYTHONPATH issue. Try `pytest --rootdir=.` or set pythonpath in pyproject.toml.
[User] Tried `pythonpath = ["src"]` in pyproject.toml. Now works.
[Assistant] Good. Next, run full suite to confirm no other paths broken.
[Result] 47 tests pass. 1 fails on test_payment_flow due to DB timeout (different issue).
[Decision] Keep pythonpath = ["src"]. Defer payment timeout to next session.
[Next] 1) Add conftest.py to ensure DB fixture setup. 2) Investigate payment flow timeout."""),
    ("CODE", "code",
     "Write a Python async function `retry_with_backoff(fn, max_attempts=3, base_delay=0.5)` that retries `fn` on transient exceptions (ConnectionError, TimeoutError). Use exponential backoff with jitter. Return the result on success, raise the last exception on max attempts. Include type hints and a brief docstring."),
    ("LONGCTX", "longctx",
     """Produce a comprehensive structured handoff from this session. Preserve all key decisions and code changes.

[Session] User debugging intermittent 500 errors in production API.
[Assistant] Started by checking logs. Found: 50% of errors happen during deploy window (10:00-10:15 UTC daily).
[Decision] Hypothesis: connection pool exhaustion during rolling restart.
[Action] Checked connection pool config: max_connections=20, current usage spikes to 28 during deploy.
[Assistant] Recommended increasing pool size AND implementing graceful drain during deploys.
[Decision] User agreed. Implemented 2 changes: (1) max_connections=50, (2) SIGTERM handler that closes existing connections gracefully.
[Action] Deployed to staging. Tested with simulated deploy. Errors went from 50% to 2% (residual = pod-level connection races).
[Next] (1) Add metrics for connection pool saturation. (2) Consider switching to a connection-pool-aware load balancer. (3) Investigate the 2% residual errors.
[Blocked] Production deploy scheduled for tomorrow - need on-call approval.
[Files] src/api/pool.py, src/api/server.py, deploy/k8s/rolling-restart.yaml"""),
    ("REASON", "reason",
     """Solve this step by step.

A team has 3 sprints left in a quarter. Sprint capacity is 40 story points per sprint. Current backlog has 200 story points. Velocity last 3 sprints: 35, 42, 38 (avg 38.3).

Question: At current velocity, can the team finish the backlog? If not, what's the minimum additional velocity needed? Show your work."""),
]


def call(model, prompt, num_predict=1024, num_ctx=8192, num_predict_override=None):
    np = num_predict_override or num_predict
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_predict": np, "num_ctx": num_ctx}
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    s = time.perf_counter() - t0
    return {
        "out": d.get("response", ""),
        "tok_s": d.get("eval_count", 0) / s if s > 0 else 0,
        "total_s": round(s, 2),
        "eval_tokens": d.get("eval_count", 0),
        "done_reason": d.get("done_reason", "?"),
    }


def unload(model):
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"{OLLAMA}/api/generate",
            data=json.dumps({"model": model, "keep_alive": 0}).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        ), timeout=10)
    except Exception:
        pass


# Run
total = len(MODELS) * len(PROMPTS)
print(f"[quality] {len(MODELS)} models × {len(PROMPTS)} prompts = {total} runs\n")

results = []
done = 0
for m in MODELS:
    print(f"\n=== {m} ===")
    call(m, "hi", num_predict=10)  # warmup
    time.sleep(1)
    for label, domain, prompt in PROMPTS:
        done += 1
        print(f"  [{done}/{total}] {label} ...", end=" ", flush=True)
        # Adjust num_predict for long tasks
        np = 2048 if domain == "longctx" else 1024
        r = call(m, prompt, num_predict=np)
        if not r["out"]:
            print(f"EMPTY! done_reason={r['done_reason']}")
        else:
            print(f"OK {r['tok_s']:.1f} tok/s {r['total_s']:.1f}s {len(r['out'])}ch")
        results.append({
            "model": m, "label": label, "domain": domain,
            "prompt_chars": len(prompt),
            "tok_s": round(r["tok_s"], 1),
            "total_s": r["total_s"],
            "out_chars": len(r["out"]),
            "done_reason": r["done_reason"],
            "output": r["out"],
        })
        unload(m)
        time.sleep(1)
        out = OUTPUT / f"{m.replace('/', '__').replace(':', '_')}.json"
        with out.open("w") as f:
            json.dump([x for x in results if x["model"] == m], f, indent=2)

(OUTPUT / "all.json").write_text(json.dumps(results, indent=2))
print(f"\nSaved: {OUTPUT}/all.json")