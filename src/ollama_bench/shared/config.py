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
        "primary_model_default": "cryptidbleh/gemma4-claude-opus-4.6:latest",  # round-17 2026-07-13: dethroned round-10 champion TeichAI in fresh 5-way (2.97 vs 2.46, +0.51). Round-10's blind spot: cryptidbleh was chain tail (legacy 2026-07-09 #1, smart_trim round-15 #2) but NOT in round-10 4-way.
        "fallback_model": "hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M",  # round-10 champion demoted to fallback after round-17 dethrone.
        "protocol": "chat-fallback",
    },
    "codeq_sum": {
        "description": "codeq summary — 1-line orientation of a function body",
        "budget_words": 32,
        "primary_model_default": "hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M",  # round-9 2026-07-12: dethroned batiai/gemma4-e4b:q4 (9.40 vs 9.19, +2.3% on hard prompts)
        "fallback_model": "batiai/gemma4-e4b:q4",
        "tertiary_model": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
        "protocol": "generate",
    },
    "smart_trim": {
        "description": "PreCompact hook — transcript → handoff",
        "budget_words": 170,
        "primary_model_default": "batiai/gemma4-e2b:q4",  # round-15 2026-07-13 cross-validation: smart_trim #1 (11.67). Quality governs, not throughput — name-bias ('e2b') had wrongly demoted it; Ollama reports 4.6B, not a tiny. Consistent with round-7 #3 (11.93).
        "fallback_model": "cryptidbleh/gemma4-claude-opus-4.6:latest",  # round-15 smart_trim #2 (11.63), fidelity runner-up.
        "protocol": "chat-fallback",
    },
    "web_synth": {
        "description": "web research — multi-source → 3-paragraph summary",
        "budget_words": 210,
        "primary_model_default": "hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M",
        "fallback_model": "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0",
        "protocol": "generate",
    },
    "code_gen": {
        "description": "code generation — small function with type hints",
        "budget_words": 120,
        "primary_model_default": "hf.co/prithivMLmods/lift-GGUF:Q4_K_M",
        "fallback_model": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
        "protocol": "generate",
    },
}

SPECIALIZED_TASKS: dict[str, dict[str, str]] = {
    "bug_finding": {
        "primary_model_default": "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0",  # round-10 2026-07-12: dethroned OmniCoder (14.97 vs 14.49 in 5-way deep, +0.48). Cross-task promotion: web_synth champ also beats bug_finding champ. WARNING: Q8_0 = 12GB; OmniCoder fallback for VRAM-tight contexts.
        "fallback_model": "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest",
    },
    "tool_call": {
        "primary_model_default": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
        "fallback_model": "hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M",
    },
    "browser_tool": {
        "primary_model_default": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
        "fallback_model": "hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M",
    },
    "pdf_extract": {
        "primary_model_default": "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest",
        "fallback_model": "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest",  # round-10 2026-07-12: 12.00 vs ykarout/Openclaw 11.97 (+0.03), already-installed, multi-role coverage.
    },
    "pdf_ocr": {
        "primary_model_default": "hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M",
        "fallback_model": "hf.co/prithivMLmods/lift-GGUF:Q4_K_M",
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
