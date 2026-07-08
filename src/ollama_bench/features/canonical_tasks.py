"""Canonical task prompts and task-specific scoring.

This module is shared by `deep` and `tie_break` so the benchmark measures the
same capabilities in first-pass and hard-prompt modes.
"""
from __future__ import annotations

import ast
import re
from typing import Any

from ollama_bench.shared.scorer import detect_leaks, prepare_scored_response, tps_bonus

CANONICAL_TASKS = ("improve", "codeq_sum", "smart_trim", "web_synth", "code_gen")

_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _words(text: str) -> list[str]:
    return re.findall(r"\b[\w.+#/-]+\b", text.lower())


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def _keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
    low = text.lower()
    return sum(1 for kw in keywords if kw.lower() in low)


def _line_count_with_prefix(text: str, prefixes: tuple[str, ...]) -> int:
    return sum(
        1
        for line in text.splitlines()
        if line.strip().lower().startswith(prefixes)
    )


def _paragraph_count(text: str) -> int:
    return len([p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()])


def _extract_code(text: str) -> str:
    match = _CODE_FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    start = text.find("def ")
    if start >= 0:
        return text[start:].strip()
    return text.strip()


def _parse_function(code: str, expected_name: str) -> ast.FunctionDef | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    for fn in funcs:
        if fn.name == expected_name:
            return fn
    return None


def _hygiene(res: dict, budget_words: int) -> tuple[float, dict[str, Any]]:
    if "err" in res:
        return -100.0, {"error": res["err"]}
    out = str(res.get("out", "") or "")
    wc = len(out.split())
    leaks = detect_leaks(out)
    score = 0.0
    detail: dict[str, Any] = {
        "word_count": wc,
        "leaks": ",".join(leaks),
        "tps": round(float(res.get("tps", 0) or 0), 2),
    }
    if not out.strip():
        score -= 10.0
        detail["empty"] = 1
    if leaks:
        score -= 6.0
        detail["leak_penalty"] = -6.0
    low = out.lower()
    if "as an ai" in low or "i cannot" in low:
        score -= 5.0
        detail["refusal_penalty"] = -5.0
    if wc <= budget_words:
        score += 1.0
        detail["budget"] = "ok"
    elif wc <= int(budget_words * 1.5):
        score += 0.4
        detail["budget"] = "soft"
    else:
        score -= 1.5
        detail["budget"] = "over"
    if res.get("done") == "length":
        score -= 2.0
        detail["truncated"] = 1
    speed = tps_bonus(float(res.get("tps", 0) or 0), cap=1.5)
    score += speed
    detail["speed_bonus"] = speed
    return score, detail


def score_task_response(
    task: str, res: dict, case: dict, strip_strippable: bool = True
) -> dict[str, Any]:
    """Return `{score, metrics}` for one canonical task response."""
    if "err" in res:
        return {"score": -100.0, "metrics": {"error": res["err"]}}
    res, policy_metrics = prepare_scored_response(res, strip_strippable=strip_strippable)
    out = str(res.get("out", "") or "")
    base, metrics = _hygiene(res, int(case["budget_words"]))
    metrics.update(policy_metrics)
    scorer = {
        "improve": _score_improve,
        "codeq_sum": _score_codeq_sum,
        "smart_trim": _score_smart_trim,
        "web_synth": _score_web_synth,
        "code_gen": _score_code_gen,
    }[task]
    task_score, task_metrics = scorer(out, case)
    metrics.update(task_metrics)
    return {"score": round(base + task_score, 2), "metrics": metrics}


def _score_improve(out: str, case: dict) -> tuple[float, dict[str, Any]]:
    low = out.lower()
    expected_sections = ("## goal", "## assumptions", "## files", "## steps", "## acceptance")
    section_hits = sum(1 for section in expected_sections if section in low)
    anchors = _keyword_hits(out, tuple(case["anchors"]))
    step_lines = _line_count_with_prefix(out, ("1.", "2.", "3.", "4.", "5.", "- "))
    concrete = sum(
        1
        for token in ("test", "pytest", "curl", "trace", "profile", "measure", "log", "reproduce")
        if token in low
    )
    score = section_hits * 1.0 + min(anchors, 5) * 0.9 + min(step_lines, 5) * 0.35
    score += min(concrete, 4) * 0.35
    if _contains_any(low, ("generic advice", "best practices", "it depends")):
        score -= 1.5
    return score, {
        "sections": section_hits,
        "anchor_hits": anchors,
        "step_lines": step_lines,
        "concrete_terms": concrete,
    }


