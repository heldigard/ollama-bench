# current-models-strip-2026-07-08
> Deep memory topic. Read on demand; keep entries factual.


## 2026-07-08T02:57:20Z
# Current Models Strip Rebench — 2026-07-08

Scope: user requested current Qwen3.5+/Gemma4 customization candidates, with recoverable reasoning leaks treated via strip instead of automatic drop.

Installed/bench candidates added this round:
- hf.co/Jackrong/Negentropy-claude-opus-4.7-4B-GGUF:Q4_K_M
- hf.co/Jackrong/Negentropy-claude-opus-4.7-9B-GGUF:Q4_K_M
- hf.co/danielcherubini/Qwen3.5-DeltaCoder-9B-GGUF:Q4_K_M
- hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M
- hf.co/Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash-GGUF:Q4_K_M
- hf.co/yuxinlu1/gemma-4-12B-it-Claude-4.6-4.8-Opus-GGUF:Q4_K_M

Smoke: 13/14 clean. DeepSeek-V4-Flash emitted thinking_process but smoke marked strippable=1, so it was included in deep --strip instead of dropped.

Deep --strip artifact committed: results_current_models_strip_deep_20260708.md. TSV/JSONL were generated locally then removed as root noise.

Top deep results by task:
- improve: zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest (7.01), then Negentropy 9B (6.46).
- codeq_sum: jaahas/crow:9b (9.57), then SetneufPT/Qwopus3.5-4B-Coder-MTP (9.15).
- smart_trim: ykarout/Openclaw Qwen3.5 9B (11.53), then functiongemma (11.33).
- web_synth: DeltaCoder 9B and aratan/gemma-4-E4B tied at 12.50; needs tie-break before rewiring.
- code_gen: Openclaw Qwen3.5 9B and OmniCoder tied at 11.65; needs tie-break/specialized code bench before rewiring.

Decision: no downstream config rewire from this deep result alone. Run tool-call, browser-tool, bug-finding, pdf-extract, and pdf-ocr (Unlimited-OCR + LIFT) before changing consumers.

## 2026-07-08T03:00:32Z
## Tool-call follow-up

A concurrent tool-call benchmark finished after the deep run and produced results_current_models_tool_call_20260708.md.

Top tool-call results:
- hf.co/ykarout/Qwen3.5-9b-Opus-Openclaw-Distilled-GGUF:Q4_K_M: 10.36 (#1)
- functiongemma, huihui, DeltaCoder, Negentropy 9B, crow, and SetneufPT clustered at 10.34
- DeepSeek-V4-Flash scored 8.35 despite strip-required handling, so do not promote it for tool-call.

Decision update: tool-call supports Openclaw as a strong candidate, but the 0.02 lead over the 10.34 cluster is too small to rewire consumers by itself. PDF/OCR, browser-tool, and bug-finding remain pending before broad config updates.

## 2026-07-08T03:03:55Z
## PDF follow-up

PDF-OCR rendered-page benchmark produced results_current_models_pdf_ocr_20260708.md:
- Unlimited OCR remains #1: 12.00 score, 1.00 avg recall, fastest by a wide margin.
- LIFT scored #3: 11.12, 1.00 avg recall; useful OCR fallback but slower than Unlimited OCR and slightly behind huihui in this run.
- Several text-only/code models returned zero OCR recall/hallucination failures and should not be used for rendered PDF OCR.

PDF-extract structured benchmark produced results_current_models_pdf_extract_20260708.md:
- Openclaw Qwen3.5 9B ranked #1 at 12.05.
- functiongemma, OmniCoder, and crow clustered at 11.96; margin is small.

Decision update: keep Unlimited OCR as pdf_ocr primary. Openclaw is a strong pdf_extract candidate but needs consumer compatibility review before replacing existing functiongemma wiring because the margin is 0.09 and existing configs may value stability.

## 2026-07-08T03:06:52Z
## Bug-finding follow-up

Bug-finding benchmark produced results_current_models_bug_finding_20260708.md:
- DeltaCoder 9B ranked #1 at 14.06.
- OmniCoder ranked #2 at 14.04.
- HauhauCS Gemma4 ranked #3 at 14.02.
- The top three are within 0.04, so treat this as a near-tie; do not rewire diff-review/bug-finding consumers without tie-break or stability run.
