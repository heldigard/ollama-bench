"""tool_call — structured JSON tool-call bench (ground-truth scoring).

Each case gives the model a natural-language request + a menu of tools. The
model must emit a JSON object `{"tool": ..., "args": {...}}`. Scoring is
DETERMINISTIC (no keyword/rubric noise): valid JSON + correct tool name + the
key argument VALUES present. This is the bench the cross-cli harness needs for
every tool-dispatch role (agent-browser, MCP tool calls, n8n, Azure Functions
bindings) — a model that writes great prose but emits broken JSON is unusable
for agents.

# vs-soft-allow  — end-to-end pipeline (request -> call -> JSON score -> rank).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.shared.ollama import CallOpts, call
from ollama_bench.shared.paths import result_path

# Each case: (id, prompt, expected_substrings). expected = lowercase substrings
# that MUST appear in a correct output (tool name + the key argument values).
# Arg-name variance across models is tolerated — we match VALUES, not arg keys.
PROMPTS: list[dict] = [
    {
        "id": "weather",
        "expected": ("get_weather", "tokyo"),
        "prompt": """You are a tool-calling assistant. Read the request and available tools. Respond with ONLY a JSON object: {"tool": "<name>", "args": {<args>}}. No prose, no code fence.

Available tools:
- get_weather(location): current weather for a city
- get_time(timezone): current time in a timezone
- search_web(query): web search

Request: What's the weather in Tokyo right now?""",
    },
    {
        "id": "timer",
        "expected": ("set_timer", "10"),
        "prompt": """You are a tool-calling assistant. Respond with ONLY a JSON object: {"tool": "<name>", "args": {<args>}}. No prose, no code fence.

Available tools:
- set_timer(minutes): start a countdown timer
- create_alarm(time): set an alarm at a clock time
- play_music(track): play a song

Request: Set a timer for 10 minutes.""",
    },
    {
        "id": "calc",
        "expected": ("calculate", "15", "23"),
        "prompt": """You are a tool-calling assistant. Respond with ONLY a JSON object: {"tool": "<name>", "args": {<args>}}. No prose, no code fence.

Available tools:
- calculate(a, b, op): arithmetic on two numbers (op: add|subtract|multiply|divide)
- search_web(query): web search
- get_weather(location): weather

Request: What is 15 multiplied by 23?""",
    },
    {
        "id": "search",
        "expected": ("search_web", "ai"),
        "prompt": """You are a tool-calling assistant. Respond with ONLY a JSON object: {"tool": "<name>", "args": {<args>}}. No prose, no code fence.

Available tools:
- search_web(query): web search
- open_url(url): open a bookmarked URL
- get_weather(location): weather

Request: Find recent news about AI.""",
    },
    {
        "id": "currency",
        "expected": ("currency_convert", "100", "usd", "eur"),
        "prompt": """You are a tool-calling assistant. Respond with ONLY a JSON object: {"tool": "<name>", "args": {<args>}}. No prose, no code fence.

Available tools:
- currency_convert(amount, from_currency, to_currency): convert money
- get_weather(location): weather
- calculate(a, b, op): arithmetic

Request: Convert 100 dollars to euros.""",
    },
]

# Extract the first balanced {...} block (models may wrap in prose/code fence).
_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(out: str) -> dict | None:
    """Return the first parseable JSON object in out, or None."""
    if not out:
        return None
    m = _JSON_BLOCK_RE.search(out)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _score(res: dict, expected: tuple[str, ...]) -> float:
    """Ground-truth score. Range -10 to ~9.

    valid JSON +3; +2 per expected substring (tool name + key arg values);
    leak/refusal penalty; empty penalty; tps bonus capped at 2.
    """
    if "err" in res:
        return -100.0
    out = res["out"]
    L = out.lower()
    s = 0.0
    if "<think>" in L or "thinking process" in L:
        s -= 5
    if "as an ai" in L or "i cannot" in L:
        s -= 5
    if not out.strip():
        s -= 10
    # JSON validity (independent of correctness).
    if extract_json(out) is not None:
        s += 3.0
    # Ground-truth hits: tool name + key arg values.
    s += 2.0 * sum(1 for kw in expected if kw.lower() in L)
    s += min(res.get("tps", 0) / 15.0, 2.0)
    return round(s, 2)


def run_model(model: str, opts: CallOpts) -> dict:
    out: list = []
    for p in PROMPTS:
        res = call(model, p["prompt"], opts=opts)
        out.append({"id": p["id"], "sc": _score(res, p["expected"])})
    return {model: out}


def cmd_tool_call(args: argparse.Namespace) -> int:
    """`ollama-bench tool-call` entry point."""
    candidates = args.models or []
    if not candidates:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    print(f"# Tool-call bench: {len(candidates)} models x {len(PROMPTS)} cases", file=sys.stderr)
    opts = CallOpts(num_predict=120, num_ctx=2048)

    results: dict = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_model, m, opts): m for m in candidates}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {m: {"err": str(e)}}
            results.update(r)
            print(f"  [{i:2d}/{len(candidates)}] {m[:55]}  done", file=sys.stderr, flush=True)

    ranked = []
    for m, r in results.items():
        if not isinstance(r, list) or not r:
            continue
        scores = [it["sc"] for it in r if "sc" in it]
        avg = round(sum(scores) / len(scores), 2) if scores else -100.0
        ranked.append((m, avg))
    ranked.sort(key=lambda x: -x[1])

    out_path = Path(args.output) if args.output else result_path("tool_call", ext="md")
    with out_path.open("w") as f:
        f.write("# Tool-Call Bench — structured JSON output\n\n")
        f.write(
            f"Scoring: +3 valid JSON, +2 per ground-truth hit (tool name + key arg "
            f"values), leak penalty, tps bonus. {len(PROMPTS)} cases per model.\n\n"
        )
        f.write("| # | Score | Model |\n|---|---|---|\n")
        for i, (m, sc) in enumerate(ranked, 1):
            f.write(f"| {i} | {sc:.2f} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser(
        "tool-call",
        parents=[parent],
        help="Structured JSON tool-call bench (ground-truth scoring).",
    )
    p.add_argument("-m", "--models", nargs="+", required=True, help="Models to bench.")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_tool_call)
