"""GPU thermal-safety helpers (cross-feature infrastructure).

Sequential bench runs MUST respect GPU thermals. A prior ThreadPoolExecutor
design maxed the GPU (80°C+), ran for hours, and got killed mid-run, losing all
progress (see memory: bench-gpu-safety). These helpers centralize temperature
monitoring + cooldown gating so every bench feature (deep, smoke, ...) paces
the card the same way. Lives in shared/ so features never duplicate thermal
logic and never import each other.
"""

from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Callable
from typing import Any


def gpu_temp() -> int:
    """Return GPU temperature in °C, or 0 if nvidia-smi is unavailable.

    0 is the sentinel for "no thermal data" — callers treat it as "do not gate"
    rather than "GPU is at 0°C" (which is impossible).
    """
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            timeout=5,
            text=True,
        )
        return int(out.strip())
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        ValueError,
        subprocess.TimeoutExpired,
    ):
        return 0


def wait_gpu_cool(temp_limit: int, poll: int = 30) -> int:
    """Block until GPU temp is at/below `temp_limit`, then return the last reading.

    If nvidia-smi is unavailable (temp 0), returns immediately without gating —
    there is nothing to gate on. Otherwise loops, sleeping `poll` seconds between
    checks, until the card cools down. Called before loading each model so a hot
    card never gets a fresh workload stacked on it.
    """
    while True:
        temp = gpu_temp()
        if temp <= 0:
            return 0
        if temp <= temp_limit:
            return temp
        print(f"  GPU {temp}°C > {temp_limit}°C, waiting {poll}s...", file=sys.stderr)
        time.sleep(poll)


def paced(
    models: list[str],
    per_model: Callable[[str], Any],
    cooldown: int = 0,
    temp_limit: int = 75,
) -> dict[str, Any]:
    """Run `per_model(model)` SEQUENTIALLY with GPU temp-gating + cooldown.

    This replaces the ThreadPoolExecutor(max_workers=4) pool that the specialized
    benches used — that parallel pool oversaturated the GPU (80°C+), ran for hours,
    and got killed. Sequential + thermal gating is the GPU-safe replacement.

    Args:
        models: candidate model names, run one at a time.
        per_model: callable(model_name) -> result (may raise; captured as {"err": ...}).
        cooldown: seconds to sleep BETWEEN models (0 = only temp-gate).
        temp_limit: block before each model until GPU is at/below this °C.

    Returns:
        {model_name: result} where a raised exception becomes {"err": str(e)}.
        Values are bench-specific (lists, dicts) — typed Any so consumers iterate
        them without narrowing noise.
    """
    results: dict[str, Any] = {}
    for i, model in enumerate(models, 1):
        wait_gpu_cool(temp_limit)
        if i > 1 and cooldown:
            time.sleep(cooldown)
        try:
            results[model] = per_model(model)
        except Exception as e:  # noqa: BLE001 - a bench must survive one bad model
            results[model] = {"err": str(e)}
        print(
            f"  [{i:2d}/{len(models)}] {model[:55]} done (GPU {gpu_temp()}°C)",
            file=sys.stderr,
            flush=True,
        )
    return results
