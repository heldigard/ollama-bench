"""Pure parsing, relevance metrics, and quality-only promotion policy."""

from __future__ import annotations

import json
import math
from statistics import mean


def parse_ranking(output: str, allowed_ids: set[str]) -> tuple[str, ...] | None:
    """Accept only an exact JSON top-3 with unique known document IDs."""
    try:
        payload = json.loads(output.strip())
    except (TypeError, json.JSONDecodeError):
        return None
    ranking = payload.get("ranking") if isinstance(payload, dict) else None
    if not isinstance(ranking, list) or len(ranking) != 3:
        return None
    if not all(isinstance(doc_id, str) for doc_id in ranking):
        return None
    result = tuple(ranking)
    if len(set(result)) != 3 or not set(result).issubset(allowed_ids):
        return None
    return result


def ndcg_at_k(ranking: tuple[str, ...] | None, relevance: dict[str, int], k: int = 3) -> float:
    """Return normalized discounted cumulative gain for graded relevance."""
    if not ranking:
        return 0.0
    dcg = sum(
        (2 ** relevance.get(doc_id, 0) - 1) / math.log2(position + 1)
        for position, doc_id in enumerate(ranking[:k], 1)
    )
    ideal = sorted(relevance.values(), reverse=True)[:k]
    ideal_dcg = sum(
        (2**score - 1) / math.log2(position + 1) for position, score in enumerate(ideal, 1)
    )
    return round(dcg / ideal_dcg, 4) if ideal_dcg else 0.0


def mrr_at_k(ranking: tuple[str, ...] | None, relevance: dict[str, int], k: int = 3) -> float:
    """Return reciprocal rank of the first directly useful document (grade >= 2)."""
    if not ranking:
        return 0.0
    for position, doc_id in enumerate(ranking[:k], 1):
        if relevance.get(doc_id, 0) >= 2:
            return round(1 / position, 4)
    return 0.0


def summarize(rows: list[dict]) -> dict:
    """Aggregate quality metrics; latency is deliberately not part of the score."""
    total = len(rows)
    return {
        "cases": total,
        "ndcg_at_3": round(mean(float(row["ndcg_at_3"]) for row in rows), 4) if rows else 0.0,
        "mrr_at_3": round(mean(float(row["mrr_at_3"]) for row in rows), 4) if rows else 0.0,
        "top1_accuracy": round(sum(bool(row.get("top1_correct")) for row in rows) / total, 4)
        if total
        else 0.0,
        "invalid_rate": round(sum(row.get("ranking") is None for row in rows) / total, 4)
        if total
        else 1.0,
    }


def promotion_decision(candidate: dict, baseline: dict, *, min_ndcg_gain: float) -> dict:
    """Promote only a relevance improvement, never a speed improvement."""
    ndcg_gain = round(float(candidate["ndcg_at_3"]) - float(baseline["ndcg_at_3"]), 4)
    checks = {
        "ndcg_gain": ndcg_gain >= min_ndcg_gain,
        "mrr_no_regression": float(candidate["mrr_at_3"]) >= float(baseline["mrr_at_3"]),
        "format_no_regression": float(candidate["invalid_rate"]) <= float(baseline["invalid_rate"]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "decision": "ACCEPT" if not failed else "REJECT",
        "failed": failed,
        "ndcg_gain": ndcg_gain,
        "checks": checks,
    }
