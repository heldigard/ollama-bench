# Active Context
- 2026-07-05: Round-3 bench (Grug-12B upset, 2x improve) → cross-project rewire (pegasus912→Grug-12B) → round-4 candidates (3 drops) → browser-bench-vision port from cli-orchestration → ollama infra fix + watchdog. Final: 21 LLM winners + 3 embed, 84 GB. RANKING.md + lineup aligned.

## Current Objective (per session)
- **Task**: (none pending) — meta-task: identify improvements / enhancements / fixes across the project now that the round-3+4 re-bench pipeline is complete and the bench infrastructure is upgraded.
- **Phase**: Reflect / Improve
- **Acceptance**: 3-5 actionable improvements identified + high-impact ones executed autonomously; deferred ones documented for future rounds.
- **Next**: identify wins → execute cheap wins → propose larger features.

## Preserved Negative Constraints
- **DO NOT** pull Q5/Q6/Q8 variants of existing Q4 winners — see `topics/quant-comparison-2026-07-04.md`.
- **DO NOT** pull reasoning-distilled small models (predictable smoke-leak: kwangsuklee, DeepSeek-V4-Flash, Phi-4-mini-reasoning) — re-reject without pull cost.
- **DO NOT** re-prompt MTP-tagged models without checking ollama MTP support (Gemmable-4-12B-MTP bench failed -10 vs base gemma4 +8.75 because MTP not wired in ollama call path).

## Recent Sessions
- 2026-07-05T19:38:00Z — Ollama dev-build broken (38MB binary, no llama-server bundled). Reinstalled official v0.31.1 via install.sh. Models in `~/.ollama/models` preserved.
- 2026-07-05T19:39:00Z — `~/.local/bin/ollama-watchdog` added (5-min healthcheck + auto-restart); crontab entry installed; NOPASSWD sudo already configured.
- 2026-07-05T20:00:00Z — Round-3 candidates bench. 3 pulled, 1 dropped (DeepSeek-V4-Flash leak). Grug-12B won improve by 2× (8.39 vs 4.15 hard prompts). HauhauCS Gemma4 Balanced kept (code_gen saturated tie).
- 2026-07-05T20:30:00Z — Cross-project rewire. pegasus912 → Grug-12B in `~/prompt-improve/src/prompt_improve/shared/config.py::_DEFAULT_IMPROVE_CHAIN` + warmup.sh + tests. Tests 102/102 pass.
- 2026-07-05T21:00:00Z — Top-5 hygiene cleanup. 2 stale models deleted (yuxinlu1 v2-tau2 + kwangsuklee). 1 missing winner documented (batiai/gemma4-e2b:q4).
- 2026-07-05T22:00:00Z — Round-4 candidates bench + browser-bench-vision port. 3 candidates pulled, ALL dropped (Phi-4 leak + Gemmable MTP -10 + HauhauCS 2.55). batiai/gemma4-e2b:q4 re-installed. Cross-CLI bench `cli-orchestration/browser/model_bench.py` ported to `features/browser_bench/` (5 subtasks T1-T5).

## Current Ship State (post-session, end of 2026-07-05)
- **Tests**: 102+ pass (ollama-bench 9/9 layout+list; prompt-improve 102/102).
- **Ruff**: clean across all touched projects.
- **Lineup**: 21 LLM winners + 3 embeddings = 24 models (~84 GB). Documented in `topics/local-ollama-lineup.md` + `RANKING.md`.
- **Commits** (this session):
  - ollama-bench: `6d980ad` (round-3 rewire) → `5395351` (top-5 hygiene) → `5c2ee17` (round-4 + browser-bench port).
  - prompt-improve: `69d436d` (Grug-12B rewire).
- **Pushed**: all to `origin/main`.

## Open Work (deferred to next round)
- **Tie-break saturation cap**: 10.50 / 16.00 in tie-break scoring hides real winners in smart_trim / web_synth / code_gen. Fix: bump scoring bounds OR add 3rd hard prompts.
- **cheap_bench.py port**: cross-provider bench (Ollama + cheap cloud cascade). Deferred from round-4. Lower impact than browser-bench-vision but useful.
- **Vision-capable model for browser-bench-vision T1/T2**: current text-only winners can't parse image refs in T4. Add `gemma3:4b-vision` or similar.
- **`bench-new` subcommand**: encapsulate the manual `pull → smoke → deep → tie-break` workflow observed across rounds 3+4. Saves ~10 min per round.
- **Claude-Code local bench integration**: `~/.claude/scripts/browser-model-bench.py` could become a thin wrapper around `ollama-bench browser-bench-vision` (instead of its own duplicate copy).
- **CI / GitHub Actions**: smoke on every PR. Current gate is local-only.

## Verified (this session, end-to-end)
- `ollama-bench browser-bench-vision --quick --models qwen3.5:4b Grug-12B` ran T1-T5 successfully.
- `ollama-bench deep + tie-break` on Grug-12B confirmed improve upset (delta +4.16 hard prompts).
- Cross-project rewire: `python3 -c "from prompt_improve.shared.config import _DEFAULT_IMPROVE_CHAIN"` returns Grug-12B at position 0 of 4.
- Ollama watchdog: `ollama-bench watch` healthy + `systemctl is-active ollama` = active.