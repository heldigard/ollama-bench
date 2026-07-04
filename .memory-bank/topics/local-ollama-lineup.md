# Local Ollama Model Lineup (RTX 5080, 16GB)

> **Purpose:** Single source of truth for the LOCAL Ollama model lineup + per-role winners +
> the "do not re-pull / do not re-test" ledger.
>
> **Owner:** the benches in `~/ollama-bench/` (smoke + deep + tie-break + lfm-variant).
> **Last updated:** 2026-07-04 (54 models installed, deep-bench 40 candidates × 5 tasks; combined-rank winners).

## Current lineup — combined-rank TOP winners (2026-07-04)

Combined rank = avg of first-pass rank + tie-break rank (5 wins the day).

| model | size | role (wired) |
|---|---|---|
| `qwen3.5:4b` | 3.4GB | **UNIVERSAL DEFAULT** (DEFAULT_GEN_MODEL, smart_trim #2, code_gen #8) |
| `fredrezones55/Qwopus3.5:9b` | 6.5GB | **improve PRIMARY** (combined #1) + **smart_trim PRIMARY** (combined #1) |
| `hf.co/mradermacher/Huihui-gemma-4-12B-it-qat-q4_0-unquantized-abliterated-GGUF:Q4_K_M` | 7.2GB | improve FALLBACK (12B depth) + browser PRIMARY + diff-review PRIMARY + codeq summary FALLBACK + PDF extract |
| `hf.co/mradermacher/gemma-4-12B-Queen-it-qat-q4_0-unquantized-i1-GGUF` | 7.4GB | improve alt (combined #2) + web_synth alt (#4) |
| `batiai/gemma4-e2b:q6` | 3.8GB | **code_gen #2** + **web_synth #1** + codeq_sum alt + smart_trim alt |
| `Librellama/gemma4:e2b-Uncensored` | 3.4GB | **codeq summary PRIMARY** + codeq_sum #2 + web_synth #2 |
| `batiai/gemma4-12b:q2` | 4.5GB | codeq_sum #1 |
| `ssfdre38/gemma4-turbo:e2b` | 4.3GB | codeq_sum #4 |
| `ssfdre38/gemma4-turbo:latest` | 6.1GB | web_synth #3 + code_gen #5 |
| `cryptidbleh/gemma4-claude-opus-4.6` | 3.4GB | **code_gen #1** + codeq_sum alt + web_synth alt |
| `cryptidbleh/gemma4-claude-sonnet-4.6` | 3.4GB | code_gen #4 + smart_trim alt |
| `qwen2.5:3b` | 1.9GB | code_gen #3 |
| `jaahas/crow:9b` | 6.5GB | improve alt + code_gen alt |
| `aratan/gemma-4-E4B-it-heretic:Q6_K` | 6.2GB | smart_trim alt |
| `ducquoc/gemma4-fast-sonnet` | 3.4GB | fast small alt (86 tps) — code_gen / smart_trim |
| `xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0` | 12GB | deep code / bug-finding (recall 0.97) |
| `xentriom/...composer2.5-v2:latest` (Q4_K_M) | 7.4GB | Q4 co-load + browser FALLBACK |
| `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` | 3.4GB | smart_trim alt + improve ultralight alt |
| `nomic-embed-text` + `embeddinggemma` | 274MB+621MB | embeddings |

**REMOVED 2026-07-04:**
- ~~`MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf`~~ — Q4_0 gemma4 arch unsupported; replaced by fredrezones55/Qwopus3.5:9b + Huihui
- ~~`SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU`~~ — qwen3next MTP init fail; replaced by fredrezones55/Qwopus3.5:9b
- ~~`VladimirGav/Qwen3.6-27B-16GB-VRAM-Uncensored`~~ — leak heavy + 138s/tok; not a winner
- ~~`hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M` and 8 other LFM variants~~ — all leak thinking on Ollama 0.23.2; not codeq candidates

## Per-role winners (post 2026-07-04 combined-rank)

| role | #1 | #2 |
|---|---|---|
| codeq summary | batiai/gemma4-12b:q2 | Librellama/gemma4:e2b-Uncensored |
| improve (primary) | fredrezones55/Qwopus3.5:9b | Huihui gemma4-12B abliterated |
| diff-review / bug-finding | Huihui (12B depth) | composer Q8 |
| deep code-gen | composer Q8 | qwen3.5:4b |
| web_research synth | batiai/gemma4-e2b:q6 | Librellama/gemma4:e2b-Uncensored |
| smart_trim (primary) | qwen3.5:4b | fredrezones55/Qwopus3.5:9b |
| universal default | qwen3.5:4b | — |
| browser (vision+tool) | Huihui | composer latest |
| rerank / PII scrub | qwen3.5:4b | crow:9b |

## ⚠️ DO NOT RE-PULL / DO NOT RE-TEST ledger

Confirmed-loser installs — skip without a full leak-gated, multi-prompt-shape bench:

| family / model | failure mode |
|---|---|
| **qwopus35-v3 family** (5 variants) | 3 leak reasoning under think=False; 2 "clean" coder variants leak under complex synth prompt |
| **Reasoning-distilled Qwopus/Mythos/omnicoder** (carstenuhlig, Mythos/Claude-Fable 9B ×5, SetneufPT-9B-Coder, kwangsuklee ×3, lfm2.5:8b unclosed-think, granite3.3) | leak reasoning as plain prose OR orphan/unclosed `<think>` |
| **Q8 quants of already-good models** (lfm2.5-8b-a1b:Q8_0, qwen3.5:4b-q8_0, composer Q6_K) | parity quality, slower + heavier |
| **HauhauCS-Aggressive :9b** | verbose + `done=length` budget-burn |
| **jaahas/crow:4b** | too small for synth judgment (2/6 vs 9b 6/6) |
| **phi4, deepseek-coder-v2:16b, granite3.3:8b, qwen2.5-coder:14b** | ctx/cutoff/cleanliness dominated |
| **mythos-nano** | CoT dump regardless of size/quant |

## Bench methodology

1. **Leak gate FIRST** (reason + longctx, think=False, temp 0.2) — hard filter.
2. **Bug-finding N=3** (6-bug diff, per-bug hit matrix) — discriminator.
3. **Code-gen N=3 + MANUAL inspect** — single-shot is variance noise.
4. **Synth** (Acme fixture) — judgment role; crow:9b 6/6 is the bar.
5. Recall/keyword scores on a LEAKING model are ARTIFACTS — always read raw output + check `done_reason=length`.