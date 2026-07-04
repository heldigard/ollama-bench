"""browser_tool — ref-based browser-action bench (ground-truth scoring).

Each case gives the model a goal + a small a11y snapshot with `eN` refs. The
model must emit `{"action": ..., "ref": ...}` where the action is a known verb
AND the ref actually EXISTS in the snapshot. This is the quality the cross-CLI
agent_browser_subagent.py needs: snap+ref compliance (a call with a ref that
isn't in the snapshot is a hallucination the browser can't execute).

Distinct from tool_call: tool_call validates tool-name + arg VALUES; browser_tool
validates that the ref token is GROUNDED in the provided snapshot. A model that
writes great JSON but invents `e42` when only e1-e11 exist is unusable here.

# vs-soft-allow  — end-to-end pipeline (goal + snapshot -> {action,ref} -> score -> rank).
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

# Canonical action verbs agent_browser accepts (mirrors its KNOWN_ACTIONS).
KNOWN_ACTIONS = frozenset(
    {
        "click",
        "press",
        "tap",
        "fill",
        "type",
        "input",
        "enter",
        "select",
        "scroll",
        "scrollintoview",
        "wait",
        "wait_for",
        "sleep",
        "eval",
        "evaluate",
        "navigate",
        "open_url",
        "goto",
    }
)
# Actions that take NO ref (the ref is a URL / inline arg, not a snapshot token).
NO_REF_ACTIONS = frozenset(
    {"eval", "evaluate", "navigate", "open_url", "goto", "wait", "wait_for", "sleep"}
)

# Each case: id, goal, snapshot (multi-line a11y tree with eN refs), expected_action,
# expected_ref (the ref the call should target, or None for no-ref actions).
CASES: list[dict] = [
    {
        "id": "click_link",
        "expected_action": "click",
        "expected_ref": "e3",
        "goal": "Click the Login link.",
        "snapshot": (
            "a11y snapshot:\n"
            "- e1: heading 'Welcome'\n"
            "- e2: link 'Home'\n"
            "- e3: link 'Login'\n"
            "- e4: link 'Help'\n"
        ),
    },
    {
        "id": "fill_search",
        "expected_action": "fill",
        "expected_ref": "e5",
        "goal": "Type 'laptop' in the search box.",
        "snapshot": (
            "a11y snapshot:\n"
            "- e5: textbox 'Search products'\n"
            "- e6: button 'Search'\n"
            "- e7: link 'Cart'\n"
        ),
    },
    {
        "id": "submit_button",
        "expected_action": "click",
        "expected_ref": "e7",
        "goal": "Submit the form.",
        "snapshot": (
            "a11y snapshot:\n"
            "- e4: textbox 'Email'\n"
            "- e6: textbox 'Password'\n"
            "- e7: button 'Submit'\n"
            "- e8: button 'Reset'\n"
        ),
    },
    {
        "id": "open_url_no_ref",
        "expected_action": "navigate",
        "expected_ref": None,
        "goal": "Go to https://example.com.",
        "snapshot": (
            "a11y snapshot:\n"
            "- e1: heading 'Dashboard'\n"
            "- e2: link 'Profile'\n"
            "(no snapshot ref for an external URL — navigate takes the URL inline)\n"
        ),
    },
    {
        "id": "select_dropdown",
        "expected_action": "select",
        "expected_ref": "e9",
        "goal": "Choose 'Premium' from the plan dropdown.",
        "snapshot": (
            "a11y snapshot:\n"
            "- e8: heading 'Choose your plan'\n"
            "- e9: combobox 'Plan' options: Basic, Premium, Pro\n"
            "- e10: button 'Continue'\n"
        ),
    },
    {
        "id": "scroll_to_region",
        "expected_action": "scroll",
        "expected_ref": "e11",
        "goal": "Scroll down to the comments section.",
        "snapshot": (
            "a11y snapshot:\n"
            "- e1: heading 'Article'\n"
            "- e5: region 'Body'\n"
            "- e11: region 'Comments'\n"
            "- e12: button 'Reply'\n"
        ),
    },
]

_REF_RE = re.compile(r"\be(\d+)\b")
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


def refs_in_snapshot(snapshot: str) -> set[str]:
    """All `eN` refs that appear in the snapshot (the ground-truth ref universe)."""
    return {f"e{n}" for n in _REF_RE.findall(snapshot)}


def _score(res: dict, case: dict) -> float:
    """Ground-truth score. Range -10 to ~10.

    Leak/refusal/empty penalties; +3 valid JSON; +3 valid action (known verb);
    +3 grounded ref (ref exists in snapshot AND matches the expected target, or
    for NO_REF_ACTIONS the model correctly omits/inlines it); tps bonus capped at 2.
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

    obj = extract_json(out)
    if obj is not None:
        s += 3.0

    action = str(obj.get("action", "")).lower().strip() if obj else ""
    ref = str(obj.get("ref", "")).strip() if obj else ""

    if action in KNOWN_ACTIONS:
        s += 3.0
        if action in NO_REF_ACTIONS:
            # Correct no-ref action; reward if it didn't invent a snapshot ref.
            if ref in ("", "null", "none") or ref.lower() in case.get("goal", "").lower():
                s += 3.0
        else:
            valid_refs = refs_in_snapshot(case["snapshot"])
            expected_ref = case.get("expected_ref")
            # Ref must be grounded in the snapshot, ideally the expected target.
            if ref in valid_refs:
                s += 2.0
                if ref == expected_ref:
                    s += 1.0

    s += min(res.get("tps", 0) / 15.0, 2.0)
    return round(s, 2)


def _build_prompt(case: dict) -> str:
    return f"""You are a browser-automation agent. Given a goal and an a11y snapshot, propose the NEXT single ref-based action. Respond with ONLY a JSON object: {{"action": "<verb>", "ref": "<eN or null>"}}. No prose, no code fence.

Rules:
  - action: one of click, fill, select, scroll, navigate (navigate takes the URL inline, NOT a snapshot ref)
  - ref: the eN token from the snapshot the action targets, or null for navigate

{case["snapshot"]}
Goal: {case["goal"]}"""


def run_model(model: str, opts: CallOpts) -> dict:
    out: list = []
    for c in CASES:
        res = call(model, _build_prompt(c), opts=opts)
        out.append({"id": c["id"], "sc": _score(res, c)})
    return {model: out}


def cmd_browser_tool(args: argparse.Namespace) -> int:
    """`ollama-bench browser-tool` entry point."""
    candidates = args.models or []
    if not candidates:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    print(f"# Browser-tool bench: {len(candidates)} models x {len(CASES)} cases", file=sys.stderr)
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

    out_path = Path(args.output) if args.output else result_path("browser_tool", ext="md")
    with out_path.open("w") as f:
        f.write("# Browser-Tool Bench — ref-grounded a11y actions\n\n")
        f.write(
            f"Scoring: +3 valid JSON, +3 known action, +3 grounded ref (exists in snapshot, "
            f"matches expected target), leak penalty, tps bonus. {len(CASES)} cases per model.\n\n"
        )
        f.write("| # | Score | Model |\n|---|---|---|\n")
        for i, (m, sc) in enumerate(ranked, 1):
            f.write(f"| {i} | {sc:.2f} | `{m}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser(
        "browser-tool",
        parents=[parent],
        help="Ref-grounded browser-action bench (snap+ref compliance).",
    )
    p.add_argument("-m", "--models", nargs="+", required=True, help="Models to bench.")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_browser_tool)
