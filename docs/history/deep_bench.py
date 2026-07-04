#!/usr/bin/env python3
"""Deep-bench: 5 tasks × N working models. Output per-task ranking.

Tasks (match the actual harness wiring):
  1. improve   — prompt improver hook (vague → structured spec)
  2. codeq_sum — codeq summary (1-line orient of a function body)
  3. smart_trim — smart-trim (transcript → handoff, 4-8 bullets)
  4. web_synth — web_research synth (sources → 200w summary)
  5. code_gen  — code-gen (small function w/ type hints)

Each model runs 2 prompts/task (10 calls/model). Scoring:
  - leak (think_tag / thinking_process / refusal / budget_burn): -5 each
  - words within budget: +2
  - tps higher is better: continuous
Top 5 per task. Output TSV + Markdown.
"""
from __future__ import annotations
import json, time, urllib.request, urllib.error, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean

OLLAMA = "http://localhost:11434"
NUM_PREDICT = 200
TIMEOUT = 240
WORKERS = 4  # concurrent model calls (only one model loaded at a time anyway)

PROMPTS = {
    "improve": {
        "budget_words": 120,
        "items": [
            ("improve_v1", "haz que el dashboard cargue mas rapido, esta lentisimo"),
            ("improve_v2", "fix the auth bug, users cant login"),
        ],
    },
    "codeq_sum": {
        "budget_words": 30,
        "items": [
            ("sum_v1",
             "Summarize this function in ONE sentence, max 30 words. NO preamble, no code blocks.\n\n"
             "async function sendChatMessage(trimmed: string) {\n"
             "  if (!trimmed || sending.value) return;\n"
             "  draft.value = '';\n"
             "  try {\n"
             "    await api.post('/chat', { text: trimmed });\n"
             "  } catch (e) {\n"
             "    error.value = e.message;\n"
             "  }\n"
             "}"),
            ("sum_v2",
             "Summarize in ONE sentence, max 30 words. NO preamble.\n\n"
             "function chunkText(text, maxTokens) {\n"
             "  const sentences = text.split(/(?<=[.!?])\\s+/);\n"
             "  const out = [];\n"
             "  let buf = '';\n"
             "  for (const s of sentences) {\n"
             "    if ((buf + s).split(/\\s+/).length > maxTokens) {\n"
             "      out.push(buf.trim());\n"
             "      buf = s;\n"
             "    } else buf += ' ' + s;\n"
             "  }\n"
             "  if (buf) out.push(buf.trim());\n"
             "  return out;\n"
             "}"),
        ],
    },
    "smart_trim": {
        "budget_words": 150,
        "items": [
            ("trim_v1", """Compress to handoff bullet list. Keep: task, current step, decisions, next action, blockers. 4-8 bullets, no preamble.

[Earlier] User asked about Python venv setup on WSL2. Assistant explained uv vs pip, recommended uv. Created .venv via 'uv venv'.
[Earlier] Discussion about why their existing imports broke. Root cause: site-packages vs .venv/lib conflict. Fixed by removing PYTHONPATH override.
[Now] User: 'pytest no encuentra los tests'. Output: 'collected 0 items'. Investigating tests/ dir missing __init__.py, or conftest.py not at root.
[Now] User: 'tambien falla ruff, dice no module'. Same root cause - ruff needs the .venv on path.
[Decision] Stay on uv, drop pip completely. Add conftest.py at project root, reinstall dev deps in .venv.
[Blocked] None."""),
        ],
    },
    "web_synth": {
        "budget_words": 180,
        "items": [
            ("synth_v1", """Synthesize a 3-paragraph summary (no preamble) of the following sources. Cite as [1], [2], etc.

[1] RFC 9457 (2023) "Problem Details for HTTP APIs" defines a standard format for error responses (application/problem+json) with type, title, status, detail, instance fields.
[2] Microsoft REST API Guidelines (2024) recommend using problem+json for 4xx/5xx responses; include a correlation id in 'instance' for tracing.
[3] Spring Boot 3.2+ has built-in ProblemDetail support via ResponseEntityExceptionHandler and @RestControllerAdvice."""),
        ],
    },
    "code_gen": {
        "budget_words": 90,
        "items": [
            ("code_v1",
             "Write a Python function `validate_email(s: str) -> bool` using ONLY stdlib (re). Handle None/empty/whitespace. Return False on invalid. No imports beyond re. No docstring, no comments, just the function."),
            ("code_v2",
             "Write a Python function `chunk_lines(text: str, max_chars: int) -> list[str]` that splits text into chunks of <= max_chars, splitting on '\\n' first, then on ' ' if a line is too long. No external deps. Just the function, no comments."),
        ],
    },
}

def get_models() -> list[str]:
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        return [m["name"] for m in json.load(r).get("models", [])]

