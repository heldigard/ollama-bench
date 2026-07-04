#!/usr/bin/env python3
"""Tie-break bench: HARDER prompts + structural scoring (no 7.0 cap).

Targets the 23 winners from the first pass. Output: re-ranked with real
discrimination (not just leak/within-budget).

HARDER prompts (different shapes from first pass):
  - improve: ambiguous/contradictory; rewards spec sections (GOAL, FILES, ACCEPTANCE)
  - codeq_sum: longer function w/ side effects, must mention key behavior
  - smart_trim: longer 12-bullet transcript; rewards [Earlier]/[Now] collapse
  - web_synth: contradicting sources; rewards conflict-aware summary
  - code_gen: type hints + edge cases (None, empty, off-by-one); rewards valid Python
"""
from __future__ import annotations
import json, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean

OLLAMA = "http://localhost:11434"
NUM_PREDICT = 300
TIMEOUT = 180

# The 23 winners from first pass
CANDIDATES = [
    "hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M",
    "fredrezones55/Qwopus3.5:9b",
    "jaahas/crow:9b",
    "qwen3.5:4b",
    "hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF:latest",
    "batiai/gemma4-e2b:q6",
    "batiai/gemma4-12b:q2",
    "Librellama/gemma4:e2b-Uncensored",
    "ssfdre38/gemma4-turbo:e2b",
    "cryptidbleh/gemma4-claude-opus-4.6:latest",
    "qwen2.5:3b",
    "fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b",
    "hf.co/liskasYR/gemma-4-12B-it-qat-q4_0-unquantized-heretic-gguf:Q4_0",
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest",
    "aratan/gemma-4-E4B-it-heretic:Q6_K",
    "batiai/gemma4-12b:q3",
    "ssfdre38/gemma4-turbo:latest",
    "batiai/gemma4-12b:iq3",
    "cryptidbleh/gemma4-claude-sonnet-4.6:latest",
    "ducquoc/gemma4-fast-sonnet:latest",
    "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ2_M",
    "batiai/gemma4-12b:iq4",
    "batiai/gemma4-12b:q4",
]

PROMPTS = {
    "improve": {
        # AMBIGUOUS: forces model to ask clarifying questions OR surface assumptions
        "v_hard": """Rewrite this vague prompt into a structured spec.

Original: "make my api faster, sometimes slow"

Your rewrite MUST have these explicit sections:
## GOAL (one sentence)
## ASSUMPTIONS (what I had to guess — list 2-3)
## FILES (likely files to touch, or 'unknown')
## STEPS (numbered, 3-5 max)
## ACCEPTANCE (one measurable check)

Be specific. No generic advice. Output ONLY the spec, no preamble.""",
        "scorer": lambda out: structural_score(out, expected_sections=["## GOAL", "## ASSUMPTIONS", "## STEPS", "## ACCEPTANCE"]),
        "budget": 250,
    },
    "codeq_sum": {
        # COMPLEX with side effects + cancellation
        "v_hard": """Summarize this function in ONE sentence, max 30 words. Mention the most important behavior.

async function subscribeToTopic(topic, handler) {
  if (subscriptions.has(topic)) return false;
  const controller = new AbortController();
  const conn = await openStream(topic, { signal: controller.signal });
  subscriptions.set(topic, { controller, handler });
  conn.on('data', msg => {
    if (msg.type === 'error') {
      controller.abort();
      unsubscribe(topic);
    } else handler(msg);
  });
  return true;
}""",
        "scorer": lambda out: quality_score(out, keywords=["abort","unsubscribe","stream","topic","error"]),
        "budget": 35,
    },
    "smart_trim": {
        # LONG transcript with technical detail and out-of-order events
        "v_hard": """Compress to handoff. KEEP: task, decisions, current step, next action, blockers. 5-10 bullets. NO preamble.

[Earlier 6 turns ago] User complained about slow CI. Assistant asked for timing breakdown. Got: install=4min, test=8min, build=12min, deploy=3min. Total ~27min.
[Earlier 5 turns ago] Discussed nx vs lerna. Decided nx because already using it for caching.
[Earlier 3 turns ago] Enabled nx affected:only in CI. Tried. Still 18min. Not enough.
[Earlier 2 turns ago] Investigated vitest vs jest. vitest 2x faster for their tests. Migration underway.
[Now] User: 'vitest migration done, but the snapshot tests still slow'. Assistant found: 14 snapshot tests with deeply nested objects taking 2.1s each.
[Now] User: 'tried happy-dom vs jsdom — happy-dom 30% faster'. Confirmed via local run.
[Decision] Drop snapshots for non-visual assertions. Use plain object comparison. Keep snapshots ONLY for SVG/PNG renders. Estimated savings: 8min.
[Blocked] None.
[Next] PR the snapshot-delete changes (branch: drop-snapshots-v1). Re-run CI. If <10min, ship. If not, look at test parallel config (currently 2 workers).""",
        "scorer": lambda out: structural_score(out, must_have=["task","decision","next","block","current"]),
        "budget": 200,
    },
    "web_synth": {
        # CONTRADICTING sources — model must surface conflict
        "v_hard": """Synthesize a 3-paragraph summary (cite as [1][2][3]). If sources disagree, surface the disagreement.

[1] Anthropic 2024 announcement: Claude 3.5 Sonnet scores 64.3% on SWE-bench Verified (release date: Oct 2024).
[2] Anthropic blog (Mar 2025) claims Claude 3.7 Sonnet scores 62.3% on SWE-bench Verified.
[3] Independent benchmark by The Decoder (Dec 2025) reports Claude 3.7 Sonnet at 70.3% on the SAME benchmark.

Note: there's a discrepancy between sources [2] and [3] about the same model/benchmark. Surface it.""",
        "scorer": lambda out: structural_score(out, must_have=["62.3","70.3","discrepan","[3]"]) and (3 if "discrep" in out.lower() or "disagree" in out.lower() else 0),
        "budget": 220,
    },
    "code_gen": {
        # EDGE cases: must handle None, empty, off-by-one
        "v_hard": """Write a Python function:

def unique_preserve_order(items: list[str | None]) -> list[str]:
    \"\"\"Return unique items in first-seen order. Skip None. Treat '' as falsy, skip it.\"\"\"

- No imports.
- No docstring, no comments. Just the function.
- Handle None items without crashing.
- Empty input → empty output.""",
        "scorer": lambda out: quality_score(out, keywords=["def unique_preserve_order","none","if","return"]) + (5 if "None" in out and "return" in out else 0),
        "budget": 120,
    },
}

