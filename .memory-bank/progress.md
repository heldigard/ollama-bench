# Progress
> Bench history for ollama-bench

## 2026-07-05 — Round-5 full re-bench + test hardening

- 2026-07-05T22:00:00Z | status:completed | Round-5 re-bench: smoke (20/20 ok) + deep (20×8 prompts) + tie-break (13×5 hard). 2 material changes — `batiai/gemma4-e4b:q4` collapsed in codeq_sum tb (9.00 #11) + web_synth tb (5.50 #13); demoted. New #1: SetneufPT (codeq_sum, combined 2.0) + jaahas/crow:9b (web_synth, combined 2.5). improve/smart_trim/code_gen maintained (saturated). See `topics/candidates-round-5-2026-07-05.md`.
- 2026-07-05T21:30:00Z | status:completed | Cross-project rewire: codeq (`llm.py`+`cli.py`), web-research (`config.py`+`engine.py`), `~/.zshrc` (`CODEQ_SUMMARY_MODEL`). 3 repos, all tests green (ollama-bench 174 / codeq 71 / web-research 63).
- 2026-07-05T21:00:00Z | status:completed | Test hardening: +50 tests (124→174). New: `test_config_drift` (config↔RANKING), `test_score_saturation` (scoring caps), `test_tsv_schema` (writer/reader column contract), `test_leak_coverage` (14 LEAK_PATTERNS exhaustive), `test_prompt_budgets` (budget invariant). Caught 2 real bugs: 8BB→8GB typo + code_gen primary mismatch.

## 2026-07-04 — Initial v0.1.0 release

- 2026-07-04T15:30:00Z | status:completed | Vertical-slice split: 40+ scripts in `~/bench/ollama/` migrated to `~/ollama-bench/` package (9 vertical slices: smoke, deep, tie_break, lfm_variant, multi_domain, judge, embedding, report, list).
- 2026-07-04T15:25:00Z | status:completed | 46 tests passing (smoke/deep/tie_break/lfm_variant/judge/ollama/scorer/paths/layout).
- 2026-07-04T12:30:00Z | status:completed | Bench session: 63+ models → 51 evaluated → 23 unique winners via combined-rank (avg of first-pass + tie-break rank).
- 2026-07-04T12:00:00Z | status:completed | 3 DEAD models deleted + re-pulled: Mobius (still broken — Ollama Q4_0 gemma4 incompat), SetneufPT (still broken — qwen3next MTP init fail), VladimirGav (works now — was slow/leaky first time).

## Earlier bench rounds (June 27 — preserved in `~/bench/ollama/results_*/`)

- 6 rounds of model evaluation: triage + 4 deep + 1 quick = 19 models tested, 31+ deleted.
- Final lineup: 7 working + 1 utility = 8 total. ~33 GB.

## Bench results carried over (raw TSVs)

Historical results from earlier rounds (pre-package) live in `docs/history/results/`.
Current re-bench (2026-07-04, Ollama 0.31.1) outputs:

- `~/.cache/ollama-bench/results/smoke_all.tsv` — 64 models × leak status
- `~/.cache/ollama-bench/results/deep_bench.{tsv,md}` — 47 candidates × 5 tasks
- `~/.cache/ollama-bench/results/tiebreak_ranking.md` — 24 winners × 5 hard tasks
- `~/.cache/ollama-bench/results/bug_finding.md` — 15 candidates × 2 diffs

The CLI `ollama-bench` is the way to regenerate these.
## 2026-07-04 — Re-bench on unified Ollama 0.31.1

- 2026-07-04T19:00:00Z | status:completed | Re-bench after Ollama server unification (Windows+WSL → single WSL 0.31.1). Smoke 64 models → 47 OK. Deep 5 tasks × 47. Tie-break 24 saturated winners. Bug-finding NEW slice (15 candidates). Combined-rank top-5 → 16 LLM winners + 2 embeddings = 18 models kept (76 GB, was 325 GB).
- 2026-07-04T19:05:00Z | status:completed | 46 non-winners deleted. ex-DEAD verdicts (Mobius, SetneufPT) corrected — they load fine on 0.31.1; SetneufPT is now smart_trim #1. Mobius ranks low (deleted on merit).
- 2026-07-04T19:10:00Z | status:completed | Harness wiring updated: 8 points (warmup/browser/diff-review/pdf/project-memory/CODEQ_SUMMARY_MODEL/OLLAMA_SYNTH_MODEL/prompt_improve chain) → new top-2 winners per task.
- 2026-07-04T19:15:00Z | status:completed | bug_finding slice added (features/bug_finding/) — diff-with-known-bugs + recall scorer. composer Q8_0 kept (#5 bug-finding).
- 2026-07-04T19:08:55Z | status:completed | session:cb6822df-6550-4e12-b29e-bcbfaf8ca306 | claude: session done
- 2026-07-04T20:00:00Z | status:completed | Quant comparison (Q4 vs Q5 vs Q6 vs Q8) for 4B/e4b/e2b winners. Pulled unsloth E4B Q5/Q8 + E2B Q8 + qwen3.5:4b-q8_0. Ran smoke+deep+tie-break (9 models). RESULT: Q8 does NOT improve quality — confirms "Q4_K_M is the quality ceiling". Same-publisher: unsloth E4B Q5 (8.89 improve) > Q8 (8.59); batiai e4b Q4≈Q6; batiai e2b Q4 > Q6. Deleted 6 higher-quant variants (~27 GB freed). See topics/quant-comparison-2026-07-04.md.
- 2026-07-04T20:23:01Z | status:completed | 2026-07-04 bench v0.2.0-improve: think-strip scoring mode + seed reproducibility + leak-pattern expansion (14 patterns) + config-drift fixes across ollama-bench/codeq/prompt-improve + new-benchmarks roadmap topic. 90 tests pass. New HF candidates pulling for eval.
- 2026-07-04T20:42:36Z | status:completed | 2026-07-04 new-models bench: 4 HF candidates pulled + benched. huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus = NEW bug_finding #1 (17.98 > incumbent cryptidbleh 15.21) + saturated smart_trim/web_synth + top tool_call 9.82. kwangsuklee reasoning = bug_finding 15.00 + --strip demonstrator (keep). yuxinlu1 Opus4.8 + DuoNeural abliterated = below incumbents (drop candidates, ~15GB). Topic: topics/new-models-bench-2026-07-04.md.
- 2026-07-04T20:58:50Z | status:completed | 2026-07-04 round-2 bench: composer v2-3.5x-tau2 (yuxinlu1) KEPT — bug_finding #2 (15.86 > cryptidbleh 15.21 > xentriom Q8_0 14.26), code_gen tied #1 (6.0), improve #2-tier (3.08), tool_call 9.83. bge-m3 KEPT (multilingual embed, dim 1024 — needs re-index vs 768-d embeddinggemma, eval deferred). Lineup now 18 LLM + 3 embed = 21. RANKING_HISTORY: 70 tested, 21 kept, 49 elim.
- 2026-07-04T21:21:40Z | status:completed | 2026-07-04 iter-2: embedding-retrieval slice landed (P0, 7 tests, hand-rolled cosine, decides embed). Live bench: bge-m3 TIES embeddinggemma (MRR 1.000 both, nomic 0.875) -> no reindex, embeddinggemma stays primary, bge-m3 alt. _post_json DRY refactor (call+embed share, nesting<=3). Layout-gate boundary-regex fix. 105 tests pass. Pulling Qwen3-Coder-30B-A3B MoE (3B active, user request) + slyfox1186 functiongemma 9B (Opus 4.6 tool-calling) for bench.
- 2026-07-04T21:33:03Z | status:completed | 2026-07-04 iter-2 complete: Qwen3-Coder-30B-A3B MoE (3B active, user request) benched + DEL — hypothesis (large knowledge + small active compute) did NOT pan out (slower 20s AND weaker than dense 9-12B on all tasks except tool_call 9.81). Culled, 14GB freed. functiongemma KEPT (tool_call #1 9.85, code_gen #1-tier 7.0). Embed decision resolved (bge-m3 ties embeddinggemma, no reindex). Lineup: 22 models (19 LLM + 3 embed). Registry: 72 tested, 22 kept, 50 elim. MoE lesson registered in RANKING_HISTORY.
- 2026-07-04T21:52:37Z | status:completed | 2026-07-04T21:51:59Z | Harness config review (4 tools: prompt-improve, smart-trim, web-research, code-intelligence). prompt-improve + web-research + diff-review already aligned. FIX: smart-trim PRIMARY/SECONDARY was BACKWARDS — SetneufPT is smart_trim #1 (combined 1.0) but ran SECONDARY; qwen3.5:4b (#14) ran PRIMARY. Swapped in source + precompact labels + enforcing tests (smart-trim 144 tests green). codeq --summary help text + llm.py default → batiai (prior uncommitted). ~/.claude scripts sweep: diff-review→huihui, project-memory→batiai, agent_browser+pdf→pegasus912, web_research/synth→batiai (Mobius culled, no longer safe default). 3 commits: smart-trim b74762b, codeq 3fee248, ~/.claude adaafa6. FOUND live-env drift: CODEQ_SUMMARY_MODEL=LFM2.5 (stale, uninstalled) silently breaks codeq enrichment THIS session; source+zshrc correct → fix = relaunch Claude Code. Topic: topics/harness-wiring-2026-07-04.md.
- 2026-07-04T22:42:36Z | status:completed | 2026-07-04T22:30:00Z | 2 new ground-truth slices: browser_tool (ref-grounded a11y action; 6 cases, +3 JSON/+3 action/+3 grounded ref) + pdf_extract (schema field extraction + abstention; 5 cases, +3 JSON/+1.5 field/+2 abstain/-2 hallucinate). Both registered in cli.py (14 subcommands now). PROXY RETIREMENT: agent_browser PRIMARY was pegasus912 (proxy) — bench showed it's only #5 (9.70); functiongemma is #1 (10.19) → promoted to PRIMARY, pegasus912 demoted to gemma4-diversity FALLBACK. pdf_extract: pegasus912 tied #1 (11.14, field saturated within 0.03) → proxy caveat retired, stays as sound default. Live bench on 6 champions each. 124 tests pass (was 105). RANKING + RANKING_HISTORY updated. ruff clean.

## 2026-07-05 — Round-3 candidate bench (3 HF models tested)

- Pulled 3 Tier-S/Tier-A HF candidates: Jackrong/DeepSeek-V4-Flash (Q4_K_M), kai-os/Grug-12B (Q4_K_M), HauhauCS/Gemma4-12B-Balanced (Q4_K_M).
- **Ollama infra fix**: ollama binary at /usr/local/bin/ollama was a dev build (38MB, no llama-server bundled). Reinstalled via official installer (sh ollama.com/install.sh). All 22 installed models now load OK. ~2 min downtime; model blobs persisted in ~/.ollama/models.
- **Smoke gate**: DeepSeek-V4-Flash LEAKED (`thinking_process`, strippable=1 — same pattern as kwangsuklee reasoning-distilled). Grug-12B + HauhauCS passed.
- **Tie-break decisive**: Grug-12B won `improve` on hard prompts by **2×** (8.39 vs 4.15 for incumbent pegasus912). Verified by re-run (8.53 vs 4.37). Same delta on reproduce → robust.
- **Hero slices**: Grug-12B tied huihui on tool_call (9.81 vs 9.82, 0.01 within noise), ranked #3 on bug_finding (15.09 vs incumbent 15.35).
- **Decisions**: KEEP Grug-12B (new improve PRIMARY, gemma4 arch diversity, 7.4 GB), KEEP HauhauCS (code_gen tier-2 saturated tie, 7.6 GB), DROP DeepSeek-V4-Flash (leak, 6.6 GB freed). Final lineup: 17 LLM + 2 embed = 19 models, 84 GB.
- **Codeq_sum incumbent holds** (fredrezones55 13.00 vs Grug 8.09) — neither new candidate is competitive.
- **Pending user action**: edit `~/prompt-improve/src/prompt_improve/shared/config.py::_DEFAULT_IMPROVE_CHAIN` to prepend Grug-12B (currently starts with pegasus912). Cross-repo edit, requires explicit user opt-in.
- Full report: `topics/candidates-round-3-2026-07-05.md`.

## 2026-07-05 — Ollama self-healing cron (3 deliverables)

- Verified systemd infra: `ollama.service` already enabled + active + `Restart=always`. `override.conf` runs as `eldi` user (reads `/home/eldi/.ollama/models`).
- Verified pre-existing auto-update: `~/.local/bin/ollama-update` (4.2K, well-designed) + `~/update_all_clis.sh` step 9/10 cron 3×/day + @reboot. No new updater script needed.
- **Added**: `~/.local/bin/ollama-watchdog` — healthcheck + auto-restart for HUNG server (systemd's `Restart=always` only catches binary crashes, not process-alive-but-unresponsive). Cron `*/5 * * * *`. Sudo NOPASSWD already configured for eldi.
- Test: watchdog --status returns OK + `/api/version`. Health-check run also OK. Cron entry verified.
- Two more dead-ends recorded in dead-ends.md: dev-build broken ollama + auto-update cron rationale.

## 2026-07-05 — Cross-project rewire: pegasus912 → Grug-12B (improve role)

Round-3 rewire extended to consumer projects. pegasus912 lost the improve slot (was #1, now #2 behind Grug-12B's 2× upset).

**Files touched (4 sources + 1 test):**
1. `~/ollama-bench/src/ollama_bench/shared/config.py::TASKS["improve"]` — canonical improve primary pegasus912 → Grug-12B; fallback demoted to pegasus912.
2. `~/prompt-improve/src/prompt_improve/shared/config.py::_DEFAULT_IMPROVE_CHAIN` — Grug-12B prepended (chain 3 → 4).
3. `~/prompt-improve/scripts/ollama-warmup.sh` — `OLLAMA_IMPROVE_WARM_MODEL` default pegasus912 → Grug-12B.
4. `~/prompt-improve/tests/test_improve_prompt.py::test_role_model_map_prefers_gemma4` — assertion updated from name-substring (`"gemma" in tag`) to ollama `details.family == "gemma4"` (robust to fine-tunes whose name doesn't contain "gemma", e.g. kai-os/Grug-12B).
5. `~/prompt-improve/.memory-bank/REFERENCE.md` — docs updated (Primary=Grug-12B, #2=pegasus912, #3=Librellama, anchor=qwen3.5:4b).

**KEEP (not rewired — bench-validated, not proxy):**
- `~/cli-orchestration/src/cli_orchestration/browser/{subagent.py,_subagent_call.py}` — pegasus912 is browser-tool FALLBACK (bench #5 9.70), not improve proxy. Different rationale.
- `~/ollama-bench/src/ollama_bench/features/pdf_extract/command.py` — pegasus912 is pdf_extract tied-#1 (bench). Different slice.

**Verification matrix (per `verify-on-edit.md` discipline):**
- `python3 -m py_compile` ✓ on all .py edits
- `ruff check` ✓ clean on all .py edits
- `shellcheck -S warning` ✓ clean on warmup.sh
- `pytest tests/` 102/102 ✓ on prompt-improve
- `pytest tests/test_layout.py tests/test_list.py -q` 9/9 ✓ on ollama-bench
- E2E: 5/5 chain lookups return Grug-12B; ollama `details.family` confirmed `gemma4`
- Full e2e: `python3 -c "from prompt_improve.shared.config import _DEFAULT_IMPROVE_CHAIN; ..."` confirms 4-element chain with Grug-12B at position 0.

**Lessons / `dead-ends.md` addendum:** old test was brittle to model naming — it asserted `"gemma" in model_name.lower()`. New fine-tunes like `kai-os/Grug-12B` don't have "gemma" in the tag even though they're gemma4 arch. Fixed by switching to ollama `details.family` check (authoritative metadata, not name pattern).

## 2026-07-05 — Top-5 hygiene cleanup (post-round-3)

User requested: clean Ollama models not in any task's top-5. Audit of installed (24) vs lineup found 2 extras + 1 missing winner.

**Deleted (13 GB freed):**
- `hf.co/yuxinlu1/gemma-4-12B-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:latest` (7.4 GB) — was DROPPED in round-2 (per `new-models-bench-2026-07-04.md::DECISIONS`) but never `ollama rm`'d. Leftover.
- `kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest` (5.6 GB) — leaks `thinking_process` despite `think=False`; not in any task's top-5. Was kept only as `--strip` demonstrator from round-2. Stale.

**Missing winner (NOT deleted; documented for re-pull):**
- `batiai/gemma4-e2b:q4` — listed in lineup as code_gen tied; not in `ollama list`. Probably deleted in the 2026-07-04 46-model cleanup. Re-pull: `ollama pull hf.co/batiai/gemma4-e2b:Q4_K_M`.

**Header count fix:** prior version said "17 LLM winners + 2 embeddings = 19 models" but the file actually lists 20 LLMs + 3 embed = 23. Header was off by 3 from a typo carried since round-3 (round-2 added huihui + slyfox but the header wasn't incremented then). Now fixed.

Final state: 20 LLM winners + 3 embeddings (embeddinggemma + nomic-embed-text + bge-m3 alt) = 23 models, ~84 GB.

## 2026-07-05 — Round-4 candidates + cross-CLI bench port

### Round-4: 3 candidates pulled, ALL 3 dropped (~16 GB freed)

Tested 3 fresh HF candidates targeting code/browser/agentic slots:

- `lmstudio-community/Phi-4-mini-reasoning-GGUF` (2.5 GB) — **LEAK** at smoke (`thinking_prefix`). Pattern matches `kwangsuklee` + `DeepSeek-V4-Flash`. **Prediction rule established**: reasoning-distilled small models consistently leak thinking despite `think=False`.
- `Mia-AiLab/Gemmable-4-12B-MTP-GGUF` (7.4 GB) — pass smoke, **LOSE tie-break** hard prompts (improve -10.00 vs Grug +8.75, codeq_sum -4.03 vs fredrezones55 +13.00). MTP not wired in ollama call path; base response is poor on structured-spec tasks.
- `HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive` (6.5 GB) — pass smoke, **LOSE tie-break** (improve 2.55, codeq_sum 8.07 vs SetneufPT 4.32 + fredrezones55 13.00). Saturation ties elsewhere inconclusive.

All 3 deleted.

### Missing winner re-installed

`batiai/gemma4-e2b:q4` (3.4 GB) — code_gen tied winner absent from `ollama list` after 2026-07-04 cleanup. **Re-pulled 2026-07-05 round-4**, verified loads.

### Cross-CLI bench port: browser-bench-vision

Ported `~/cli-orchestration/src/cli_orchestration/browser/model_bench.py` + 3 sibling helpers (`_bench_data.py`, `_bench_fixtures.py`, `_bench_scoring.py`) into `~/ollama-bench/src/ollama_bench/features/browser_bench/`. 5 subtasks: T1 vision_ocr, T2 vision_classify (8-class UI state), T3 snapshot_diff, T4 tool_call, T5 speed.

**Wired**: `cli.py::_SLICES` now lists `browser-bench-vision`. `cmd_browser_bench_vision(args)` satisfies `test_layout.py::test_every_feature_has_cmd_function`.

**Imports patched**: relative → absolute (`from ._bench_data` → `from ollama_bench.features.browser_bench._data`).

**Models updated** to current champions (qwen3.5:4b + Grug-12B + huihui — replaces the DROPPED Mobius + the listed HauhauCS-4b typo).

**Verified**: `python3 -m py_compile` ✓, `ruff check` ✓, `pytest tests/test_layout.py tests/test_list.py` 9/9 ✓, `ollama-bench browser-bench-vision --quick` E2E ran T1-T5 successfully on 2 models.

### What was NOT ported (justified)

- `~/smart-trim/tests/test_summarize.py`: monkeypatched ollama unit tests, NOT a model bench.
- `~/cli-orchestration/tests/test_agent_browser_subagent.py`: snapshot validator (no model calls).
- `~/codeq/tests/test-code-intelligence.py`: code-intelligence regression, not a model eval.
- `~/cheap-llm/cheap_bench.py`: cross-provider bench (Ollama + cheap cloud). Defer to round-5.

### Caveats / future work

- Hard-prompt tie-break saturation continues to hide real winners in smart_trim / web_synth / code_gen at 10.50 / 16.00. Bump upper bound OR add 3rd hard prompts.
- MTP-tagged models may benchmark poorly without ollama MTP wiring. Treat MTP capability as throughput-only (not capability).
- Vision-capable models needed for browser-bench-vision T1/T2; current champion qwen3.5:4b only.

## 2026-07-05 — Project improvements (meta-task per user)

User asked: identify improvements / enhancements / fixes across the project now that round-3+4 + browser-bench port are landed.

**Inventory findings:**
- 0 TODOs/FIXMEs in source (clean debt)
- README.md only listed 6/14 subcommands (heavy drift after rounds 3-4)
- `activeContext.md` stale ("Iter-2 task" — pre-round-3)
- Tie-break saturation at 10.50/16.00 hides real winners (documented; deferred to bump scoring bounds)
- Manual `pull → smoke → deep` workflow repeated 2 rounds — encapsulable into one command
- `cheap_bench.py` cross-provider bench (deferred)
- Browser-bench-vision ported but `gemma3:4b-vision` not added to lineup for T1/T2 (deferred)

**Wins executed (3):**

1. **README.md rewritten** — 14 subcommands documented (was 6). Added pipeline diagram, current 2026-07-05 lineup table, cross-CLI bench ownership section, deferred-work section (tie-break cap bump, cheap_bench port, vision-capable model, CI).

2. **activeContext.md refreshed** — replaced stale "Iter-2 task" with current state (3 commits pushed, 21 winners, browser-bench-vision landed, watchdog active). Includes Preserved Negative Constraints (don't pull reasoning-distilled, Q5/Q6/Q8 of Q4 winners, MTP without ollama MTP support).

3. **`candidates` slice added** (NEW, 4-file vertical slice per CLAUDE.md pattern):
   - `features/candidates/command.py` — orchestrator that runs `pull → smoke → deep → MD report` for a list of HF model tags in one command. Reuses `smoke` and `deep` slices via subprocess (no slice-to-slice imports).
   - Wired into `cli.py::_SLICES` as `(candidates, add_candidates, ...)`.
   - `cmd_candidates(args)` named entry function satisfies `test_layout.py::test_every_feature_has_cmd_function`.
   - `ollama-bench candidates 'hf.co/owner/model:Q4_K_M'` — encapsules ~15 min of manual orchestration per round. Pull log + smoke gate + deep scores + recommendations in one MD file.

**Wins deferred (3):**

- Tie-break saturation cap bump (10.50 → higher) — scoring formula change, needs design discussion before code.
- `cheap_bench.py` cross-provider port from `~/cheap-llm/` — separate repo, lower impact than browser-bench-vision.
- Vision-capable model for browser-bench-vision T1/T2 (e.g. `gemma3:4b-vision` from Ollama library).
- `claude-code` hooks/scripts refactor: `~/.claude/scripts/browser-model-bench.py` could become a thin wrapper around `ollama-bench browser-bench-vision` instead of its own duplicate. Cross-repo change.
- GitHub Actions CI: smoke on every PR. Currently local-only gate.

**Verification matrix:**

- `python3 -m py_compile` ✓ (candidates/command.py + cli.py)
- `ruff check` ✓ clean
- `codeq refs` ✓ (1 ref to add_candidates in cli.py::_SLICES)
- `pytest tests/test_layout.py tests/test_list.py` ✓ 9/9 (incl. new candidates slice)
- `ollama-bench candidates --help` ✓ shows positional models + --tasks + --keep-on-pull-fail
- `ollama-bench candidates` (no args) ✓ errors with "at least one model required"
- 2026-07-08T00:49:43Z | status:completed | Cross-CLI maintenance audit: benchmark scoring work is active; keep memory tied to durable scoring/canonical-task decisions, not transient run logs.
- 2026-07-08T01:39:45Z | 2026-07-08: Refactored benchmark rankings and config after new scorer/rebench. RANKING.md now reflects refactor outputs; shared/config.py TASKS primary/fallback updated for canonical tasks. Tests pass (183 passed).
- 2026-07-08T02:08:12Z | status:completed | 2026-07-08: Added rendered-PDF OCR benchmark slice and ranked installed vision models. Unlimited OCR hf.co/sahilchachra/Unlimited-OCR-GGUF:Q4_K_M is pdf_ocr #1: 12.00 score, 1.00 avg recall, fastest in live synthetic PDF OCR. It requires /api/chat vision input and literal prompt "ocr [img]"; generic text-extraction prompts can return empty. RANKING.md now separates pdf_extract (structured JSON from parsed markdown; functiongemma primary) from pdf_ocr (rendered PDF reading; Unlimited OCR primary).
- 2026-07-08T02:57:20Z | status:partial | Current-model strip rebench: installed six current Qwen3.5+/Gemma4 HF candidates; smoke 13/14 clean, DeepSeek-V4-Flash marked strippable=1 and included in deep --strip; deep artifact results_current_models_strip_deep_20260708.md written. No downstream rewire yet: web_synth/code_gen have ties and PDF/OCR/tool benches still pending.
- 2026-07-08T03:00:32Z | status:partial | Tool-call follow-up completed from concurrent run: Openclaw Qwen3.5 9B ranked #1 at 10.36, with several incumbents/new candidates clustered at 10.34; DeepSeek-V4-Flash lagged at 8.35. Artifact: results_current_models_tool_call_20260708.md. No config rewire from this near-tie alone.
- 2026-07-08T03:03:55Z | status:partial | PDF follow-up completed: Unlimited OCR remains pdf_ocr #1 at 12.00/1.00 recall; LIFT is viable fallback at 11.12/1.00 recall but slower. PDF-extract current-model run ranks Openclaw Qwen3.5 9B #1 at 12.05, narrowly ahead of functiongemma/OmniCoder/crow at 11.96. Artifacts written for commit.
- 2026-07-08T03:06:52Z | status:partial | Bug-finding follow-up completed: DeltaCoder 9B ranked #1 at 14.06, narrowly ahead of OmniCoder 14.04 and HauhauCS Gemma4 14.02. Artifact: results_current_models_bug_finding_20260708.md. Treat top three as near-tie pending tie-break.
- 2026-07-08T12:00:00Z | status:completed | Bench methodology overhaul: +15 edge-case prompts (improve 7, codeq_sum 7, smart_trim 6, web_synth 6, code_gen 7), +4 tool_call hard cases, +2 bug_finding hard diffs, redesigned HARD_PROMPTS (genuine hard scenarios, not concatenated), improved all 5 task scorers (gradated scoring, conflict-flagging, source utilization), added depth scoring to _hygiene. 187/187 tests pass. Split canonical_tasks.py → prompts.py (data) + canonical_tasks.py (scoring, <500 LOC). Ecosystem verified: all consumer repos pass (prompt-improve 116, smart-trim 158, web-research 65).
- 2026-07-08T13:00:00Z | status:completed | GPU-safe incremental benching: deep + tie_break now support --resume (skip completed), --cooldown (seconds between models, default 60), --temp-limit (GPU °C threshold, default 75). Sequential execution replaces ThreadPoolExecutor. Per-model incremental TSV save prevents progress loss on kill/crash. nvidia-smi GPU temp monitoring. 3 new HF models pulled: TeichAI/Qwen3.5-9B-Fable-5-v1 (Fable 5 distillation), FadedRedStar/Qwen3.5-9B-heretic, mradermacher/Gemma-4-12B-StyleTune. Smoke 31/31 pass. Deep bench started (13 models × 33 prompts, 60s cooldown) — running overnight.
- 2026-07-08T13:18:36Z | status:completed | Fixed CRITICAL resume data-loss bug in deep bench: details JSONL was written only at run end, so a mid-run kill left no JSONL → resume reconstructed empty results → final TSV rewrite DROPPED every previously-benched model ('perder todo el progreso'). Fix: JSONL is now append-only (one line per case, flushed after each model) + resilient loader (skips truncated tail) + TSV-mean fallback. Also fixed cooldown firing before the first model, removed dead WORKERS=4 (ghost of the parallel pool that overheated the GPU), extracted shared/gpu.py (gpu_temp + wait_gpu_cool) so deep + smoke pace identically, and gave smoke the same --resume/--cooldown/--temp-limit + incremental save. Fresh (non-resume) runs now clear stale TSV/JSONL to prevent append-stacking. 194/194 tests pass (incl. 5 new resume regression tests). Smoke re-run 31/31 (GPU peak ~50°C). Deep launched: 30 candidates × 33 prompts, --resume --cooldown 60 --temp-limit 75, GPU peak 69°C, incremental save verified on real execution (TSV+JSONL flush per model). Estimated ~3h full run.
- 2026-07-08T13:47:38Z | status:active | Removed the parallel-pool OVERHEATING root cause from ALL benches: bug_finding/tool_call/pdf_extract used ThreadPoolExecutor(max_workers=4) (= the pool that hit 80°C+ yesterday). Added shared/gpu.py::paced() (sequential + temp-gate + cooldown between models); all 4 specialized benches now use it with --cooldown/--temp-limit. tie_break deduped to shared gpu helpers. Wrote scripts/run_pipeline.sh (orchestrator: wait-deep -> bug-finding/tool-call/pdf-extract/pdf-ocr -> tie-break, idempotent, GPU-safe, nohup) + scripts/tie_winners.py (detects models within 0.5 of per-task top). 194/194 tests + shellcheck clean. Pipeline launched detached: deep 14/30 running, orchestrator in Stage-0 wait; will auto-run specialized then tie-break when deep finishes.
- 2026-07-08T15:28:14Z | status:active | Pipeline progress: deep 30/30 + tie-break 26/26 DONE. Specialized benches running (bug-finding started, 30 models each for bug-finding/tool-call/pdf-extract + 2 for pdf-ocr). DEEP WINNERS SHIFTED 4/5 vs config.py primaries: improve held (OmniCoder); codeq_sum crow→gemma4-e4b:q4; smart_trim Openclaw→HauhauCS-Balanced; web_synth DeltaCoder→SC117/heretic-QAT; code_gen Openclaw→prithiv/lift. DeltaCoder + Openclaw fell out of top-5. New hf.co model set reshuffled the field. config.py primaries + RANKING.md now stale in 4/5 — DO NOT rewire until full pipeline (specialized + combined deep+tie-break) done. Noise cleaned: removed 6 orphan prior-session result dumps (deep_bench old, deep_v2_Gemma scratch, browser_tool.md old, bench_v2 logs) + 4 stale 07-04 logs + 22 __pycache__ dirs. Kept *_refactor_20260708 (comparison baseline) + deep_r5/tiebreak_r5 (round-5 topic refs).
- 2026-07-08T19:16:28Z | status:completed | Round-7 FINAL: full pipeline done (smoke 31/31, deep 30×33 --strip, tie-break 26×15, bug_finding/tool_call/pdf_extract ×30, pdf_ocr ×2). Combined rank (deep+tiebreak)/2 rewired 7/9 PRIMARY in shared/config.py + 7 cross-CLI consumer repos (prompt-improve, smart-trim, web-research, cheap-llm, agent-memory, cli-orchestration, ~/.claude/scripts). qwen3.5:4b replaced by cryptidbleh/gemma4-claude-opus-4.6 (9.97 vs 8.85 avg, faster). Lineup trimmed to top-5 union: 12 losers + qwen3.5:4b deleted → 19 LLM + 3 embeddings = 22 models. New champs: improve+bug_finding OmniCoder, codeq_sum batiai/gemma4-e4b:q4, smart_trim HauhauCS-Balanced, web_synth TeichAI/Fable-5-v1, code_gen lift, tool_call+pdf_extract+browser SetneufPT/Qwopus3.5-4B-MTP, pdf_ocr Unlimited-OCR. DeltaCoder+Openclaw fell out of top-5. All 7 repos pushed clean.
- 2026-07-08T19:16:28Z | status:completed | Round-8 (same day): tested 4 NEW HF candidates vs round-7 champs — ALL LOST, deleted. shuhulx/Qwopus3.5-4B-Coder-Fable5-v1 (tool_call 9.79 < SetneufPT 10.10); tvall43/Qwen3.6-14B-A3B-FableVibes MoE (mid everywhere, no specialist-killer; MoE-latency thesis failed: tps 6.9 vs 4B 10.7); llmfan46/composer2.5-v2 Q4 (bug_finding 15.01 TIES xentriom 14.99 same-base noise, but web_synth 10.82 < xentriom-Q8 11.92 — Q8 stays); KevinJK51/Qwen3.6-12B-Thinking-V2 (bug_finding 11.03, thinking bad fit for diff-review). 4 others skipped analytically (Qwable-9B saturated family, 2× LFM2.5 tiny, Thireus 27B IQ2 trash). Lineup UNCHANGED at 22, no rewire. RANKING_HISTORY §round-8 + 4 durable learnings recorded. Re-test MoE only if coder-tuned variant drops.
- 2026-07-09T21:32:46Z | status:completed | 2026-07-09: Replaced close lexical scores with risk-weighted semantic contracts, alternative phrasing groups, evidence/length penalties, per-case persisted weights, raw-response JSONL, and two reproducible rescored rounds plus a fresh final run.
- 2026-07-09T21:40:55Z | status:completed | 2026-07-09 final validation: full pytest and Ruff pass; changed benchmark files are formatted and Pyright-clean. Final role ordering is Cryptid/Negentropy9B, Batiai-e4b/Qwopus, and Batiai-e2b/Cryptid.
- 2026-07-09T22:16:47Z | status:completed | 2026-07-09 independent wiring verification: coted all 7 graduated projects against authoritative bench (results_wiring_validation_20260709.md). Wiring CORRECT with correct winner everywhere — prompt-improve Cryptid->Negentropy->Qwopus (8eb1477), smart-trim batiai-e2b PRIMARY + cryptid SECONDARY (b0f2cf2), codeq batiai-e4b (1273af4), ollama-client GEN=cryptid/SUMMARY=batiai v1.1.0 chat->generate fallback (bfdd2e4). audited (no own winner): agent-memory inherits CODEQ_SUMMARY_MODEL, web-research uses ollama_client DEFAULT, skill-router pure router. Fixed stale codeq comment (9.23/9.15 + date 07-08 -> real 9.18/8.99 + 07-09) e4034c0; documented codeq single-model design (Qwopus FALLBACK is ranking-only, unlike smart-trim fail-open secondary). No wrong/stale winner wired anywhere.
- 2026-07-12T18:08:45Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | claude: **Lineup:** 19 LLM + 3 embeddings = 22 models. Trimmed to top-5 union per role.
- 2026-07-12T18:50:00Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Round-9 (2026-07-12):** 9 HF candidates filtered (7 rejected pre-bench: Qwable no-verify / 2× Cosmos3 video / grug-9b redundant Qwen3.5-9B finetune / MiniCPM5-1B no GGUF / GELab GUI agent out-of-scope / FastContext needs new task). **gemma-4-E4B-it-qat-q4_0-gguf (Google oficial) BLOCKED by ollama pull 400** (4/4 chunks download 5.2GB+991MB but manifest registration fails — likely gated differently than HF API reports, no CLI license-accept flag). **`hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` DETHRONED `batiai/gemma4-e4b:q4` in codeq_sum** (9.40 vs 9.19, +2.3% in 4-way deep) — also code_gen #2 fallback (10.38 vs lift 10.52, -1.3%); web_synth #4 (8.84 vs xentriom Q8_0 10.19, lose). Smoke ok, no leak. Tie-break vs OmniCoder MISLED on web_synth (OmniCoder not the champ). Wiring rewired: `src/ollama_bench/shared/config.py:42` primary→Qwythos, fallback→batiai, NEW tertiary→SetneufPT; `RANKING.md` 3 tables (line 13 wiring, line 43 codeq_sum deep #1, line 138 Per-task PRIMARY); `~/.zshrc:1134` `CODEQ_SUMMARY_MODEL="hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M"`; agent-memory inherit per `rules/code-intelligence-tools.md`. `tests/test_config_drift.py` 6/6 pass (drift guard works). Full pytest 204/204, ruff clean. Lineup 22 → 23 models. See `topics/candidates-round-9-2026-07-12.md`.
- 2026-07-12T20:30:00Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Round-10 (2026-07-12):** 8 cross-task 4-way validations + 1 follow-up 5-way = **3 PRIMARY DETHRONES**. Round-9 learning generalized: stale per-task champions were vulnerable to other-task champions never tested against them. **(1) improve:** TeichAI/Fable-5-v1 (web_synth champion) dethroned OmniCoder (2.46 vs 0.93, +1.53 in 4-way deep). **(2) smart_trim:** SC117/heretic-QAT (smart_trim #2 fallback) dethroned HauhauCS-Balanced (10.79 vs 9.87, +0.92) — gemma-4-12B-heretic family rotation. **(3) bug_finding:** xentriom Q8_0 (web_synth #2) dethroned OmniCoder in 5-way specialized bench (14.97 vs 14.49, +0.48). Plus pdf_extract #2 swap: OmniCoder (12.00) > ykarout/Openclaw (11.97). HELD: codeq_sum Qwythos, web_synth TeichAI, code_gen lift, tool_call SetneufPT, pdf_extract SetneufPT. Tool_call #2 yuxinlu1 held (10.07 vs SetneufPT 10.10, +0.03). Wiring rewired: `src/ollama_bench/shared/config.py` 3 primary changes + 1 fallback swap; `RANKING.md` 4 task sections + 3 tables; `~/.claude/scripts/diff-review.py` `OLLAMA_CODE_MODEL` → xentriom Q8_0 (was OmniCoder) + 12GB VRAM warning. 14/14 drift + canonical pass, 204/204 full pytest, ruff clean. Lineup 23 models unchanged (re-organized roles). See `topics/candidates-round-10-2026-07-12.md`. Downstream action items: `~/prompt-improve/_DEFAULT_IMPROVE_CHAIN` put TeichAI first; `~/smart-trim/features/summarize/command.py:28` use SC117/heretic-QAT.
- 2026-07-12T22:30:00Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Round-11 (2026-07-12):** 4 cross-task 4-way validations = **ZERO REWIRES**. Round-10 champions held all 4 attempts to displace them via cross-task challengers. (a) improve: TeichAI held (2.46), SC117 0.94 #2 (no displace), Qwythos -0.51 NEGATIVE on improve prompts (specialist leak). (b) smart_trim: SC117 held (10.79), xentriom 8.89 #3 (no displace). (c) tool_call: SetneufPT held (10.10 vs yuxinlu1 10.09, +0.01), TeichAI 9.93 #3 (close but no displace). (d) code_gen: lift held (10.52), SC117 9.96 #4 (no displace). **Strategic finding:** round-10's 3 dethrones were the LAST easy wins. Remaining champions are HARDENED against cross-task challengers. Round-10 vs round-11 asymmetry: a reasoning-heavy champion beats a coding-heavy champion (one-way), but two reasoning-heavy champions don't compete (orthogonal). Lineup at LOCAL OPTIMUM. Strategic recommendation: move from every-2-days re-bench to triggered/quarterly cadence. Coder-MoE 14B-A3B remains the highest-leverage untested architecture when one becomes available. See `topics/candidates-round-11-2026-07-12.md`.
- 2026-07-12T23:50:00Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Round-12 (2026-07-12):** gemma-4 official family exploration = **ZERO REWIRES, 1 add, 1 delete**. Tested two NEW gemma-4 variants never benched: (1) `unsloth/gemma-4-26B-A4B-it-GGUF` MoE 26B-A4B at UD-Q3_K_M 13GB — smoke ok 0.8 tps (slow, partial GPU offload), code_gen 9.90 #4 (LOSES -0.62 vs lift) → **DELETE** (lose + 10× latency penalty). MoE architecture confirmed NOT competitive on 16GB VRAM. (2) `unsloth/gemma-4-12B-it-qat-GGUF` UD-Q4_K_XL 6.9GB — smoke ok 6.6 tps, smart_trim 9.82 #3 (ties HauhauCS-Balanced 9.87 within 0.05 noise, loses SC117 10.79 -0.97) → **KEEP as depth** (official upstream of lineup's heretic variants, reference value if community drops). Lineup 23 → 24 (12B QAT added, 26B-A4B deleted). **TERMINAL STABILITY confirmed:** all plausible architectures exhausted (no coder-MoE 14B-A3B on HF, gemma-4-26B-A4B loses on quality + latency, gemma-4-12B QAT ties community heretic, cross-task challengers exhausted). Recommend TRIGGERED re-bench policy only (Ollama major upgrade, new HF release, quarterly drift watch). See `topics/candidates-round-12-2026-07-12.md`.
- 2026-07-12T23:55:00Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Cleanup pass 2026-07-12 PM:** autonomous corrections and improvements following round-12 closure. 5 lines of work: (1) **Cross-CLI rewire** (round-10 action items complete): `~/prompt-improve/src/prompt_improve/shared/config.py` `_DEFAULT_IMPROVE_CHAIN` → TeichAI primary, Negentropy-9B fallback, SetneufPT, cryptidbleh (was cryptidbleh/OmniCoder); 192/192 tests pass; `~/smart-trim/src/smart_trim/features/summarize/command.py` `_PRIMARY_MODEL` → SC117/heretic-QAT, `_SECONDARY_MODEL` → HauhauCS (was batiai/cryptidbleh); 170/170 tests pass; `~/.claude/scripts/diff-review.py` `OLLAMA_CODE_MODEL` → xentriom Q8_0 (was OmniCoder); test updates for all three repos. (2) **Drift guard hardening:** new test `test_tertiary_model_in_ranking_top_n` in `tests/test_config_drift.py` syncs the `tertiary_model` field added in rounds 9/10 with RANKING.md; total 205 tests pass. (3) **Dead code removal:** `paths.py::log_path` (no tests, no callers) removed; `__pycache__/` cleaned across `src/`. (4) **Bench-methodology.md** updated with new "Step 6: Cross-Task 4-Way Validation (mandatory after rewire)" section formalizing the round-9/10/11/12 learning as standard practice. (5) **Memory bank:** action items in `topics/harness-wiring-2026-07-04.md` updated to mark rewire done (`✅`); `currentTask.md` + `progress.md` log cleanup pass.
- 2026-07-12T23:59:00Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Round-13 purge 2026-07-12 PM:** apply top-5 union rule — delete any installed model NOT in any task's top-5. Parser extracted top-5 per task from `RANKING.md ## task` sections (round-7/8/9/10/11/12 leaders); deleted: (a) `Librellama/gemma4:e2b-Uncensored` — not in any top-5 (depth-only multi-task mid); (b) `hf.co/unsloth/gemma-4-12b-it-qat-GGUF:UD-Q4_K_XL` — added round-12 as gemma-4-12B official upstream, never entered top-5 (tied HauhauCS within noise, lost SC117 -0.97 in smart_trim v3). Both deleted via `ollama rm`. **Lineup 24 → 22 models** (19 LLM + 3 embed). **10.3GB disk freed** (combined with round-12 26B-A4B delete: 23.3GB total this session). Memory bank updated (`local-ollama-lineup.md` installed section rewritten to reflect top-5 union; currentTask.md lineage counter). Cumulative purges this session: 3 models (26B-A4B MoE + Librellama + 12B QAT official).
- 2026-07-12T23:59:30Z | status:completed | session:be523e99-e23e-4613-8950-f28c454bcd3d | **Round-14 (2026-07-12):** **ZERO REWIRES, two new-family attempts both fail.** (1) `unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_M` → 400 sharded GGUF (Ollama #5245); pivoted Q3_K_S = 48GB on disk; smoke 0.5 tps partial GPU offload → **DELETE without bench** (latency veto per round-12 lesson). (2) `bartowski/Codestral-22B-v0.1-GGUF:Q4_K_M` → 13GB; smoke 1.8 tps ok; **code_gen 4-way: Codestral 8.67 #4 (-1.85 vs lift)** → **DELETE**. Lineup 22 → 22 (no net change). **DEEPER terminal stability confirmed:** robust against new families (Llama-4 first Meta in lineup, Codestral first Mistral). 84.3GB total disk freed rounds 12-14 cumulative. See `topics/candidates-round-14-2026-07-12.md`. Recommend stopping all test-the-limits work; lineup frozen unless 5-8GB sweet-spot new family emerges.
- 2026-07-13T14:18:40Z | status:completed | session:947f69e9-b78b-4182-9f7e-6951ffdc771b | claude: **Lineup:** 19 LLM + 3 embeddings = 22 models (round-13 purge 2026-07-12:...
- 2026-07-13T15:29:07Z | 2026-07-13T16:00:00Z | status:completed | claude-controller | **smart_trim correction (round-15 name-bias revert):** round-15 wrongly demoted batiai/gemma4-e2b to "candidate" while cabling SC117 (lower score) as primary via a circular "throughput non-decisive" argument. Round-15 cross-validation actually scored batiai-e2b 11.67 + cryptidbleh 11.63 > SC117 10.79 + Hauhau 9.87; round-7 had batiai-e2b #3 at 11.93. Two failures: (1) name-bias — e2b read as tiny though 4.6B; (2) non-governing metric used to discard a governing-metric win (inverts quality-over-speed). Reverted: config.py smart_trim primary->batiai-e2b/fallback->cryptidbleh; RANKING.md 3 sites; ~/smart-trim command.py+test (commit 8b634be). 218+179 tests + drift + ruff green. codeq_sum (batiai-e4b->Qwythos) NOT touched (real quality win 9.40>9.19). Detail: topics/candidates-round-15-2026-07-13.md Correction section + systemPatterns anti-pattern.
- 2026-07-13T18:40:51Z | 2026-07-13 re-deep + bench hardening: VRAM-clean unload entre modelos (477110c) + ollama-client serialize lock opt-in (06cbc90) + retry configurable deep retries=0 (6a55254). Re-bench 3 corridas: smart_trim batiai-e2b confirmado (11.81); improve TeichAI sin cambio (ruido); codeq_sum Qwythos se queda (funciona en producción 9.17). Qwythos da err HTTP bajo deep (eval None -100) incluso con VRAM-clean: causa NO determinada (no contención — unload opera y descarga; no prompt — deep prompt tiene instrucciones; no timeout — 240s). Limitación conocida del bench con Qwythos. Ningún rewire. Slices classification+rerank aterrizados (411d5af).
- 2026-07-13T19:08:51Z | 2026-07-13 wiring alignment final: codeq llm.py default batiai-e4b->Qwythos (codeq_sum ganador round-9) + anadido _CODEQ_FALLBACK_MODEL (batiai-e4b 5.3GB) para robustez VRAM (Qwythos 6.8GB puede no cargar bajo contension). agent-memory MAINT_MODEL_DEFAULT batiai-e4b->Qwythos (mismo ganador, comparten CODEQ_SUMMARY_MODEL). prompt-improve (TeichAI) y smart-trim (batiai-e2b) ya estaban correctos. Commits: codeq 894a945, agent-memory 8038ef2. Qwythos ctx: 1M marketing, techo real RTX5080 128k-256k; codeq_sum usa 4096 (sobra).
- 2026-07-13T19:34:35Z | 2026-07-13 find-tokens task: fd v10.4.2 instalado (~/.local/bin/fd + fdfind alias) via fd-update wrapper (download musl, backup, idempotent). Cron update_all_clis.sh seccion [12/12] fd anadida + contadores /11->/12, shellcheck 0. Regla cross-CLI: ~/.claude/rules/repo-exploration.md (Claude autoload) + seccion en ~/.gemini/GEMINI.md (Antigravity/Gemini) + ref en ~/.codex/AGENTS.md. Promueve git ls-files/fd/rtk find/codeq map sobre find naked (filtra __pycache__/.venv/dist). Validacion: fd 0 omisiones vs git, codeq Qwythos+fallback calidad alta, 5 repos tests verde.
- 2026-07-13T20:30:00Z | status:completed | claude-controller | **Round-17 (2026-07-13): fresh 5-way improve re-bench — ONE PRIMARY DETHRONE.** Fresh 5-way deep re-bench of `ollama-bench deep -t improve` exposed round-10's blind spot: cryptidbleh was the chain tail (legacy 2026-07-09 #1, smart_trim round-15 #2) but was NOT in round-10's 4-way, so its strength was never re-validated against TeichAI. Fresh 5-way: `cryptidbleh/gemma4-claude-opus-4.6` 2.97 (NEW #1) > `TeichAI/Qwen3.5-9B-Fable-5-v1` 2.46 (round-10 champion demoted to fallback) > `Negentropy-9B` 2.03 (held) > `SetneufPT/Qwopus3.5-4B` 1.68 (now bench-validated, was untested) > `OmniCoder` 0.93 (held lowest, confirmed demoted to bug_finding/pdf_extract depth only). **Rewire applied:** `~/prompt-improve/src/prompt_improve/shared/config.py::_DEFAULT_IMPROVE_CHAIN` swaps to `cryptidbleh → TeichAI → Negentropy-9B → SetneufPT` (OmniCoder removed). Synced: `tests/test_improve.py` (5 tests), `README.md`, `CLAUDE.md`, `scripts/ollama-warmup.sh` (`OLLAMA_IMPROVE_WARM_MODEL` default), `.memory-bank/REFERENCE.md`. ollama-bench side: `src/ollama_bench/shared/config.py::TASKS["improve"]` primary→cryptidbleh, fallback→TeichAI; `RANKING.md` (4 sections: validation table, improve section, per-task table, runtime notes); `topics/harness-wiring-2026-07-04.md` (prompt-improve row + web-research dual-role note); `topics/local-ollama-lineup.md` (improve row + round-17 header); NEW `topics/candidates-round-17-2026-07-13.md`; `topics/_index.md` consolidates round-13/14/15/16/17 entries. Tests: prompt-improve 199/199 pass (2 pre-existing env-dependent `test_target.py` failures unrelated, documented in prompt-improve progress.md 2026-07-11T19:19 entry), ollama-bench 242/242 pass. ruff/mypy/py_compile/shellcheck all clean. Commits: prompt-improve `6541fd8` (pushed to main); ollama-bench pending. **Lesson (systemPatterns):** the chain tail is never trustworthy as "weaker than head" without re-validation. Re-promoting the head = mandatory re-bench of all installed tail models that score ≥0.7 of the head in any sibling task. Round-18 will apply this rule to smart_trim / codeq_sum / code_gen / bug_finding chains (in progress at end of session).
