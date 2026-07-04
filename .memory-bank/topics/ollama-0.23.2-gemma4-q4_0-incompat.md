# Ollama 0.23.2 — gemma4 Q4_0 + qwen3next MTP incompat (2026-07-04)

## Symptom

`ollama run <model>` fails with:
```
unable to load model: /home/eldi/.ollama/models/blobs/sha256-XXX
```

Log detail:
```
llama_model_load: error loading model: error loading model architecture: unknown model architecture: 'gemma4'
# OR
failed to initialize model: qwen3next: layer 32 missing attn_qkv/attn_gate projections
```

The blob exists on disk and is not corrupt (sha256 matches, file size OK). Re-pulling the same digest does NOT fix it.

## Affected models (Ollama 0.23.2 confirmed broken)

| model | error | originally role |
|---|---|---|
| `MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf` | unknown gemma4 arch (Q4_0 quant) | improve PRIMARY + diff-review + browser |
| `SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` | qwen3next MTP layer init fail | longctx/reason champ + smart-trim alt |
| `hf.co/google/gemma-4-12B-it-qat-q4_0-gguf` | same Q4_0 arch issue | official gemma4 12B Q4_0 |
| `hf.co/lmstudio-community/gemma-4-12B-it-QAT-GGUF:Q4_0` | same | alt gemma4 12B Q4_0 |
| (all `hf.co/...` gemma4-12B Q4_0 variants) | same | various |

## Working replacements (same base, different quant)

- `Mobius` (gemma-4-12B-it-qat-q4_0) → `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` (same base, **Q4_K_M quant works**)
- `SetneufPT/Qwopus3.5-4B-Coder-MTP` → `fredrezones55/Qwopus3.5:9b` (same qwen3.5 family, **no MTP**)
- For codeq summary: `Librellama/gemma4:e2b-Uncensored` (gemma4 e2b distilled, 3.4GB, no leaks)

## Fix options

1. **Upgrade Ollama** to a version that supports gemma4 Q4_0 + qwen3next MTP — required if user wants to restore Mobius/SetneufPT specifically.
2. **Use the working replacements** above (no Ollama change needed).

## Detection rule (in ollama-bench)

`ollama-bench list` flags models in `OLLAMA_0_23_INCOMPAT_MODELS` (shared/config.py) with `[WARN: OLLAMA_0_23_INCOMPAT]`.

## Why: Why this matters

- The 2026-06-28 local-model summary winner was Mobius for codeq summary — that file is now permanently incompatible until Ollama upgrade.
- All `OLLAMA_IMPROVE_WARM_MODEL`, `CODEQ_SUMMARY_MODEL`, `CODE_MODEL` (diff-review), `PDF_EXTRACT_MODEL`, browser PRIMARY defaults had to switch in the 2026-07-04 sweep.

## How to apply

- Before declaring a model "DEAD", verify the error is real and not stale Ollama cache. Restart `ollama serve` once; if still fails, log as DEAD.
- After Ollama upgrades, re-test Mobius/SetneufPT — they may come back.
- For NEW model pulls: prefer Q4_K_M over Q4_0 for gemma4 family until Ollama version stabilizes.