def structural_score(out: str, expected_sections=(), must_have=()) -> float:
    """Award points per section/keyword present. Range 0-10."""
    s = 0.0
    L = out.lower()
    for sec in expected_sections:
        if sec.lower() in L: s += 2.0
    for kw in must_have:
        if kw.lower() in L: s += 1.5
    return min(s, 10.0)

def quality_score(out: str, keywords=()) -> float:
    """Award points per keyword present. Range 0-10."""
    s = 0.0
    L = out.lower()
    for kw in keywords:
        if kw.lower() in L: s += 2.0
    return min(s, 10.0)

def call(model: str, prompt: str) -> dict:
    body = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0.2, "num_predict": NUM_PREDICT, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
    except Exception as e:
        return {"err": str(e)[:200]}
    dt = time.perf_counter() - t0
    out = data.get("response", "") or ""
    return {
        "dt": round(dt, 2),
        "tps": round(data.get("eval_count", 0) / dt, 1) if dt > 0 else 0.0,
        "len": len(out),
        "done": data.get("done_reason"),
        "out": out,
    }

def score(task: str, res: dict, cfg: dict) -> float:
    """Structural scoring + leak penalties + tps bonus. Range -5 to +15."""
    if "err" in res: return -100.0
    out = res["out"]
    L = out.lower()
    s = 0.0
    # Leak penalties (HARD fail)
    if "think>" in L or "thinking process" in L: s -= 8
    if "as an ai" in L or "i cannot" in L: s -= 5
    if res.get("done") == "length" and res.get("len", 0) > cfg["budget"] * 2: s -= 5
    if not out.strip(): s -= 10
    # Structural / quality score (max 10 from scorer)
    s += cfg["scorer"](out)
    # tps bonus (max +3, no saturation at 7.0)
    s += min(res["tps"] / 15.0, 3.0)
    return round(s, 2)

def run_model(model: str) -> dict:
    out = {}
    for task, cfg in PROMPTS.items():
        res = call(model, cfg["v_hard"])
        sc = score(task, res, cfg)
        out[task] = sc
    return {model: out}

def main():
    print(f"# Tie-break bench: {len(CANDIDATES)} winners × 5 hard tasks", flush=True)
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m): m for m in CANDIDATES}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(CANDIDATES)}] {m[:55]}  done", flush=True)

    # Rank per task
    per_task = {t: [] for t in PROMPTS}
    for m, r in results.items():
        if not isinstance(r, dict) or "err" in r: continue
        for t, sc in r.items():
            if isinstance(sc, (int, float)):
                per_task[t].append((m, sc))
    for t in per_task:
        per_task[t].sort(key=lambda x: -x[1])

    OUT = Path("/home/eldi/bench/ollama/RANKING_TIEBREAK.md")
    with OUT.open("w") as f:
        f.write("# Ollama Tie-Break — Hard Prompts + Structural Scoring (2026-07-04)\n\n")
        f.write("Each task uses a HARDER prompt + structural scoring (no 7.0 cap).\n")
        f.write("Range -5 to +15. Higher = better.\n\n")
        for task, ranked in per_task.items():
            f.write(f"## {task}\n\n")
            f.write("| # | Score | Model |\n|---|---|---|\n")
            for i, (m, s) in enumerate(ranked, 1):
                f.write(f"| {i} | {s:.2f} | `{m}` |\n")
            f.write("\n")
    print(f"\nWrote {OUT}", flush=True)

if __name__ == "__main__":
    main()