def _score_codeq_sum(out: str, case: dict) -> tuple[float, dict[str, Any]]:
    stripped = out.strip()
    words = _words(stripped)
    keyword_hits = _keyword_hits(stripped, tuple(case["anchors"]))
    sentences = len(re.findall(r"[.!?](?:\s|$)", stripped)) or (1 if stripped else 0)
    score = min(keyword_hits, 5) * 1.35
    if len(words) <= int(case["budget_words"]):
        score += 1.3
    if sentences == 1:
        score += 1.2
    if "```" in stripped or "\n" in stripped:
        score -= 1.2
    if _contains_any(stripped, ("this function", "the function")):
        score += 0.4
    return score, {
        "anchor_hits": keyword_hits,
        "sentences": sentences,
        "summary_words": len(words),
        "format_clean": int("```" not in stripped and "\n" not in stripped),
    }


def _score_smart_trim(out: str, case: dict) -> tuple[float, dict[str, Any]]:
    low = out.lower()
    required = ("task", "decision", "current", "next", "block")
    required_hits = _keyword_hits(low, required)
    anchors = _keyword_hits(low, tuple(case["anchors"]))
    bullet_count = _line_count_with_prefix(out, ("- ", "* "))
    score = required_hits * 0.9 + min(anchors, 8) * 0.85
    if 4 <= bullet_count <= 10:
        score += 1.2
    elif bullet_count:
        score += 0.4
    if _contains_any(low, ("transcript", "earlier", "assistant explained")):
        score -= 1.0
    return score, {
        "required_hits": required_hits,
        "anchor_hits": anchors,
        "bullet_count": bullet_count,
    }


def _score_web_synth(out: str, case: dict) -> tuple[float, dict[str, Any]]:
    low = out.lower()
    anchors = _keyword_hits(low, tuple(case["anchors"]))
    citations = len(set(re.findall(r"\[(\d+)\]", out)))
    paragraphs = _paragraph_count(out)
    contradiction = int(_contains_any(low, tuple(case.get("disagreement_terms", ()))))
    score = min(anchors, 8) * 0.9 + min(citations, int(case["source_count"])) * 0.9
    if 2 <= paragraphs <= 4:
        score += 1.0
    if case.get("requires_disagreement"):
        score += 1.8 if contradiction else -1.5
    if _contains_any(low, ("according to the sources", "sources say")) and citations == 0:
        score -= 1.0
    return score, {
        "anchor_hits": anchors,
        "citations": citations,
        "paragraphs": paragraphs,
        "disagreement": contradiction,
    }


def _score_code_gen(out: str, case: dict) -> tuple[float, dict[str, Any]]:
    code = _extract_code(out)
    fn = _parse_function(code, str(case["function"]))
    low_code = code.lower()
    anchor_hits = _keyword_hits(low_code, tuple(case["anchors"]))
    score = min(anchor_hits, 6) * 0.95
    if fn is not None:
        score += 2.0
        arg_names = [a.arg for a in fn.args.args]
        expected_args = list(case.get("args", ()))
        if arg_names[: len(expected_args)] == expected_args:
            score += 1.2
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(fn))
        if has_return:
            score += 1.0
    else:
        has_return = False
    if "import " in low_code and not case.get("allow_imports"):
        score -= 1.5
    prose_lines = [
        line for line in out.splitlines()
        if line.strip() and not line.lstrip().startswith(("def ", "if ", "for ", "while ", "return", "import", "from", "try:", "except", "else:", "elif ", "#", "seen", "out", "result", "chunks", "current"))
    ]
    if len(prose_lines) > 2:
        score -= 1.0
    return score, {
        "ast_ok": int(fn is not None),
        "arg_ok": int(fn is not None and [a.arg for a in fn.args.args][: len(case.get("args", ()))] == list(case.get("args", ()))),
        "has_return": int(has_return),
        "anchor_hits": anchor_hits,
    }


