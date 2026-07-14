# Harness Wiring — cross-CLI consumer → Ollama champion map (2026-07-08)
> Single map of which installed model each harness tool actually invokes.
> Spans 3 repos (~/smart-trim, ~/codeq, ~/prompt-improve) + ~/.claude/scripts.
> Verify against RANKING.md "Per-task PRIMARY + FALLBACK" after every re-bench.

## Tool → role → model

| tool | role | model (default; env override) | repo | status |
|---|---|---|---|---|
| prompt-improve | improve (rewrite/clarify) | **`cryptidbleh/gemma4-claude-opus-4.6`** (improve #1 fresh 5-way 2.97) → `TeichAI/Fable-5-v1` (round-10 champion demoted, 2.46) → `Negentropy-claude-opus-4.7-9B` → `SetneufPT/Qwopus3.5-4B-Coder-MTP` (`OLLAMA_IMPROVE_MODELS`, `config.py:67` `_DEFAULT_IMPROVE_CHAIN`) | ~/prompt-improve | ✅ **rewired 2026-07-13 round-17** — cryptidbleh dethroned TeichAI in fresh 5-way deep (2.97 vs 2.46, +0.51). Round-10 blind spot: cryptidbleh was chain tail (legacy 2026-07-09 #1, smart_trim round-15 #2) but NOT in round-10 4-way, so its strength was never re-validated. |
| smart-trim | PreCompact summarize | PRIMARY **`hf.co/SC117/gemma-4-12B-it-heretic-QAT-GGUF:UD-Q4_K_XL`** → **`hf.co/HauhauCS/Gemma4-12B-QAT-Uncensored-HauhauCS-Balanced:Q4_K_M`**. (`SMART_TRIM_PRIMARY_MODEL`) | ~/smart-trim | ✅ quality-first incumbent. Round-15 E2B is an unreplicated candidate; throughput cannot displace fidelity. `features/summarize/command.py:27`. |
| web-research | web_synth (final cited answer) | `hf.co/TeichAI/Qwen3.5-9B-Fable-5-v1-GGUF:Q4_K_M` (web_synth combined #1 11.85/12.83). (`OLLAMA_SYNTH_MODEL`) | ~/web-research | ✅ rewired 2026-07-08 PM — `shared/config.py:56`. TeichAI held improve #2 after round-17 dethrone; still dual-role web_synth champion. |
| web-research | query_profile / focused_extract | `cryptidbleh/gemma4-claude-opus-4.6:latest` (high-freq per-page) | same | ✅ anchor (inherits web-research `_OLLAMA_DEFAULT_MODEL`, `config.py:54`) |
| codeq | summary / context / relations | **`hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M`** (`CODEQ_SUMMARY_MODEL` in ~/.zshrc + `llm.py` default) | ~/codeq | ✅ **rewired 2026-07-12 round-9** — Qwythos dethroned batiai codeq_sum #1 (9.40 vs 9.19, +2.3%); batiai demoted to fallback. See `topics/candidates-round-9-2026-07-12.md`. |
| diff-review | bug_finding | **`xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:Q8_0`** (bug_finding #1 14.97 5-way round-10). (`OLLAMA_CODE_MODEL`) | ~/.claude/scripts/diff-review.py | ✅ **rewired 2026-07-12 round-10** — xentriom Q8_0 dethroned OmniCoder in 5-way specialized bench (14.97 vs 14.49, +0.48). Cross-task promotion: web_synth champion also wins bug_finding. WARNING: Q8_0 = 12GB; override `OLLAMA_CODE_MODEL=OmniCoder` for low-VRAM contexts. |
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

## Round-9 rewire delta (2026-07-12)

ONE row updated: `codeq` → Qwythos primary (was batiai). `~/.zshrc:1134`
`CODEQ_SUMMARY_MODEL` rewired in same atomic edit. All other rows HELD — no
move at the top-5 level for improve / smart_trim / web_synth / code_gen /
bug_finding / tool_call / pdf_extract / pdf_ocr.

Qwythos did not displace any consumer champion — but came within striking
distance on code_gen (10.38 vs lift 10.52, -1.3% on hard prompts). Not promoted
there; recorded as "watch" for round-10.

## Round-10 rewire delta (2026-07-12) — **MAJOR**

3 PRIMARY changes via cross-task 4-way validation:

| row | OLD | NEW | source of upset |
|---|---|---|---|
| prompt-improve | OmniCoder | **TeichAI/Fable-5-v1** (web_synth champion crossed-task) | 2.46 vs 0.93 in 4-way deep |
| smart-trim | HauhauCS-Balanced | **SC117/heretic-QAT** (smart_trim #2 fallback promoted) | 10.79 vs 9.87 in 4-way deep |
| diff-review (`OLLAMA_CODE_MODEL`) | OmniCoder | **xentriom Q8_0** (web_synth champion crossed-task) | 14.97 vs 14.49 in 5-way specialized |

Plus ONE fallback swap: pdf_extract #2 → OmniCoder (12.00 vs ykarout/Openclaw 11.97).

Pattern: stale round-7 champions were never challenged by other-task champions.
Cross-task validation dethroned 3 specialists with broad generalists. The
"broad generalist" winners (TeichAI, xentriom) won multiple roles; the
"specialist" losers (OmniCoder, HauhauCS) lost to siblings in same family.

**Action items for downstream consumers:**
1. ✅ Update `~/prompt-improve/_DEFAULT_IMPROVE_CHAIN` to put TeichAI first. **DONE 2026-07-12 PM** (TeichAI primary, Negentropy-9B fallback, SetneufPT, cryptidbleh). Tests: 192/192 pass.
2. ✅ Update `~/smart-trim/features/summarize/command.py:28` to use SC117/heretic-QAT as PRIMARY. **DONE 2026-07-12 PM** (SC117 primary, HauhauCS-Balanced secondary). Tests: 170/170 pass.
3. ✅ `~/.claude/scripts/diff-review.py` already rewired to xentriom Q8_0. **DONE 2026-07-12 PM**.
4. `OLLAMA_CODE_MODEL=OmniCoder` env override available for low-VRAM contexts (xentriom Q8_0 = 12GB).

## Gotcha: live env drift

After any champion rewiring, check `env | grep -E '(CODEQ_SUMMARY|SMART_TRIM|OLLAMA_SYNTH|OLLAMA_IMPROVE|OLLAMA_CODE)'`
against the source defaults — a stale live export can silently neutralize a
source fix. Relaunch CLI sessions to pick up new zshrc values.
