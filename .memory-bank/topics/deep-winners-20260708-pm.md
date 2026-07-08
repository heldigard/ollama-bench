# Deep winners — 2026-07-08 PM run (deep pass, pending combined)
> Status: deep + tie-break done; specialized benches running. NOT yet rewired into config.py/RANKING.md.

## Deep-pass #1 today vs config.py primaries (prior bench)

| Task | Prior #1 (config) | Today #1 (deep) | Score | Δ |
|---|---|---|---|---|
| improve | zfujicute/OmniCoder | OmniCoder | 7.74 | ✅ held |
| codeq_sum | jaahas/crow:9b | batiai/gemma4-e4b:q4 | 10.24 | ⚠️ crow → #4 |
| smart_trim | ykarout/Openclaw | HauhauCS/Gemma4-12B-QAT-Uncensored-Balanced | 12.3 | ⚠️ Openclaw → #2 |
| web_synth | danielcherubini/DeltaCoder | SC117/gemma-4-12B-it-heretic-QAT (UD-Q4_K_XL) | 12.27 | ⚠️ DeltaCoder OUT of top-5 |
| code_gen | ykarout/Openclaw | prithivMLmods/lift-GGUF | 12.13 | ⚠️ Openclaw OUT of top-5 |

## Notable shifts
- **Openclaw** (was smart_trim + code_gen #1) and **DeltaCoder** (was web_synth + bug_finding #1) both FELL OUT of top-5. Big reshuffle.
- New strong: SC117/heretic-QAT (web_synth), prithiv/lift (code_gen), HauhauCS-Balanced (smart_trim), batiai/gemma4-e4b (codeq_sum).
- Root cause: new hf.co candidate set installed ~9h before this run (StyleTune, heretic, Fable-5-v1, Negentropy, DeltaCoder, etc.) reshuffled the field.
- Discrimination healthy: 22-27 unique scores per task, max tie group 3 → scoring saturates less than prior runs.

## Caveats — DO NOT rewire config yet
- This is the DEEP pass only. Final ranking = deep + tie-break (hard prompts) combined, per [[bench-methodology]].
- Specialized benches (bug_finding, tool_call, pdf_extract, pdf_ocr) still running — their winners pending.
- bug_finding prior #1 was DeltaCoder (now weakened in deep) — may change.
- Rewire config.py TASKS primary/fallback + RANKING.md ONLY after the full pipeline completes and the combined ranking is computed.

## Run artifacts (this session)
- deep: `~/.cache/ollama-bench/results/deep_bench_strip.{tsv,md,_details.jsonl}`
- tie-break: `tiebreak_ranking.{md,_details.jsonl}`
- Baseline (prior, for diff): `deep_refactor_20260708.*` + `*_refactor_20260708.md`
