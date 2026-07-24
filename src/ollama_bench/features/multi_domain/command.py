# vs-soft-allow  - end-to-end pipeline (load model -> bench 4 domains -> JSONL).
"""multi_domain - legacy 4-domain bench (improve/compact/code/reason).

Kept for compatibility with the original 2026-06-27 harness. Most users
should run `deep` instead (5 tasks, modern scoring, think-strip).

# vs-soft-allow  — deep nested control flow in JSONL output + dataclass glue.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ollama_bench.shared.config import OLLAMA_URL, TIMEOUT_DEFAULT

OLLAMA = OLLAMA_URL
TIMEOUT = TIMEOUT_DEFAULT


IMPROVE_PROMPTS = [
    ("improve_vague_1", "fix the auth bug"),
    ("improve_vague_2", "haz que el dashboard cargue mas rapido"),
    ("improve_vague_3", "i need a thing that converts csv to json, like the file thing"),
    ("improve_vague_4", "el test falla a veces, no se porque"),
]


def _compact_1() -> str:
    return (
        "Session transcript (condensed). Goal: summarize as handoff note preserving "
        "task, decisions, current step, blockers, next action.\n\n"
        "[Earlier] User asked about Python venv setup on WSL2. Assistant explained uv vs pip, recommended uv. Created .venv via 'uv venv'. Activated.\n"
        "[Earlier] Discussion about why their existing imports broke. Root cause: site-packages vs .venv/lib conflict. Fixed by removing PYTHONPATH override.\n"
        "[Earlier] User asked about cross-platform wheel compatibility. Assistant noted manylinux2014 vs musllinux. Decided to pin --python 3.12 --platform manylinux2014.\n"
        "[Now] User: 'pero ahora pytest no encuentra los tests'. Assistant running pytest --collect-only. Output shows 'collected 0 items'.\n"
        "[Now] Root cause being investigated: tests/ dir missing __init__.py, or conftest.py not at root. Will check next.\n"
        "[Now] User: 'tambien falla ruff, dice no module'. Same root cause - ruff needs the .venv on path.\n"
        "[Next] Plan: add conftest.py at project root, reinstall dev deps in .venv, re-run pytest + ruff.\n"
        "[Decision] Stay on uv, drop pip completely.\n"
        "[Blocked] No blockers."
    )


def _compact_2() -> str:
    return (
        "Session transcript. Goal: handoff summary.\n\n"
        "[Earlier] Discussing Azure Function cold-start. 4s baseline unacceptable. User wants <500ms.\n"
        "[Earlier] Options: premium plan, always-on, native deps. Decided always-on + premium EP1.\n"
        "[Earlier] Tested locally with func start. Got 1.2s with no warmup.\n"
        "[Now] User: 'deploy it'. Need to: zip package, push via az functionapp deploy. Auth via az login already done.\n"
        "[Now] Concern: storage account connection string in local.settings.json - must NOT include in zip.\n"
        "[Decision] Use --build-native-deps flag for cryptography native wheels.\n"
        "[Blocked] None.\n"
        "[Next] Build pkg.zip (exclude .venv, __pycache__, Tests, .git, local.settings.json). Then az functionapp deploy."
    )


COMPACT_PROMPTS = [
    ("compact_1", _compact_1()),
    ("compact_2", _compact_2()),
]

CODE_PROMPTS = [
    (
        "code_1",
        "Write a Python function `validate_email(s: str) -> bool` using ONLY stdlib (re or email.utils). Handle None/empty/whitespace. Explain edge cases in 2 lines.",
    ),
    (
        "code_2",
        "Write a Python async function `fetch_all(urls: list[str]) -> list[dict]` using aiohttp. Use semaphore to cap concurrency at 10. Return results preserving input order. Include exception handling per URL.",
    ),
    (
        "code_3",
        "Write a Python function `chunk_text(text: str, max_tokens: int) -> list[str]` that splits text into chunks of approx max_tokens, splitting on sentence boundaries when possible. No external deps.",
    ),
]

REASON_PROMPTS = [
    (
        "reason_1",
        "If A > B and B > C, and C = D - 2, and D = 10, what is A? Show reasoning in 3 steps max. End with: ANSWER: <number>",
    ),
    (
        "reason_2",
        "A box has 3 red, 2 blue, 5 green balls. P(red then green without replacement)? Show work. End with: ANSWER: <fraction>",
    ),
]


def _all_tests():
    out: list = []
    out.extend((f"improve_{n}", "improve", p) for n, p in IMPROVE_PROMPTS)
    out.extend((f"compact_{n}", "compact", p) for n, p in COMPACT_PROMPTS)
    out.extend((f"code_{n}", "code", p) for n, p in CODE_PROMPTS)
    out.extend((f"reason_{n}", "reason", p) for n, p in REASON_PROMPTS)
    return out


ALL_TESTS = _all_tests()


@dataclass
class BenchResult:
    model: str
    test_id: str
    domain: str
    prompt_chars: int
    status: str
    error: str = ""
    load_s: float = 0.0
    ttft_s: float = 0.0
    total_s: float = 0.0
    eval_tokens: int = 0
    prompt_tokens: int = 0
    tok_per_s: float = 0.0
    gpu_mem_before_mib: int = 0
    gpu_mem_peak_mib: int = 0
    output: str = ""
    output_chars: int = 0


def _get_installed_models() -> list[dict[str, Any]]:
    """Return raw /api/tags response list."""
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        data = json.load(r)
    return list(data.get("models", []))


def _get_gpu_mem() -> int:
    """Return GPU memory used in MiB."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            timeout=5,
            text=True,
        ).strip()
        return int(out)
    except Exception:
        return -1


