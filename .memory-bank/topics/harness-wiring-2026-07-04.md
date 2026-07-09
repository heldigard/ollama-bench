# Harness Wiring — cross-CLI consumer → Ollama champion map (2026-07-08)
> Single map of which installed model each harness tool actually invokes.
> Spans 3 repos (~/smart-trim, ~/codeq, ~/prompt-improve) + ~/.claude/scripts.
> Verify against RANKING.md "Per-task PRIMARY + FALLBACK" after every re-bench.

## Tool → role → model

| tool | role | model (default; env override) | repo | status |
|---|---|---|---|---|
| prompt-improve | improve (rewrite/clarify) | `OmniCoder` (improve #1, held) → `Negentropy-claude-opus-4.7-9B` → `SetneufPT/Qwopus3.5` → `cryptidbleh` (`OLLAMA_IMPROVE_MODELS`, `config.py:38` `_DEFAULT_IMPROVE_CHAIN`) | ~/prompt-improve | ✅ rewired 2026-07-08 PM — chain = PM winners; OmniCoder held as improve #1. |
| smart-trim | PreCompact summarize | PRIMARY `HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced` (smart_trim #1 12.30/13.53). (`SMART_TRIM_PRIMARY_MODEL`) | ~/smart-trim | ✅ rewired 2026-07-08 PM — `features/summarize/command.py:28`. SetneufPT + the map's earlier `Openclaw` suggestion both superseded by HauhauCS-Balanced. |
| web-research | web_synth (final cited answer) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` (web_synth combined #1 11.85/12.83). (`OLLAMA_SYNTH_MODEL`) | ~/web-research | ✅ rewired 2026-07-08 PM — `shared/config.py:56`. DeltaCoder + crow:9b both superseded (DeltaCoder fell out of top-5). |
| web-research | query_profile / focused_extract | `cryptidbleh/gemma4-claude-opus-4.6:latest` (high-freq per-page) | same | ✅ anchor (inherits web-research `_OLLAMA_DEFAULT_MODEL`, `config.py:54`) |
| codeq | summary / context / relations | `batiai/gemma4-e4b:q4` (`CODEQ_SUMMARY_MODEL` in ~/.zshrc + `llm.py` default; commit 671d934) | ~/codeq | ✅ rewired 2026-07-08 PM — batiai codeq_sum #1 (10.24/11.20); `jaahas/crow:9b` demoted to fallback #2 (10.01/11.25). |
| diff-review | bug_finding | `zfujicute/OmniCoder-...Opus-Uncensored-v2` (bug_finding #1 15.43 AND code_gen top-5). (`OLLAMA_CODE_MODEL`) | ~/.claude/scripts/diff-review.py | ✅ rewired 2026-07-08 PM — `diff-review.py:62` "OmniCoder bug_finding #1 15.58". huihui + DeltaCoder superseded (OmniCoder overtook both). |
| project-memory | maintain (semantic-dedup + compact) | `cryptidbleh/gemma4-claude-opus-4.6:latest` (via ollama_client DEFAULT_GEN_MODEL) | ~/.claude/scripts/project-memory.py | ✅ anchor (inherits default, which is now cryptidbleh) |
| agent-browser subagent | browser PRIMARY | `SetneufPT/Qwopus3.5-4B-Coder-MTP` (browser_tool + tool_call + pdf_extract #1); FALLBACK `huihui` | ~/.claude/scripts/agent_browser_subagent.py (shim → cli-orchestration browser/subagent.py:5) | ✅ rewired 2026-07-08 PM — functiongemma deleted from lineup, replaced by SetneufPT. |
| pdf-extract-structured | PDF extraction | `SetneufPT/Qwopus3.5-4B-Coder-MTP` (pdf_extract #1 12.07) + OPT-IN cloud `deepseek-v4-flash`; fallback chain → `cryptidbleh` | ~/.claude/scripts/pdf-extract-structured.py:40 | ✅ rewired 2026-07-08 PM — functiongemma deleted; DEFAULT_MODEL now SetneufPT (pdf_extract #1). |
| pdf-ocr | rendered PDF OCR | `Unlimited-OCR` (pdf_ocr #1 12.00, 573 tok/s); FALLBACK `lift` (pdf_ocr #3 11.12) | ~/.claude/scripts/pdf-extract-structured.py | ✅ lift added as fallback |
| ollama_client | DEFAULT_GEN_MODEL | `cryptidbleh/gemma4-claude-opus-4.6:latest` (3.4GB universal fallback) | ~/.claude/scripts/ollama_client.py (shim → ~/ollama-client/ollama_client/_config.py:18) | ✅ rewired 2026-07-08 PM — qwen3.5:4b deleted from lineup, replaced by cryptidbleh (better+faster at same VRAM). |
| ollama_client | DEFAULT_EMBED_MODEL | `embeddinggemma` (768-d) | same | ✅ MRR 1.000; bge-m3 ties |
| memory-semantic | rerank | `SetneufPT/Qwopus3.5-4B-Coder-MTP` (LLM-as-reranker; tool_call #1) | ~/.claude/scripts/memory-semantic.py (shim → agent-memory features/semantic/hybrid.py:35) | ✅ rewired 2026-07-08 PM — qwen3.5:4b deleted; RERANK_MODEL now SetneufPT. |

## Universal-anchor policy

`cryptidbleh/gemma4-claude-opus-4.6:latest` is the **fallback-of-fallbacks** across
the harness (3.4 GB, clean output, no think-leak). It replaced `qwen3.5:4b`, which
was deleted from the installed lineup on 2026-07-08 PM (cryptidbleh scored higher
and faster at the same VRAM). It is NOT a task champion but appears as the small
universal fallback / anchor in many tools because availability beats marginal
quality on the fallback path.

## Consumer rewires (2026-07-08 PM) — COMPLETE

All consumer repos were rewired to the 2026-07-08 PM RANKING winners. Note: the
intermediate AM/strip targets (Openclaw, DeltaCoder) were themselves superseded by
the PM deep+tiebreak combined results, so the final wired models differ from the
earlier PENDING suggestions. Each row in the table above reflects the model actually
wired in source today:

1. **~/prompt-improve**: `_DEFAULT_IMPROVE_CHAIN` = OmniCoder → Negentropy-9B → SetneufPT → cryptidbleh.
2. **~/smart-trim**: `SMART_TRIM_PRIMARY_MODEL` = HauhauCS/Gemma4-12B-QAT-Balanced.
3. **~/web-research**: `OLLAMA_SYNTH_MODEL` = TeichAI/Fable-5-v1; extract/profile = cryptidbleh.
4. **~/.claude/scripts/diff-review.py**: `OLLAMA_CODE_MODEL` = OmniCoder.

Source defaults in each repo match; zshrc exports must match too (see gotcha below).

## Gotcha: live env drift

After any champion rewiring, check `env | grep -E '(CODEQ_SUMMARY|SMART_TRIM|OLLAMA_SYNTH|OLLAMA_IMPROVE|OLLAMA_CODE)'`
against the source defaults — a stale live export can silently neutralize a
source fix. Relaunch CLI sessions to pick up new zshrc values.
