# Candidates Round-15 - Tiny Classification Dead End

> 2026-07-13. Goal: test a <=2 GiB resident classification layer without
> degrading routing quality. RTX 5080 16GB, Ollama 0.31.2.

## Result

**No tiny is promotable. No wiring changed.** The classification slice is now
implemented and the first empirical run rejects every candidate against the
best incumbent baseline.

## Method

1. Verified candidate tags and artifact sizes from the official Hugging Face
   model cards.
2. Pulled `LFM2.5-1.2B-Instruct Q4_K_M` (730 MB), `qwen3:0.6b` (522 MB), and
   `gemma3:1b` (815 MB).
3. Ran smoke with `--cooldown 0 --temp-limit 75`: all 3 clean, no leak.
4. Selected TeichAI Qwen3.5-9B Fable-5 as baseline after a balanced 30-case
   route preliminary: TeichAI and Qwythos both scored 1.0000; TeichAI had the
   lower median latency (0.28s vs 0.29s).
5. Ran all 48 bilingual cases (`route` + `caveman`) against TeichAI, the 3
   tinys, and installed `batiai/gemma4-e2b:q4` as E2B control.

## Full classification result

| Model | macro-F1 | accuracy | median latency | size GiB | Decision |
|---|---:|---:|---:|---:|---|
| TeichAI/Qwen3.5-9B-Fable-5 Q4_K_M | 0.9185 | 0.9167 | 0.29s | 6.098 | baseline |
| batiai/gemma4-e2b:q4 | 0.8975 | 0.8958 | 0.35s | 3.192 | REJECT |
| gemma3:1b | 0.4882 | 0.5625 | 0.35s | 0.759 | REJECT |
| LiquidAI LFM2.5-1.2B-Instruct Q4_K_M | 0.3527 | 0.3958 | 0.07s | 0.681 | REJECT |
| qwen3:0.6b | 0.1054 | 0.2500 | 0.13s | 0.487 | REJECT |

Promotion floor: macro-F1 >= 0.8985 (baseline - 0.02), >=3x latency speedup,
<=2 GiB and invalid-output rate <=40%. LFM alone reaches speed (4.14x) but
fails quality by 0.5458. E2B nearly reaches the quality floor but is 3.192 GiB
and slower than baseline.

Artifacts: `~/.cache/ollama-bench/results/classification_baselines_round15.md`
and `~/.cache/ollama-bench/results/classification_tiny_round15.md`.

## Gemma 4 E2B repository screen

All GGUF variants considered are outside the resident <=2 GiB contract:

| Repository / variant | Smallest relevant artifact | Size | Disposition |
|---|---|---:|---|
| google E2B-it QAT Q4_0 | Q4_0 GGUF | 3.35 GB | reject size |
| Huihui E2B QAT abliterated | Q4_K GGUF | 3.42 GB | reject size; unsafe role fit |
| Unsloth E2B-it | UD-IQ2_M GGUF | 2.29 GB | reject size |
| HauhauCS Aggressive | Q2_K_P GGUF | 3.01 GB | reject size; uncensored |
| LM Studio E2B-it | Q4_K_M GGUF | 3.43 GB | reject size |
| Queen E2B QAT | Q2_K GGUF | 2.99 GB | reject size |
| mistralrs-community E2B-it UQFF | Q4K UQFF | 1.54 GB | not Ollama-compatible |

`E2B` means 2.3B effective parameters but 5.1B with PLE embeddings. It is not
a 1-2GB resident model class. UQFF would require a new mistral.rs backend,
which is out of scope for an Ollama benchmark slice.

## Durable decision

- Stop the tiny cascade sequence after classification, per the acceptance rule.
- Do not implement rerank, focused_extract, escalation-gate, or a new backend
  from the failed tiny classification result.
- Remove the three failed tiny pulls; retain batiai E2B for a separate,
  validated compression role.

## E2B compression re-evaluation

`batiai/gemma4-e2b:q4` is a 4.6B Ollama model, not a <=2B tiny. A dedicated
round-15 smart-trim cross-validation produced 11.67 for batiai, 11.63 for
`cryptidbleh/gemma4-claude-opus-4.6:latest`, 10.79 for SC117 12B, and 9.87 for
Hauhau 12B. Batiai's median generation throughput was about 2.1x SC117.

Decision: do not wire E2B from this result. A single score advantage is not a
quality/fidelity promotion, and E2B's throughput is explicitly non-decisive.
Keep SC117/Hauhau as the smart-trim cascade until repeated fidelity-focused
validation proves a material, reproducible quality gain. This is not evidence
to use E2B for routing, code understanding, judging, security, or general
reasoning.

## Correction (2026-07-13 PM) — REVERTED

The "Durable decision" above was **wrong and has been reverted**. Two errors:

1. **Name-bias.** `batiai/gemma4-e2b:q4` was treated as a low-fidelity *tiny*
   because of the `e2b` suffix, but the E2B repository screen in this same
   document states it is a **4.6B** Ollama model (2.3B effective + PLE
   embeddings). It is not in the <=2B tiny class being rejected here.
2. **Circular justification.** "Throughput is explicitly non-decisive" was used
   to deny batiai-e2b a promotion — but batiai-e2b won on **score**, not
   throughput. Invoking the throughput rule to discard a quality win inverts
   the user's "quality over speed" directive (faster model penalized for being
   fast while also scoring higher).

The round-15 smart_trim cross-validation is the deciding evidence — same round,
same rubric: **batiai-e2b 11.67, cryptidbleh 11.63, SC117 10.79, Hauhau 9.87.**
Plus round-7 had batiai-e2b smart_trim #3 at 11.93. Two consistent data points
above SC117 — not the "single signal" the reversion claimed.

**Applied:** `config.py` smart_trim primary→batiai-e2b, fallback→cryptidbleh;
`RANKING.md` smart_trim table + wiring + per-task tables; `~/smart-trim`
command.py + test_summarize.py (commit 8b634be). 218/218 ollama-bench tests,
179/179 smart-trim tests, drift guard green. **codeq_sum (batiai-e4b → Qwythos
fallback) was NOT reverted** — that demotion was a genuine quality win
(9.40 > 9.19) and stays.
