# Topic Index
> Deep project memory. Search/read on demand; do not load all topics by default.

## Architecture / methodology
- [bench-methodology](bench-methodology.md) — smoke → deep → tie-break → bug-finding pipeline (+ `--strip` think-strip, 14 leak patterns)
- [local-ollama-lineup](local-ollama-lineup.md) — 21 LLM winners + per-role map (re-bench 2026-07-05 round-3 + 4; re-installed batiai/gemma4-e2b:q4 missing winner)
- [harness-wiring-2026-07-04](harness-wiring-2026-07-04.md) — cross-CLI consumer → champion map (smart-trim/codeq/web-research/diff-review/etc.) + live-env drift gotcha

## Bench iterations (2026-07-04)
- [new-benchmarks-roadmap-2026-07-04](new-benchmarks-roadmap-2026-07-04.md) — 8 new bench dimensions → cross-CLI consumers (tool_call + embedding_retrieval landed)
- [new-models-bench-2026-07-04](new-models-bench-2026-07-04.md) — HF candidates benched; huihui = bug_finding #1 (17.98)
- [quant-comparison-2026-07-04](quant-comparison-2026-07-04.md) — Q4 vs Q5/Q6/Q8 evidence (Q4 is the ceiling)

## Bench iterations (2026-07-05)
- [candidates-round-3-2026-07-05](candidates-round-3-2026-07-05.md) — 3 HF candidates tested; Grug-12B won improve by 2× (hard prompts); DeepSeek-V4-Flash dropped (leak); ollama infra fixed.
- [candidates-round-4-2026-07-05](candidates-round-4-2026-07-05.md) — Round-4: 3 HF candidates ALL DROPPED (Phi-4 leak + Gemmable MTP tie-break collapse + HauhauCS saturation ties); browser-bench-vision ported from cli-orchestration (5 subtasks T1-T5); batiai/gemma4-e2b:q4 missing winner re-installed.
- [candidates-round-5-2026-07-05](candidates-round-5-2026-07-05.md) — FULL re-bench of all 20 winners. e4b collapsed in codeq_sum + web_synth tb → SetneufPT (codeq_sum) + crow:9b (web_synth) new #1. improve/smart_trim/code_gen maintained (saturated). Cross-project rewire: codeq + web-research + zshrc.

## Resolved / reference
- [ollama-0.23.2-gemma4-q4_0-incompat](ollama-0.23.2-gemma4-q4_0-incompat.md) — resolved (Ollama 0.31.1 fixed it)
- [session-handoffs](session-handoffs.md) — compaction handoff log
- [agent-sessions](agent-sessions.md) — auto-generated cross-CLI coordination registry
