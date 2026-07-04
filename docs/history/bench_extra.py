#!/usr/bin/env python3
"""
Extra tests:
1. 64K context model with REAL long context (>16K tokens) — does it shine?
2. Parallel loading — can we run 2 models simultaneously in 16GB VRAM?
"""
from __future__ import annotations
import json, subprocess, time, urllib.request, urllib.error
from pathlib import Path

OLLAMA = "http://localhost:11434"
OUTPUT_DIR = Path("/home/eldi/bench/ollama/results_extra")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gpu_mem() -> int:
    try:
        return int(subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            timeout=5, text=True).strip())
    except Exception:
        return -1


def unload(model: str):
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"{OLLAMA}/api/generate",
            data=json.dumps({"model": model, "keep_alive": 0}).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        ), timeout=10)
    except Exception:
        pass


def run(model: str, prompt: str, num_predict: int = 768, num_ctx: int = 16384, keep_alive: str = "5m") -> dict:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "keep_alive": keep_alive,
        "options": {"temperature": 0.2, "num_predict": num_predict, "num_ctx": num_ctx},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.load(r)
        return {
            "ok": True,
            "total_s": time.perf_counter() - t0,
            "eval_tokens": d.get("eval_count", 0),
            "prompt_tokens": d.get("prompt_eval_count", 0),
            "output": d.get("response", ""),
            "done_reason": d.get("done_reason", "?"),
        }
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


# Build a REAL long context (~16K tokens) by repeating a complex session
LONG_SESSION_BLOCK = """[Session turn {n}] User: {user_msg}
[Assistant response]: {assistant_msg}
[Decision]: {decision}
[Action]: {action}
[Result]: {result}
[Next]: {next_step}
"""
LONG_SESSION_PROMPT = """Below is a long, detailed session transcript (~16K tokens). Produce a comprehensive structured handoff note that preserves ALL key decisions, root causes, code changes, and action items. Be thorough — do not lose details.

""" + "\n".join([
    LONG_SESSION_BLOCK.format(
        n=i,
        user_msg=f"User asked about {['pytest conftest', 'ruff config', 'coverage report', 'pip vs uv', 'hatchling vs setuptools', 'manylinux wheels', 'cffi deps', 'azure function deploy'][i % 8]}",
        assistant_msg=f"Assistant explained the tradeoffs in detail with code examples and ran tests to validate the approach. Showed output and got user feedback.",
        decision=f"Decision {i}: chose option B because it preserves backward compatibility and has better long-term maintainability. User confirmed this was the right call.",
        action=f"Action {i}: edited pyproject.toml to add the new section. Ran `uv pip install -e '.[dev]'` to update. Verified with `pytest tests/ -v`.",
        result=f"Result {i}: tests pass (12/12). Coverage at 94%. ruff clean. pyright strict mode passes.",
        next_step=f"Next {i}: commit changes with descriptive message, push branch, open PR. Will need code review from team before merging to main.",
    )
    for i in range(120)  # ~120 blocks * ~120 tokens/block ≈ 14K tokens
]) + "\n\nNow produce the handoff note. Include:\n- Top 3 key decisions\n- All root causes identified\n- Files modified\n- Outstanding action items\n- Open questions"


print(f"[extra] Test 1: 64K context model with REAL 16K token input")
print(f"Prompt size: ~{len(LONG_SESSION_PROMPT.split())} words\n")