PROMPTS: dict[str, dict[str, Any]] = {
    "improve": {
        "budget_words": 150,
        "items": [
            (
                "improve_auth_flake",
                "Rewrite this vague request into a concrete implementation spec with sections GOAL, ASSUMPTIONS, FILES, STEPS, ACCEPTANCE. Original: users sometimes cannot login after password reset, fix auth.",
                ("password reset", "login", "session", "token", "reproduce", "test", "auth"),
            ),
            (
                "improve_dashboard_perf",
                "Rewrite into an actionable engineering task. Original: haz que el dashboard cargue mas rapido, esta lentisimo cuando hay muchas cuentas.",
                ("dashboard", "many accounts", "profile", "query", "cache", "metric", "acceptance"),
            ),
            (
                "improve_flaky_test",
                "Turn this into a precise debugging spec. Original: el test de checkout falla a veces en CI pero local no.",
                ("checkout", "ci", "flaky", "seed", "timeout", "reproduce", "pytest"),
            ),
            (
                "improve_csv_import",
                "Rewrite into a concise spec. Original: i need the csv thing to import customers but skip bad rows and tell me what failed.",
                ("csv", "customers", "bad rows", "validation", "error report", "acceptance"),
            ),
        ],
    },
    "codeq_sum": {
        "budget_words": 32,
        "items": [
            (
                "sum_send_chat",
                "Summarize this function in ONE sentence, max 30 words. NO preamble, no code blocks.\n\nasync function sendChatMessage(trimmed: string) {\n  if (!trimmed || sending.value) return;\n  draft.value = '';\n  try {\n    await api.post('/chat', { text: trimmed });\n  } catch (e) {\n    error.value = e.message;\n  }\n}",
                ("empty", "sending", "clears", "posts", "error"),
            ),
            (
                "sum_chunk_text",
                "Summarize in ONE sentence, max 30 words. NO preamble.\n\nfunction chunkText(text, maxTokens) {\n  const sentences = text.split(/(?<=[.!?])\\s+/);\n  const out = [];\n  let buf = '';\n  for (const s of sentences) {\n    if ((buf + s).split(/\\s+/).length > maxTokens) { out.push(buf.trim()); buf = s; }\n    else buf += ' ' + s;\n  }\n  if (buf) out.push(buf.trim());\n  return out;\n}",
                ("sentences", "chunks", "max", "tokens", "buffer"),
            ),
            (
                "sum_subscribe",
                "Summarize this function in ONE sentence, max 30 words. Mention the important behavior.\n\nasync function subscribeToTopic(topic, handler) {\n  if (subscriptions.has(topic)) return false;\n  const controller = new AbortController();\n  const conn = await openStream(topic, { signal: controller.signal });\n  subscriptions.set(topic, { controller, handler });\n  conn.on('data', msg => {\n    if (msg.type === 'error') { controller.abort(); unsubscribe(topic); }\n    else handler(msg);\n  });\n  return true;\n}",
                ("topic", "stream", "abort", "unsubscribe", "handler"),
            ),
            (
                "sum_retry",
                "One-sentence summary, max 30 words. NO preamble.\n\nasync function retry(fn, attempts, delayMs) {\n  let lastErr;\n  for (let i = 0; i < attempts; i++) {\n    try { return await fn(); }\n    catch (err) { lastErr = err; await sleep(delayMs * (i + 1)); }\n  }\n  throw lastErr;\n}",
                ("retry", "attempts", "delay", "last", "throws"),
            ),
        ],
    },
    "smart_trim": {
        "budget_words": 170,
        "items": [
            (
                "trim_wsgi_pytest",
                "Compress to handoff bullet list. Keep task, current step, decisions, next action, blockers. 4-8 bullets, no preamble.\n\n[Earlier] User asked about Python venv setup on WSL2. Assistant recommended uv and created .venv. [Earlier] Imports broke because PYTHONPATH pointed at global site-packages. Fixed by removing override. [Now] pytest collected 0 items. Investigating tests/ dir and conftest.py placement. [Now] ruff says no module, same environment root cause. [Decision] Stay on uv, no pip. [Next] Add root conftest.py, reinstall dev deps, run pytest and ruff. [Blocked] None.",
                ("uv", "pytest collected 0", "conftest", "ruff", "next", "blocked none", "pythonpath"),
            ),
            (
                "trim_ci_snapshots",
                "Make a handoff summary. Keep decisions and next action.\n\n[Earlier] CI took 27min: install=4, test=8, build=12, deploy=3. Chose nx affected because repo already uses nx. [Earlier] nx reduced CI to 18min, still too slow. [Now] vitest migration done; snapshots still slow. Found 14 nested snapshots taking 2.1s each. happy-dom is 30 percent faster than jsdom. [Decision] Delete non-visual snapshots, keep only SVG/PNG render snapshots. [Next] PR branch drop-snapshots-v1 and target <10min CI. [Blocked] None.",
                ("ci", "27min", "nx", "vitest", "snapshots", "drop-snapshots-v1", "blocked none"),
            ),
            (
                "trim_azure_zip",
                "Condense this session into a handoff. 5-9 bullets.\n\n[Earlier] Azure Function cold start baseline 4s, target <500ms. Decided premium EP1 plus always-on. [Earlier] Local func start was 1.2s without warmup. [Now] User said deploy it. Need zip package and az functionapp deploy. [Risk] local.settings.json has storage connection string and must not be zipped. [Decision] Use --build-native-deps for cryptography wheels. [Next] Build pkg.zip excluding .venv, __pycache__, Tests, .git, local.settings.json; then deploy. [Blocked] az login is already done.",
                ("azure function", "premium ep1", "always-on", "local.settings.json", "build-native-deps", "pkg.zip", "az login"),
            ),
        ],
    },
    "web_synth": {
        "budget_words": 210,
        "items": [
            (
                "synth_problem_json",
                "Synthesize a 3-paragraph summary with citations [1], [2], [3]. No preamble.\n\n[1] RFC 9457 defines Problem Details for HTTP APIs with type, title, status, detail, instance fields. [2] Microsoft REST API Guidelines recommend problem+json for 4xx/5xx and correlation id in instance. [3] Spring Boot 3.2+ exposes ProblemDetail through ResponseEntityExceptionHandler and RestControllerAdvice.",
                ("problem details", "type", "title", "status", "correlation", "spring boot", "problemdetail"),
            ),
            (
                "synth_conflict_bench",
                "Synthesize with citations. If sources disagree, state the disagreement.\n\n[1] Vendor announcement says Model A reached 64.3 on SWE-bench Verified in Oct 2024. [2] March 2025 blog says Model B reached 62.3 on the same benchmark. [3] Independent December 2025 report lists Model B at 70.3 on the same benchmark.",
                ("64.3", "62.3", "70.3", "same benchmark", "model b", "independent"),
            ),
            (
                "synth_security_policy",
                "Write a 2-3 paragraph synthesis with citations [1][2][3].\n\n[1] OWASP recommends validating redirect targets against an allow-list. [2] A product incident report says unvalidated next= parameters caused account takeover via phishing. [3] The engineering policy requires rejecting absolute external URLs and logging blocked redirect attempts.",
                ("owasp", "allow-list", "next=", "account takeover", "external urls", "logging"),
            ),
        ],
    },
    "code_gen": {
        "budget_words": 120,
        "items": [
            (
                "code_validate_email",
                "Write a Python function `validate_email(s: str) -> bool` using ONLY stdlib re. Handle None, empty, whitespace. Return False on invalid. No docstring, no comments, just the function.",
                ("validate_email", "none", "strip", "re.", "return false", "bool"),
                {"function": "validate_email", "args": ("s",), "allow_imports": True},
            ),
            (
                "code_unique_order",
                "Write Python function `unique_preserve_order(items: list[str | None]) -> list[str]`. Skip None and ''. Keep first-seen order. No imports. Just the function.",
                ("unique_preserve_order", "seen", "none", "append", "return", "items"),
                {"function": "unique_preserve_order", "args": ("items",), "allow_imports": False},
            ),
            (
                "code_chunk_lines",
                "Write Python function `chunk_lines(text: str, max_chars: int) -> list[str]` that returns chunks <= max_chars. Split on newline first, then spaces for long lines. No external deps. Just the function.",
                ("chunk_lines", "max_chars", "split", "append", "return", "line"),
                {"function": "chunk_lines", "args": ("text", "max_chars"), "allow_imports": False},
            ),
            (
                "code_parse_bool",
                "Write Python function `parse_bool(value) -> bool | None`. Return True for yes/true/1/on, False for no/false/0/off, None for unknown or None. No imports. Just the function.",
                ("parse_bool", "true", "false", "none", "lower", "return"),
                {"function": "parse_bool", "args": ("value",), "allow_imports": False},
            ),
        ],
    },
}


def iter_cases(task: str) -> list[dict[str, Any]]:
    """Return normalized cases for a canonical task."""
    cases: list[dict[str, Any]] = []
    cfg = PROMPTS[task]
    for item in cfg["items"]:
        case_id, prompt, anchors = item[:3]
        extra = dict(item[3]) if len(item) > 3 else {}
        case = {
            "id": case_id,
            "prompt": prompt,
            "anchors": anchors,
            "budget_words": cfg["budget_words"],
            **extra,
        }
        if task == "web_synth":
            case.setdefault("source_count", 3)
            case.setdefault("requires_disagreement", case_id == "synth_conflict_bench")
            case.setdefault("disagreement_terms", ("disagree", "discrepancy", "conflict", "different", "reports"))
        cases.append(case)
    return cases


HARD_PROMPTS: dict[str, dict[str, Any]] = {
    task: {
        "budget": max(int(cfg["budget_words"] * 1.35), cfg["budget_words"] + 20),
        "v_hard": "\n\n---\n\n".join(case["prompt"] for case in iter_cases(task)),
        "cases": iter_cases(task),
    }
    for task, cfg in PROMPTS.items()
}
