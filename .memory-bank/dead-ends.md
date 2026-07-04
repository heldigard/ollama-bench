# Dead Ends
> Failed approaches — keep as regression history

## 2026-07-04 — LFM2.5-8B-A1B as codeq summary PRIMARY

- Tried: configure `CODEQ_SUMMARY_MODEL=LFM2.5-8B-A1B-GGUF:Q4_K_M` in zshrc.
- Failed: leaks thinking despite `think=False`. The thinking fills the response field; model hits `done=length` BEFORE emitting the real answer.
- Worked instead: switched to `Librellama/gemma4:e2b-Uncensored` (3.4GB, gemma4 e2b distilled, fast).

## 2026-07-04 — Mobius as improve PRIMARY on Ollama 0.23.2

- Tried: `ollama run MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf` — fails with `unknown model architecture: 'gemma4'`.
- Re-pull doesn't help (blob not corrupt; Ollama version doesn't recognize gemma4 Q4_0 GGUF).
- Worked instead: `Huihui gemma4-12B abliterated` (Q4_K_M quant, same base model, loads correctly).

## 2026-07-04 — SetneufPT/Qwopus3.5-4B-Coder-MTP as longctx champ

- Tried: `ollama run SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU` — fails with `qwen3next: layer 32 missing attn_qkv/attn_gate projections`.
- Re-pull doesn't help (Ollama version doesn't recognize qwen3next MTP layers).
- Worked instead: `fredrezones55/Qwopus3.5:9b` (same qwen3.5 family, no MTP, loads correctly).

## 2026-07-04 — First-pass score as final ranking

- Tried: rank models using `first_pass_score` directly.
- Failed: 20+ models tie at 7.0 (saturation cap). Cannot distinguish "excellent" from "good enough".
- Worked instead: re-bench tied candidates with `tie_break_score` (no cap, harder prompts, structural scoring).

## 2026-07-04 — `think` inside Ollama `options`

- Tried: put `"think": false` inside the request's `options` dict.
- Failed: silently ignored. qwen3.x and gemma4 still emit thinking trace in response.
- Worked instead: put `think` at TOP LEVEL of the request body. `CallOpts.think` is enforced at this level by `shared/ollama.call()`.