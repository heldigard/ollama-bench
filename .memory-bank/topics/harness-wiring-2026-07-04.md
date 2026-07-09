# Harness Wiring — cross-CLI consumer → Ollama champion map (2026-07-08)
> Single map of which installed model each harness tool actually invokes.
> Spans 3 repos (~/smart-trim, ~/codeq, ~/prompt-improve) + ~/.claude/scripts.
> Verify against RANKING.md "Per-task PRIMARY + FALLBACK" after every re-bench.

## Tool → role → model

| tool | role | model (default; env override) | repo | status |
|---|---|---|---|---|
| prompt-improve | improve (rewrite/clarify) | `OmniCoder` (improve #1, held) → `Openclaw` → `qwen3.5:4b` (`OLLAMA_IMPROVE_MODELS`) | ~/prompt-improve | ✅ rewired 2026-07-08 PM — `config.py:31` "PM re-bench winners, OmniCoder improve #1". |
| smart-trim | PreCompact summarize | PRIMARY `HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced` (smart_trim #1 12.30/13.53). (`SMART_TRIM_PRIMARY_MODEL`) | ~/smart-trim | ✅ rewired 2026-07-08 PM — `features/summarize/command.py:28`. SetneufPT + the map's earlier `Openclaw` suggestion both superseded by HauhauCS-Balanced. |
| web-research | web_synth (final cited answer) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` (web_synth combined #1 11.85/12.83). (`OLLAMA_SYNTH_MODEL`) | ~/web-research | ✅ rewired 2026-07-08 PM — `shared/config.py:56`. DeltaCoder + crow:9b both superseded (DeltaCoder fell out of top-5). |
| web-research | query_profile / focused_extract | `cryptidbleh/gemma4-claude-opus-4.6:latest` (high-freq per-page) | same | ✅ anchor (inherits web-research `_OLLAMA_DEFAULT_MODEL`, `config.py:54`) |
| codeq | summary / context / relations | `batiai/gemma4-e4b:q4` (`CODEQ_SUMMARY_MODEL` in ~/.zshrc + `llm.py` default; commit 671d934) | ~/codeq | ✅ rewired 2026-07-08 PM — batiai codeq_sum #1 (10.24/11.20); `jaahas/crow:9b` demoted to fallback #2 (10.01/11.25). |
| diff-review | bug_finding | `zfujicute/OmniCoder-...Opus-Uncensored-v2` (bug_finding #1 15.43 AND code_gen top-5). (`OLLAMA_CODE_MODEL`) | ~/.claude/scripts/diff-review.py | ✅ rewired 2026-07-08 PM — `diff-review.py:62` "OmniCoder bug_finding #1 15.58". huihui + DeltaCoder superseded (OmniCoder overtook both). |
| project-memory | maintain (semantic-dedup + compact) | `cryptidbleh/gemma4-claude-opus-4.6:latest` (via ollama_client DEFAULT_GEN_MODEL) | ~/.claude/scripts/project-memory.py | ✅ anchor (inherits default, which is now cryptidbleh) |
| agent-browser subagent | browser PRIMARY | `functiongemma` (browser-tool #1 10.22, saturated); FALLBACK `huihui` | ~/.claude/scripts/agent_browser_subagent.py | ✅ unchanged (saturated bench) |
| pdf-extract-structured | PDF extraction | `functiongemma` (pdf_extract #2 11.96, near-saturated) + OPT-IN cloud `deepseek-v4-flash` | ~/.claude/scripts/pdf-extract-structured.py | ✅ unchanged (saturated bench) |
| pdf-ocr | rendered PDF OCR | `Unlimited-OCR` (pdf_ocr #1 12.00, 573 tok/s); FALLBACK `lift` (pdf_ocr #3 11.12) | ~/.claude/scripts/pdf-extract-structured.py | ✅ lift added as fallback |
| ollama_client | DEFAULT_GEN_MODEL | `cryptidbleh/gemma4-claude-opus-4.6:latest` (3.4GB universal fallback) | ~/.claude/scripts/ollama_client.py (shim → ~/ollama-client/ollama_client/_config.py:18) | ✅ rewired 2026-07-08 PM — qwen3.5:4b deleted from lineup, replaced by cryptidbleh (better+faster at same VRAM). |
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
