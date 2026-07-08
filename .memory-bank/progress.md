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
