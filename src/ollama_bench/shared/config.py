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
#
# primary/fallback mirror the per-task winners in RANKING.md (re-bench
# 2026-07-05, Ollama 0.31.1). They are documentary (not consumed by the bench
# runner) but MUST stay aligned with RANKING.md — the harness wires these tags
# into ~/.claude/{hooks,scripts}/. Drift here = drift in the live harness.
#
# 2026-07-08 refactor: canonical scorers replaced the saturating first-pass
# cap. These defaults mirror RANKING.md snapshot 2026-07-08.
TASKS: dict[str, dict] = {
    "improve": {
        "description": "prompt-improver hook — vague input → structured spec",
        "budget_words": 150,
        "primary_model_default": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
        "fallback_model": "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest",
    },
    "codeq_sum": {
        "description": "codeq summary — 1-line orientation of a function body",
        "budget_words": 32,
        "primary_model_default": "jaahas/crow:9b",
        "fallback_model": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
    },
    "smart_trim": {
        "description": "PreCompact hook — transcript → handoff",
        "budget_words": 170,
        "primary_model_default": "fredrezones55/Qwopus3.5:9b",
        "fallback_model": "hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M",
    },
    "web_synth": {
        "description": "web research — multi-source → 3-paragraph summary",
        "budget_words": 210,
        "primary_model_default": "aratan/gemma-4-E4B-it-heretic:Q6_K",
        "fallback_model": "cryptidbleh/gemma4-claude-opus-4.6:latest",
    },
    "code_gen": {
        "description": "code generation — small function with type hints",
        "budget_words": 120,
        "primary_model_default": "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest",
        "fallback_model": "cryptidbleh/gemma4-claude-opus-4.6:latest",
    },
}

SPECIALIZED_TASKS: dict[str, dict[str, str]] = {
    "bug_finding": {
        "primary_model_default": "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest",
        "fallback_model": "hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M",
    },
    "tool_call": {
        "primary_model_default": "hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M",
        "fallback_model": "huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K",
    },
    "browser_tool": {
        "primary_model_default": "hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M",
        "fallback_model": "huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K",
    },
    "pdf_extract": {
        "primary_model_default": "hf.co/slyfox1186/qwen3.5-9b-opus-4.6-functiongemma.gguf:Q4_K_M",
        "fallback_model": "huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K",
    },
    "pdf_ocr": {
        "primary_model_default": "hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M",
        "fallback_model": "huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K",
        "prompt": "ocr [img]",
    },
}

__all__ = [
    "LOGS_DIR",
    "NUM_PREDICT_DEFAULT",
    "OLLAMA_0_23_INCOMPAT_MODELS",
    "OLLAMA_URL",
    "RESULTS_DIR",
    "SPECIALIZED_TASKS",
    "TASKS",
    "TIMEOUT_DEFAULT",
]

# Models that were incompatible with Ollama 0.23.2 but WORK on 0.31.1+.
# Kept empty as the canonical record; the incompat was the old Ollama version,
# not the models. See topics/ollama-0.23.2-gemma4-q4_0-incompat.md for history.
OLLAMA_0_23_INCOMPAT_MODELS: set[str] = set()

# Models known to leak thinking on Ollama 0.23.2 despite think=False (LFM family).
LEAKY_THINK_MODELS_SUBSTR: tuple[str, ...] = (
    "LFM2.5-8B-A1B",
    "lfm2.5-8b-a1b",
)
