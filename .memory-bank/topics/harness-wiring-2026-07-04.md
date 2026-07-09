# Harness Wiring — cross-CLI consumer → Ollama champion map (2026-07-08)
> Single map of which installed model each harness tool actually invokes.
> Spans 3 repos (~/smart-trim, ~/codeq, ~/prompt-improve) + ~/.claude/scripts.
> Verify against RANKING.md "Per-task PRIMARY + FALLBACK" after every re-bench.

## Tool → role → model

| tool | role | model (default; env override) | repo | status |
|---|---|---|---|---|
| prompt-improve | improve (rewrite/clarify) | **→ NEEDS REWIRE**: `OmniCoder` (improve #1 7.01) replaces Grug-12B. Chain: `OmniCoder` → `Openclaw` → `qwen3.5:4b` (`OLLAMA_IMPROVE_MODELS`) | ~/prompt-improve | ⚠️ **PENDING 2026-07-08** — Grug-12B no longer #1. OmniCoder +0.41 over old. |
| smart-trim | PreCompact summarize | **→ NEEDS REWIRE**: PRIMARY `Openclaw` (smart_trim #1 11.53) replaces SetneufPT. (`SMART_TRIM_PRIMARY_MODEL`) | ~/smart-trim | ⚠️ **PENDING 2026-07-08** — SetneufPT dropped to #13 in new bench. |
| web-research | web_synth (final cited answer) | **→ NEEDS REWIRE**: `DeltaCoder` (web_synth #1 12.50 tied) replaces crow:9b. (`OLLAMA_SYNTH_MODEL`) | ~/web-research | ⚠️ **PENDING 2026-07-08** — DeltaCoder ties aratan; crow:9b no longer #1 web_synth. |
| web-research | query_profile / focused_extract | `qwen3.5:4b` (high-freq per-page) | same | ✅ anchor |
| codeq | summary / context / relations | `batiai/gemma4-e4b:q4` (`CODEQ_SUMMARY_MODEL` in ~/.zshrc + `llm.py` default; commit 671d934) | ~/codeq | ✅ rewired 2026-07-08 PM — batiai codeq_sum #1 (10.24/11.20); `jaahas/crow:9b` demoted to fallback #2 (10.01/11.25). |
| diff-review | bug_finding | **→ NEEDS REWIRE**: `DeltaCoder` (bug_finding #1 14.06) replaces huihui. (`OLLAMA_CODE_MODEL`) | ~/.claude/scripts/diff-review.py | ⚠️ **PENDING 2026-07-08** — DeltaCoder overtakes huihui. |
| project-memory | maintain (semantic-dedup + compact) | `qwen3.5:4b` (via ollama_client DEFAULT_GEN_MODEL) | ~/.claude/scripts/project-memory.py | ✅ anchor |
| agent-browser subagent | browser PRIMARY | `functiongemma` (browser-tool #1 10.22, saturated); FALLBACK `huihui` | ~/.claude/scripts/agent_browser_subagent.py | ✅ unchanged (saturated bench) |
| pdf-extract-structured | PDF extraction | `functiongemma` (pdf_extract #2 11.96, near-saturated) + OPT-IN cloud `deepseek-v4-flash` | ~/.claude/scripts/pdf-extract-structured.py | ✅ unchanged (saturated bench) |
| pdf-ocr | rendered PDF OCR | `Unlimited-OCR` (pdf_ocr #1 12.00, 573 tok/s); FALLBACK `lift` (pdf_ocr #3 11.12) | ~/.claude/scripts/pdf-extract-structured.py | ✅ lift added as fallback |
| ollama_client | DEFAULT_GEN_MODEL | `qwen3.5:4b` | ~/.claude/scripts/ollama_client.py | ✅ anchor |
| ollama_client | DEFAULT_EMBED_MODEL | `embeddinggemma` (768-d) | same | ✅ MRR 1.000; bge-m3 ties |
| memory-semantic | rerank | `qwen3.5:4b` | ~/.claude/scripts/memory-semantic.py | ✅ anchor |

## Universal-anchor policy

`qwen3.5:4b` is the **fallback-of-fallbacks** across the harness: always installed
(3.4 GB, clean output, no think-leak). It is NOT a task champion but appears as
SECONDARY/anchor in many tools because availability beats marginal quality on the
fallback path.

## Pending consumer rewires (2026-07-08)

These repos need their default model configs updated to match RANKING.md 2026-07-08:

1. **~/prompt-improve**: `_DEFAULT_IMPROVE_CHAIN` → prepend OmniCoder, append Openclaw
2. **~/smart-trim**: `SMART_TRIM_PRIMARY_MODEL` → Openclaw
3. **~/web-research**: `OLLAMA_SYNTH_MODEL` → DeltaCoder
4. **~/.claude/scripts/diff-review.py**: `OLLAMA_CODE_MODEL` → DeltaCoder

Source defaults in each repo must change; zshrc exports must match.

## Gotcha: live env drift

After any champion rewiring, check `env | grep -E '(CODEQ_SUMMARY|SMART_TRIM|OLLAMA_SYNTH|OLLAMA_IMPROVE|OLLAMA_CODE)'`
against the source defaults — a stale live export can silently neutralize a
source fix. Relaunch CLI sessions to pick up new zshrc values.