def call(model: str, prompt: str) -> dict:
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.2, "num_predict": NUM_PREDICT, "num_ctx": 4096},
    }).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
    except Exception as e:
        return {"err": f"{type(e).__name__}: {str(e)[:200]}"}
    dt = time.perf_counter() - t0
    out = data.get("response", "") or ""
    return {
        "dt": round(dt, 2),
        "tps": round(data.get("eval_count", 0) / dt, 1) if dt > 0 else 0.0,
        "etoks": data.get("eval_count", 0),
        "len": len(out),
        "done": data.get("done_reason"),
        "out": out,
    }

def score(task: str, res: dict, budget: int) -> float:
    """Higher = better. Penalize leaks, reward speed + brevity."""
    if "err" in res:
        return -100.0
    out = res["out"]
    L = out.lower()
    s = 0.0
    # leak penalties
    if "<think>" in L or "</think>" in L: s -= 5
    if "thinking process" in L: s -= 3
    if "as an ai" in L or "i cannot" in L: s -= 5
    if res["done"] == "length" and res["etoks"] >= NUM_PREDICT - 1:
        s -= 2  # hit the cap
    if not out.strip(): s -= 10
    # words within budget = good
    wc = len(out.split())
    if wc <= budget: s += 2
    elif wc <= budget * 1.5: s += 1
    # tps bonus (capped)
    s += min(res["tps"] / 10.0, 5.0)
    # length penalty for over-budget
    if wc > budget * 2: s -= 3
    return round(s, 2)

def run_model(model: str) -> dict:
    """Return {task: [score1, score2, ...]}."""
    out: dict[str, list] = {t: [] for t in PROMPTS}
    for task, cfg in PROMPTS.items():
        for pid, prompt in cfg["items"]:
            res = call(model, prompt)
            sc = score(task, res, cfg["budget_words"])
            out[task].append({
                "pid": pid, "sc": sc, "dt": res.get("dt", 0),
                "tps": res.get("tps", 0), "len": res.get("len", 0),
                "out_head": (res.get("out", "") or "")[:140].replace("\n", " "),
            })
    return {model: out}

def main():
    # 35 keep + 3 potential + 4 winners being re-pulled = up to 42 candidates.
    # The broken 12 non-winners are excluded (skip — not loaded).
    keep = [r["name"] for r in (
        __import__("csv").DictReader(
            open("/home/eldi/bench/ollama/results_smoke_all.tsv"),
            delimiter="\t",
        )
    ) if r["status"] == "ok" or r["status"].startswith("leak")]

    # Remove embeddings (they don't generate)
    keep = [m for m in keep if "embed" not in m.lower()]

    # Also add the 4 winners being re-pulled (in case they succeed)
    winners = [
        "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest",
        "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
    ]
    installed = set(get_models())
    candidates = keep + [w for w in winners if w in installed]
    # dedupe preserving order
    seen = set()
    candidates = [m for m in candidates if not (m in seen or seen.add(m))]

    print(f"# Deep-bench: {len(candidates)} candidates × {sum(len(c['items']) for c in PROMPTS.values())} prompts", file=sys.stderr)

    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_model, m): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(candidates)}] {m[:60]}", file=sys.stderr, flush=True)

    # Aggregate per-task score (mean of prompts)
    per_task_rank: dict[str, list] = {t: [] for t in PROMPTS}
    for m, r in results.items():
        if "err" in r or not isinstance(r, dict):
            continue
        for t, items in r.items():
            scores = [it["sc"] for it in items if "sc" in it]
            if scores:
                per_task_rank[t].append((m, round(mean(scores), 2)))

    # Sort by score desc
    for t in per_task_rank:
        per_task_rank[t].sort(key=lambda x: -x[1])

    # Output
    OUT = Path("/home/eldi/bench/ollama/results_deep_bench.tsv")
    RANK = Path("/home/eldi/bench/ollama/RANKING.md")
    with OUT.open("w") as f:
        f.write("task\trank\tscore\tmodel\n")
        for t, ranked in per_task_rank.items():
            for i, (m, s) in enumerate(ranked, 1):
                f.write(f"{t}\t{i}\t{s}\t{m}\n")
    print(f"\nWrote {OUT}", file=sys.stderr)

    with RANK.open("w") as f:
        f.write("# Ollama Deep-Bench — Top 5 per task (2026-07-04)\n\n")
        for t, ranked in per_task_rank.items():
            f.write(f"\n## {t}\n\n")
            f.write("| # | Score | Model |\n|---|---|---|\n")
            for i, (m, s) in enumerate(ranked[:5], 1):
                f.write(f"| {i} | {s} | `{m}` |\n")
    print(f"Wrote {RANK}", file=sys.stderr)

if __name__ == "__main__":
    main()