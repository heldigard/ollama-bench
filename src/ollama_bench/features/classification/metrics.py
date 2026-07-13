"""Pure scoring and promotion policy for classification results."""

from __future__ import annotations

from statistics import median


def parse_label(output: str, allowed: tuple[str, ...]) -> str | None:
    """Accept a single closed-set label; reject prose and ambiguous output."""
    candidate = output.strip().strip("`'\".").lower()
    return candidate if candidate in allowed else None


def summarize(rows: list[dict], labels: tuple[str, ...]) -> dict:
    """Return deterministic accuracy, macro-F1, invalid rate, and speed metrics."""
    total = len(rows)
    correct = sum(row.get("pred") == row["gold"] for row in rows)
    invalid = sum(row.get("pred") is None for row in rows)
    f1s: list[float] = []
    for label in labels:
        tp = sum(row.get("pred") == label and row["gold"] == label for row in rows)
        fp = sum(row.get("pred") == label and row["gold"] != label for row in rows)
        fn = sum(row.get("pred") != label and row["gold"] == label for row in rows)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    latencies = [float(row["dt"]) for row in rows if float(row.get("dt", 0)) > 0]
    tps_values = [float(row["tps"]) for row in rows if float(row.get("tps", 0)) > 0]
    return {
        "cases": total,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "macro_f1": round(sum(f1s) / len(f1s), 4) if f1s else 0.0,
        "invalid_rate": round(invalid / total, 4) if total else 1.0,
        "median_latency": round(median(latencies), 4) if latencies else 0.0,
        "median_tps": round(median(tps_values), 2) if tps_values else 0.0,
    }


def promotion_decision(
    candidate: dict,
    baseline: dict,
    *,
    quality_margin: float,
    min_speedup: float,
    max_size_gib: float,
    max_invalid_rate: float,
) -> dict:
    """Apply the non-negotiable tiny-model promotion gate."""
    candidate_latency = float(candidate.get("median_latency", 0))
    baseline_latency = float(baseline.get("median_latency", 0))
    speedup = baseline_latency / candidate_latency if candidate_latency > 0 else 0.0
    quality_floor = float(baseline["macro_f1"]) - quality_margin
    size_gib = candidate.get("size_gib")
    checks = {
        "quality": float(candidate["macro_f1"]) >= quality_floor,
        "speed": speedup >= min_speedup,
        "size": size_gib is not None and float(size_gib) <= max_size_gib,
        "format_gate": float(candidate["invalid_rate"]) <= max_invalid_rate,
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "decision": "ACCEPT" if not failed else "REJECT",
        "failed": failed,
        "quality_floor": round(quality_floor, 4),
        "latency_speedup": round(speedup, 2),
        "checks": checks,
    }
