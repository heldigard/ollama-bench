"""Canonical task scoring + case iteration.

Prompt data lives in prompts.py (PROMPTS, HARD_PROMPTS).
This module provides scoring functions and iter_cases/iter_hard_cases used by
deep and tie_break.
"""

from __future__ import annotations

import ast
import re
from typing import Any

from ollama_bench.features.prompts import HARD_PROMPTS, PROMPTS
from ollama_bench.shared.scorer import detect_leaks, prepare_scored_response, tps_bonus

CANONICAL_TASKS = ("improve", "codeq_sum", "smart_trim", "web_synth", "code_gen")

_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

# Re-export for downstream imports
__all__ = [
    "CANONICAL_TASKS",
    "PROMPTS",
    "HARD_PROMPTS",
    "iter_cases",
    "iter_hard_cases",
    "score_task_response",
]


def _words(text: str) -> list[str]:
    return re.findall(r"\b[\w.+#/-]+\b", text.lower())


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def _keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
    low = text.lower()
    return sum(1 for kw in keywords if kw.lower() in low)


def _line_count_with_prefix(text: str, prefixes: tuple[str, ...]) -> int:
    return sum(1 for line in text.splitlines() if line.strip().lower().startswith(prefixes))


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
    """Base score: leaks, budget compliance, truncation, speed."""
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
    # Specificity bonus: concrete numbers/paths beat generic placeholders
    concrete_patterns = re.findall(r"\b\d+[.,]?\d*\b|[A-Z]:\\|/[a-z]+/|\.\w{2,4}\b", out)
    if len(concrete_patterns) >= 2:
        score += 0.5
        detail["specificity_bonus"] = 0.5
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
    # Gradated section scoring: partial credit for each section present
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
    # Stronger penalty for generic filler
    for filler in ("generic advice", "best practices", "it depends", "consider using"):
        if filler in low:
            score -= 2.0
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
    # Reward mentioning side effects / error handling
    if _contains_any(stripped, ("error", "exception", "throw", "catch", "swallow", "silently")):
        score += 0.6
    # Penalize mentioning implementation details (loop type, variable names)
    impl_details = sum(
        1 for w in ("for loop", "while loop", "variable", "array", "index") if w in stripped.lower()
    )
    if impl_details > 0:
        score -= 0.5 * impl_details
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
    # Reward conflict-flagging when present
    if _contains_any(low, ("contradict", "conflict", "reverted", "switched back", "changed mind")):
        score += 1.0
    # Penalize restating the prompt verbatim
    prompt_words = set(_words(case["prompt"]))
    out_words = set(_words(out))
    if prompt_words and len(out_words & prompt_words) / max(len(out_words), 1) > 0.7:
        score -= 0.8
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
    # Source utilization: penalize citing a source without using its key claim
    cited_nums = set(re.findall(r"\[(\d+)\]", out))
    for src_num in cited_nums:
        # Check if at least one anchor from the source context appears near the citation
        src_context = re.search(rf"\[{src_num}\][^.]*", case["prompt"])
        if src_context:
            src_text = src_context.group().lower()
            # Any anchor mentioned in the source text should appear in the output
            src_anchors = [a for a in case["anchors"] if a.lower() in src_text]
            if src_anchors and not any(a.lower() in low for a in src_anchors):
                score -= 0.3
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
        # Edge-case handling: bonus for defensive patterns
        has_try = any(isinstance(n, ast.Try) for n in ast.walk(fn))
        has_if_guard = any(isinstance(n, ast.If) for n in ast.walk(fn))
        if has_try:
            score += 0.5
        if has_if_guard:
            score += 0.3
    else:
        has_return = False
    if "import " in low_code and not case.get("allow_imports"):
        score -= 1.5
    prose_lines = [
        line
        for line in out.splitlines()
        if line.strip()
        and not line.lstrip().startswith(
            (
                "def ",
                "if ",
                "for ",
                "while ",
                "return",
                "import",
                "from",
                "try:",
                "except",
                "else:",
                "elif ",
                "#",
                "seen",
                "out",
                "result",
                "chunks",
                "current",
            )
        )
    ]
    if len(prose_lines) > 2:
        score -= 1.0
    return score, {
        "ast_ok": int(fn is not None),
        "arg_ok": int(
            fn is not None
            and [a.arg for a in fn.args.args][: len(case.get("args", ()))]
            == list(case.get("args", ()))
        ),
        "has_return": int(has_return),
        "anchor_hits": anchor_hits,
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
            case.setdefault(
                "disagreement_terms",
                ("disagree", "discrepancy", "conflict", "different", "reports"),
            )
        cases.append(case)
    return cases


def iter_hard_cases(task: str) -> list[dict[str, Any]]:
    """Return normalized hard cases for tie-break."""
    cases: list[dict[str, Any]] = []
    cfg = HARD_PROMPTS[task]
    for item in cfg["items"]:
        case_id, prompt, anchors = item[:3]
        extra = dict(item[3]) if len(item) > 3 else {}
        case = {
            "id": case_id,
            "prompt": prompt,
            "anchors": anchors,
            "budget_words": cfg["budget"],
            **extra,
        }
        if task == "web_synth":
            case.setdefault("source_count", 5)
            case.setdefault(
                "requires_disagreement", "contradict" in case_id or "no_consensus" in case_id
            )
            case.setdefault(
                "disagreement_terms",
                (
                    "disagree",
                    "discrepancy",
                    "conflict",
                    "different",
                    "contradict",
                    "warns",
                    "regret",
                ),
            )
        cases.append(case)
    return cases
