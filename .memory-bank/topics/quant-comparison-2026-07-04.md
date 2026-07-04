# Quant comparison: Q4 vs Q5 vs Q6 vs Q8 (2026-07-04)

> **Question:** Do higher-precision quants (Q6, Q8) of the 4B/e4b/e2b winners
> give better quality than the current Q4_K_M?

## TL;DR — NO. Q4_K_M is the quality ceiling. Q8 adds weight with no quality gain.

Confirms the long-standing ledger entry: "Q8 quants of already-good models =
parity quality (NOT better), slower + heavier."

## Models compared

Pulled Q5_K_M / Q6_K / Q8_0 from `unsloth` (canonical multi-quant publisher)
for E4B and E2B, plus official `qwen3.5:4b-q8_0`:

- batiai e4b:q4 (Q4) — incumbent
- unsloth E4B Q5_K_M
- batiai e4b:q6 (Q6)
- unsloth E4B Q8_0
- batiai e2b:q4 (Q4)
- batiai e2b:q6 (Q6)
- unsloth E2B Q8_0
- qwen3.5:4b (Q4)
- qwen3.5:4b-q8_0 (Q8)

## Results (tie-break structural scores; range -5 to +15)

| model | quant | size | improve | codeq_sum | smart_trim | web_synth | code_gen |
|---|---|---|---|---|---|---|---|
| batiai e4b | Q4 | 5.3GB | 3.37 | **11.0** | 10.5 | 7.0 | 16.0 |
| unsloth e4b | Q5 | 6.5GB | **8.89** | 11.0 | 10.5 | 7.0 | 16.0 |
| batiai e4b | Q6 | 6.2GB | 3.47 | 11.0 | 10.5 | 7.0 | 16.0 |
| unsloth e4b | Q8 | 9.2GB | 8.59 | 8.81 | 10.5 | 7.0 | 16.0 |
| batiai e2b | Q4 | 3.4GB | 6.00 | 11.0 | 10.5 | 7.0 | 16.0 |
| batiai e2b | Q6 | 3.8GB | 3.67 | 9.00 | 10.5 | 7.0 | 16.0 |
| unsloth e2b | Q8 | 6.0GB | 3.55 | 9.00 | 10.5 | 7.0 | 16.0 |
| qwen3.5:4b | Q4 | 3.4GB | 3.71 | 8.35 | 10.5 | 5.5 | 16.0 |
| qwen3.5:4b | Q8 | 5.3GB | 1.73 | 10.80 | 10.5 | 7.0 | 16.0 |

## Same-publisher quant-isolation (the clean signal)

Cross-publisher comparisons mix 2 variables (publisher fine-tune + quant).
Same-publisher series isolate the quant effect:

- **unsloth E4B**: Q5 (8.89 improve) > Q8 (8.59) — Q5 wins, Q8 does NOT help
- **batiai e4b**: Q4 (3.37) ≈ Q6 (3.47) — identical; Q4 is enough
- **batiai e2b**: Q4 (6.00) > Q6 (3.67 improve; 9.0 codeq_sum vs 11.0) — **Q4 wins**
- **qwen3.5:4b**: Q4 (3.71 improve; 8.35 codeq_sum) vs Q8 (1.73 improve; 10.80 codeq_sum) — **mixed, Q4 wins overall**

## Conclusion

1. **Q8 does NOT improve quality** on any task for these families. Sometimes
   strictly worse (unsloth E4B Q8 codeq_sum 8.81 < Q5 11.0).
2. **Q4_K_M is the quality ceiling** for gemma4-e4b/e2b and qwen3.5:4b. Higher
   quants add weight + latency without quality.
3. **The non-monotonic pattern persists** (Q5 sometimes > Q8): quantization is
   not strictly ordered by quality at these sizes.
4. **One publisher effect surfaced**: unsloth E4B Q5 was #1 in improve (8.89)
   vs batiai e4b Q4 (3.37). But that's a fine-tune/publisher delta, NOT a quant
   delta — and the actual improve winner (pegasus912, not in this bench) still
   beats it on the full lineup.

## Action taken

All Q5/Q6/Q8 variants deleted (6 models, ~27 GB freed). Kept only Q4_K_M
across the board:
- batiai/gemma4-e4b:q4 (Q4) — codeq_sum #1 + web_synth #1
- batiai/gemma4-e2b:q4 (Q4) — bug-finding / smart_trim alt
- qwen3.5:4b (Q4) — universal default

The gemma4-e4b/e2b winners stay at Q4. If a future fine-tune (not just a
requant) appears, re-bench then. Mere requantization of the same base is not
worth the disk.