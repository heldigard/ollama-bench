"""Shared config: task registry, defaults, paths.

Single source of truth for the canonical 5 tasks the bench measures.
Adding a new task means: add to TASKS dict + write the prompts in the
appropriate feature's PROMPTS.
"""
from __future__ import annotations

import os
from pathlib import Path

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
TIMEOUT_DEFAULT = 240
NUM_PREDICT_DEFAULT = 200

# Output roots (regenerable; not git-tracked)
RESULTS_DIR = Path.home() / ".cache" / "ollama-bench" / "results"
LOGS_DIR = Path.home() / ".cache" / "ollama-bench" / "logs"

# Canonical 5 tasks (mirror harness wiring in ~/.claude/{hooks,scripts}/).
# Each feature extends these with its own per-prompt items.
TASKS: dict[str, dict] = {
    "improve": {
        "description": "prompt-improver hook — vague input → structured spec",
        "budget_words": 120,
        "primary_model_default": "fredrezones55/Qwopus3.5:9b",
    },
    "codeq_sum": {
        "description": "codeq summary — 1-line orientation of a function body",
        "budget_words": 30,
        "primary_model_default": "Librellama/gemma4:e2b-Uncensored",
    },
    "smart_trim": {
        "description": "PreCompact hook — transcript → handoff",
        "budget_words": 150,
        "primary_model_default": "qwen3.5:4b",
    },
    "web_synth": {
        "description": "web research — multi-source → 3-paragraph summary",
        "budget_words": 200,
        "primary_model_default": "batiai/gemma4-e2b:q6",
    },
    "code_gen": {
        "description": "code generation — small function with type hints",
        "budget_words": 100,
        "primary_model_default": "qwen3.5:4b",
    },
}

# Models that were incompatible with Ollama 0.23.2 but WORK on 0.31.1+.
# Kept empty as the canonical record; the incompat was the old Ollama version,
# not the models. See topics/ollama-0.23.2-gemma4-q4_0-incompat.md for history.
OLLAMA_0_23_INCOMPAT_MODELS: set[str] = set()

# Models known to leak thinking on Ollama 0.23.2 despite think=False (LFM family).
LEAKY_THINK_MODELS_SUBSTR: tuple[str, ...] = (
    "LFM2.5-8B-A1B",
    "lfm2.5-8b-a1b",
)