def _call(model: str, prompt: str) -> dict:
    """Single Ollama /api/generate call. Non-streaming."""
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 512, "num_ctx": 4096},
        }
    ).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:200]}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    return {
        "total_s": time.perf_counter() - t0,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "eval_tokens": data.get("eval_count", 0),
        "ttft_s": (data.get("prompt_eval_duration", 0) / 1e9)
        if data.get("prompt_eval_duration")
        else 0.0,
        "output": data.get("response", ""),
    }


def _result_from_call(
    model: str, test_id: str, domain: str, prompt: str, call_res: dict, mem_peak: int
) -> BenchResult:
    """Build BenchResult from _call() output."""
    if "error" in call_res:
        return BenchResult(
            model=model,
            test_id=test_id,
            domain=domain,
            prompt_chars=len(prompt),
            status="error",
            error=call_res["error"],
        )
    output = call_res.get("output", "") or ""
    total = call_res.get("total_s") or 0.0
    return BenchResult(
        model=model,
        test_id=test_id,
        domain=domain,
        prompt_chars=len(prompt),
        status="ok",
        load_s=0.0,
        ttft_s=call_res.get("ttft_s", 0.0),
        total_s=total,
        eval_tokens=call_res.get("eval_tokens", 0),
        prompt_tokens=call_res.get("prompt_tokens", 0),
        tok_per_s=(call_res.get("eval_tokens", 0) / total) if total else 0.0,
        gpu_mem_before_mib=0,
        gpu_mem_peak_mib=mem_peak,
        output=output,
        output_chars=len(output),
    )


def bench_one(model: str, test_id: str, domain: str, prompt: str) -> BenchResult:
    """Run a single benchmark (test_id, domain, prompt) on a model."""
    call_res = _call(model, prompt)
    mem_peak = _get_gpu_mem()
    return _result_from_call(model, test_id, domain, prompt, call_res, mem_peak)


def cmd_multi_domain(args) -> int:
    """`ollama-bench multi-domain` entry point."""
    if args.model:
        models = [{"name": args.model}]
    else:
        models = _get_installed_models()
    print(f"# multi-domain bench on {len(models)} models", file=__import__("sys").stderr)
    results: list[BenchResult] = []
    for m in models:
        name = m["name"]
        for test_id, domain, prompt in ALL_TESTS:
            r = bench_one(name, test_id, domain, prompt)
            results.append(r)
    out_path = Path(args.output) if args.output else Path("/tmp/multi_domain_results.jsonl")
    with out_path.open("w") as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + "\n")
    print(f"Wrote {out_path} ({len(results)} results)", file=__import__("sys").stderr)
    return 0


def add_parser(sub, parent):
    """Attach multi-domain subcommand."""
    p = sub.add_parser(
        "multi-domain",
        parents=[parent],
        help="Legacy 4-domain bench (improve/compact/code/reason).",
    )
    p.add_argument("-m", "--model", help="Single model to bench (default: all installed).")
    p.add_argument("-o", "--output", help="Output JSONL path.")
    p.set_defaults(cmd=cmd_multi_domain)
