# Ollama 0.23.2 incompat — RESOLVED by upgrade to 0.31.1 (2026-07-04)

> **STATUS: OBSOLETE.** This was a symptom of running a stale Ollama binary.
> Root cause was NOT the models — it was a version-skew between a Windows-side
> Ollama and a WSL-side Ollama, with the WSL one stuck at 0.23.2. Unifying on a
> single WSL Ollama 0.31.1 fixed everything.

## Original symptom (Ollama 0.23.2, pre-unification)

`ollama run <model>` failed with `unknown model architecture: 'gemma4'` or
`qwen3next: layer 32 missing attn_qkv/attn_gate projections`. Re-pull did NOT
fix (blob was fine; the binary didn't recognize the arch).

## Affected models — ALL WORK on 0.31.1+

| model | 0.23.2 status | 0.31.1 status |
|---|---|---|
| `MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf` | DEAD | loads ✓ (but ranks low → deleted in re-bench) |
| `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` | DEAD | loads ✓ → **smart_trim #1 winner** |
| `hf.co/google/gemma-4-12B-it-qat-q4_0-gguf` | DEAD | loads ✓ (deleted, outperformed) |
| All gemma4 Q4_0 variants | DEAD/fragile | load ✓ |
| qwen3next MTP models | DEAD | load ✓ |

## Real LFM issue (NOT Ollama-version-related)

`hf.co/LiquidAI/LFM2.5-8B-A1B-*` and the 8 sibling variants leak `<think>`
content into the response field despite `think: false`. This persists on
0.23.2 AND 0.31.1 — it is **model-inherent** (the fine-tune baked thinking
into the response channel). Re-pulling or upgrading Ollama does NOT fix.
**All 9 LFM variants deleted.** Not candidates for any task.

## Lesson

Before declaring a model "DEAD", verify the Ollama version. `ollama --version`
should be ≥ 0.31.x for full gemma4 + qwen3next support. A single
unified-server Ollama beats two version-skewed servers (Windows + WSL).

## Detection in ollama-bench

`shared/config.py::OLLAMA_0_23_INCOMPAT_MODELS` is now empty (the incompat was
the binary, not the models). `ollama-bench list` flags LFM family via
`LEAKY_THINK_MODELS_SUBSTR` (still relevant — those leak on every version).