# Test 64K model with 16K+ context
for model, ctx in [
    ("SetneufPT/Gemma4-12B_Q4_64K_16GB-GPU:latest", 32768),  # truly use the 64K
    ("qwen3.5:4b", 32768),  # control: does qwen3.5 handle long context?
    ("maxwellb/gemma4-12b-it-dn:latest", 16384),  # control: what does 12B at 16K give?
]:
    print(f"=== {model} (num_ctx={ctx}) ===")
    r = run(model, LONG_SESSION_PROMPT, num_predict=1024, num_ctx=ctx)
    if not r["ok"]:
        print(f"  ERR {r['error'][:100]}")
    else:
        vram = gpu_mem()
        tps = r["eval_tokens"] / r["total_s"] if r["total_s"] > 0 else 0
        out_chars = len(r["output"])
        # Quality heuristic: count distinct entities preserved
        ents = ["pytest", "ruff", "uv", "hatchling", "pyproject", "coverage", "manylinux", "pyright"]
        preserved = sum(1 for e in ents if e.lower() in r["output"].lower())
        print(f"  OK {tps:>5.1f} tok/s  {r['total_s']:>5.1f}s  vram={vram}MiB  out={out_chars}ch  done={r['done_reason']}")
        print(f"  entities_preserved={preserved}/{len(ents)}")
        # Save first 200 chars of output for review
        with (OUTPUT_DIR / f"longctx_{model.replace('/', '__').replace(':', '_')}.txt").open("w") as f:
            f.write(f"# model={model} ctx={ctx}\n")
            f.write(f"# tps={tps:.1f} total_s={r['total_s']:.1f}s vram={vram}MiB\n")
            f.write(f"# entities_preserved={preserved}/{len(ents)}\n\n")
            f.write(r["output"])
    unload(model)
    time.sleep(2)

# Test 2: Parallel loading
print(f"\n[extra] Test 2: Parallel loading — can 2 small models coexist?\n")

# Scenario A: qwen3.5:4b + Mobius E2B (smallest combo)
print("=== A: qwen3.5:4b + Mobius E2B (both tiny) ===")
# Warm qwen3.5:4b
r1 = run("qwen3.5:4b", "say 'ready 1' and stop", num_predict=20, num_ctx=512, keep_alive="5m")
vram1 = gpu_mem()
print(f"  qwen3.5:4b loaded: vram={vram1}MiB")
time.sleep(2)
# Now Mobius while qwen stays
r2 = run("MobiusDevelopment/gemma4-E2B-it-qat-Q4-unsloth-heretic:latest", "say 'ready 2' and stop", num_predict=20, num_ctx=512, keep_alive="5m")
vram2 = gpu_mem()
print(f"  + Mobius E2B loaded: vram={vram2}MiB (delta={vram2-vram1}MiB)")
print(f"  Both loaded simultaneously? {vram2 < 14000} (under 14GB)")
unload("qwen3.5:4b")
unload("MobiusDevelopment/gemma4-E2B-it-qat-Q4-unsloth-heretic:latest")
time.sleep(5)

# Scenario B: qwen3.5:4b + maxwellb (PRIMARY + quality backup)
print("\n=== B: qwen3.5:4b + maxwellb gemma4-12b-it-dn (PRIMARY + SECONDARY) ===")
r1 = run("qwen3.5:4b", "say 'ready 1' and stop", num_predict=20, num_ctx=512, keep_alive="5m")
vram1 = gpu_mem()
print(f"  qwen3.5:4b loaded: vram={vram1}MiB")
time.sleep(2)
r2 = run("maxwellb/gemma4-12b-it-dn:latest", "say 'ready 2' and stop", num_predict=20, num_ctx=512, keep_alive="5m")
vram2 = gpu_mem()
print(f"  + maxwellb gemma4-12b-it-dn loaded: vram={vram2}MiB (delta={vram2-vram1}MiB)")
print(f"  Both loaded simultaneously? {vram2 < 14000} (under 14GB)")
unload("qwen3.5:4b")
unload("maxwellb/gemma4-12b-it-dn:latest")
time.sleep(5)

# Scenario C: qwen3.5 + iq3 (PRIMARY + FAST)
print("\n=== C: qwen3.5:4b + batiai/gemma4-12b:iq3 (PRIMARY + FAST) ===")
r1 = run("qwen3.5:4b", "say 'ready 1' and stop", num_predict=20, num_ctx=512, keep_alive="5m")
vram1 = gpu_mem()
print(f"  qwen3.5:4b loaded: vram={vram1}MiB")
time.sleep(2)
r2 = run("batiai/gemma4-12b:iq3", "say 'ready 2' and stop", num_predict=20, num_ctx=512, keep_alive="5m")
vram2 = gpu_mem()
print(f"  + batiai:iq3 loaded: vram={vram2}MiB (delta={vram2-vram1}MiB)")
print(f"  Both loaded simultaneously? {vram2 < 14000} (under 14GB)")
unload("qwen3.5:4b")
unload("batiai/gemma4-12b:iq3")
time.sleep(5)

print("\n[extra] DONE")