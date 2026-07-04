# Harness Wiring — cross-CLI consumer → Ollama champion map (2026-07-04)
> Single map of which installed model each harness tool actually invokes.
> Spans 3 repos (~/smart-trim, ~/codeq, ~/prompt-improve) + ~/.claude/scripts.
> Verify against RANKING.md "Per-task PRIMARY + FALLBACK" after every re-bench.

## Tool → role → model

| tool | role | model (default; env override) | repo | status |
|---|---|---|---|---|
| prompt-improve | improve (rewrite/clarify) | `pegasus912` → `Librellama/gemma4:e2b` → `qwen3.5:4b` (`OLLAMA_IMPROVE_MODELS`) | ~/prompt-improve | ✅ aligned (improve #1, #2) |
| smart-trim | PreCompact summarize | PRIMARY `SetneufPT/Qwopus3.5-4B-Coder-MTP`, SECONDARY `qwen3.5:4b` (`SMART_TRIM_PRIMARY_MODEL` / `_SECONDARY_MODEL`) | ~/smart-trim | ✅ aligned (smart_trim #1) — **swapped 2026-07-04, was backwards** |
| web-research | web_synth (final cited answer) | `batiai/gemma4-e4b:q4` (`OLLAMA_SYNTH_MODEL`); general `qwen3.5:4b` (`OLLAMA_MODEL`); cloud `deepseek-v4-flash` | ~/.claude/scripts/web_research | ✅ aligned (web_synth #1) |
| web-research | query_profile / focused_extract | `qwen3.5:4b` (high-freq per-page) | same | ✅ anchor |
| codeq | summary / context / relations | `batiai/gemma4-e4b:q4` (`CODEQ_SUMMARY_MODEL`) | ~/codeq | ✅ source aligned (codeq_sum #1) |
| diff-review | bug_finding | `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` (`OLLAMA_CODE_MODEL`) | ~/.claude/scripts/diff-review.py | ✅ aligned (bug_finding #1, 17.98) |
| project-memory | maintain (semantic-dedup + compact) | `batiai/gemma4-e4b:q4` | ~/.claude/scripts/project-memory.py | ✅ aligned (codeq_sum/web_synth #1) |
| agent-browser subagent | browser PRIMARY | PRIMARY `functiongemma` (browser-tool #1 10.19 + tool_call #1 9.85); FALLBACK `pegasus912` (browser #5 9.70, gemma4 family diversity) | ~/.claude/scripts/agent_browser_subagent.py | ✅ benched (browser-tool slice 2026-07-04; pegasus912 proxy retired — was only #5) |
| pdf-extract-structured | PDF extraction | `pegasus912` (pdf_extract tied #1 11.14; field saturated within 0.03) + OPT-IN cloud escape `deepseek-v4-flash` (`PDF_EXTRACT_CLOUD_FALLBACK=1`) | ~/.claude/scripts/pdf-extract-structured.py | ✅ benched (slice 2026-07-04; proxy confirmed sound, caveat retired) |
| ollama_client | DEFAULT_GEN_MODEL (universal anchor) | `qwen3.5:4b` | ~/.claude/scripts/ollama_client.py | ✅ anchor (always installed) |
| ollama_client | DEFAULT_EMBED_MODEL | `embeddinggemma` (768-d) | same | ✅ MRR 0.724; bge-m3 ties, kept as alt |
| memory-semantic | rerank (LLM-as-reranker) | `qwen3.5:4b` | ~/.claude/scripts/memory-semantic.py | ✅ anchor |

## Universal-anchor policy

`qwen3.5:4b` is the **fallback-of-fallbacks** across the harness: always installed
(3.4 GB, 81 tok/s, clean output, no think-leak). It is NOT a task champion
(smart_trim #14, web_synth off-top-5) but appears as SECONDARY/anchor in many
tools because availability beats marginal quality on the fallback path. Task
champions (pegasus912, SetneufPT, batiai, huihui) run PRIMARY; qwen3.5:4b catches
the case where a champion tag is missing.

## Gotcha: live env drift (CODEQ_SUMMARY_MODEL)

**Symptom**: `codeq summary <fn>` prints
`[ollama summary unavailable: Ollama call failed: OllamaRequestError]` — LLM
enrichment silently disabled, body still prints.

**Root cause**: the live Claude Code session inherited a stale
`CODEQ_SUMMARY_MODEL=hf.co/LiquidAI/LFM2.5-8B-A1B-GGUF:Q4_K_M` from before the
2026-07-04 batiai fix. LFM2.5 was culled (think-leak family), so the call 404s.
The source default (~/codeq/.../llm.py) AND `~/.zshrc:1137` are both correct
(`batiai/gemma4-e4b:q4`), but Claude Code does not re-source zshrc, so the stale
export wins for every codeq subprocess in the session.

**Fix**: relaunch Claude Code (fresh shell picks up zshrc). Not a code bug —
source + zshrc are already correct. Confirmed: `CODEQ_SUMMARY_MODEL=batiai/... codeq summary ...`
works (10.6 s cold, cache warm).

**Generalize**: after any champion rewiring, check `env | grep -E '(CODEQ_SUMMARY|SMART_TRIM|OLLAMA_SYNTH|OLLAMA_IMPROVE|OLLAMA_CODE)'`
against the source defaults — a stale live export can silently neutralize a
source fix. GLM PATH-persistence gotcha (rules/model-specific.md) applies.

## Commits (2026-07-04T21:51Z)

- `smart-trim b74762b` — swap PRIMARY/SECONDARY to SetneufPT (smart_trim #1) + labels/tests.
- `codeq 3fee248` — default + `--summary` help → batiai/gemma4-e4b:q4.
- `~/.claude adaafa6` — wire champions into diff-review/project-memory/agent_browser/pdf/web_research (Mobius→campeones).

## Slices still missing (proxy choices above)

`agent_browser` + `pdf-extract` use pegasus912 as a *proxy* (improve #1) because
no bench slice measures browser-tool dispatch or PDF extraction. Add slices
(roadmap: `browser_tool`, `pdf_extract`) to retire the guess — same pattern as
`tool_call` (functiongemma #1) and `embedding_retrieval` (embeddinggemma #1).
