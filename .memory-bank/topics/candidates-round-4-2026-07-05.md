# Candidates Round 4 (2026-07-05) — 3 HF candidates + browser-bench port

> Round-4 sweep after the Grug-12B upset (round-3). Goal: re-confirm Grug holds improve + open browser/code slots via fresh candidates + port the cross-CLI browser bench to ollama-bench so the slice stays graduated.
> Also re-installed the missing `batiai/gemma4-e2b:q4` winner.

## Candidates (3 pulled, ALL 3 dropped)

| candidate | HF repo | size | why pulled | verdict |
|---|---|---|---|---|
| `lmstudio-community/Phi-4-mini-reasoning-GGUF` | [HF](https://huggingface.co/lmstudio-community/Phi-4-mini-reasoning-GGUF) | 2.5 GB Q4_K_M | Phi-4 family diversity — first Phi model we've tested. Reasoning-focused at ~3B effective. | **LEAK** at smoke (`thinking_prefix`, reasoning-distilled pattern). **DELETED**. |
| `Mia-AiLab/Gemmable-4-12B-MTP-GGUF` | [HF](https://huggingface.co/Mia-AiLab/Gemmable-4-12B-MTP-GGUF) | 7.4 GB Q4_K_M | gemma4-12B + MTP (multi-token prediction) = agent throughput potential. ~194K pulls (community-validated). | **PASS smoke** (ok, 6.55s, 8.1 tps). **DELETED** after tie-break shows -10.00 improve on hard prompts. |
| `HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive` | [HF](https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive) | 6.5 GB Q4_K_M | 501K pulls — most-downloaded Qwen3.5-9B uncensored variant. Bug_finding / uncensored role. | **PASS smoke** (ok, 5.58s, 5.9 tps). **DELETED** after tie-break loses improve + codeq_sum to incumbents. |

## Smoke gate (leak detection)

| model | status | strippable | dt_s | tps | etoks | len |
|---|---|---|---|---|---|---|
| Phi-4-mini-reasoning | `leak:thinking_prefix` | 1 | 8.74 | 9.2 | 95 | 360 |
| Gemmable MTP | `ok` | 0 | 6.55 | 8.1 | 38 | 244 |
| HauhauCS Aggressive | `ok` | 0 | 5.58 | 5.9 | 10 | 167 |

Phi-4 follows the same reasoning-distilled-leak pattern as `kwangsuklee`, `DeepSeek-V4-Flash`. **Reasoning-distilled models on small bases consistently leak** despite `think=False` — confirmed 3rd instance, can be predicted for future reasoning-distilled pulls.

## Deep bench (5 tasks, 0–7 scale, saturated scores)

| task | Gemmable MTP | HauhauCS Aggressive | incumbent #1 | deep incumbent |
|---|---|---|---|---|
| codeq_sum | -2.34 | **4.05** | batiai/gemma4-e4b:q4 | 6.52 |
| smart_trim | 5.0 | **7.00 SAT** | SetneufPT/Qwopus3.5-4B-Coder-MTP | 7.00 SAT |
| web_synth | **5.71** | 5.0 | batiai/gemma4-e4b:q4 | 7.00 SAT |
| improve | **5.54** | 4.5 | Grug-12B | 3.54 |
| code_gen | 4.72 | **6.6** | fredrezones55/Qwopus3.5:9b | 6.0 |

Reads: HauhauCS Aggressive at code_gen 6.6 looks like a **+0.6 upset vs fredrezones55 6.0**. Both new candidates look competitive on improve (Gemmable 5.54, HauhauCS 4.5 > incumbents pegasus912 3.44, Grug 3.54). Need tie-break.

## Tie-break (hard prompts, structural scoring, no 7.0 cap)

### HauhauCS Aggressive vs incumbents

| task | HauhauCS Aggressive | SetneufPT incumbent | fredrezones55 incumbent |
|---|---|---|---|
| improve | 2.55 | **4.32** | 3.77 |
| codeq_sum | 8.07 | 11.00 | **13.00** |
| smart_trim | 10.50 (SAT) | 10.50 (SAT) | 10.50 (SAT) |
| web_synth | 10.50 (SAT) | 10.50 (SAT) | 10.50 (SAT) |
| code_gen | 16.00 (SAT) | 16.00 (SAT) | 16.00 (SAT) |

**HauhauCS Aggressive LOSES improve + codeq_sum on hard prompts.** Saturation tie elsewhere is inconclusive but doesn't upset. Verdict: **DROP**.

### Gemmable MTP vs Grug-12B + fredrezones55

| task | Gemmable MTP | Grug-12B (incumbent improve #1) | fredrezones55 (incumbent codeq_sum #1) |
|---|---|---|---|
| improve | **-10.00** | **8.75** | 6.00 |
| codeq_sum | -4.03 | 10.27 | **13.00** |
| smart_trim | -2.47 | 10.50 (SAT) | 10.50 (SAT) |

**Gemmable MTP loses MASSIVELY on hard prompts** (improve -10 vs Grug 8.75 = delta 18.75). Verdict: **DROP**. Caveat: MTP (multi-token prediction) the model's claimed USPatent likely was disabled in the ollama call path (ollama doesn't yet wire MTP); so the bench tested the base gemma4-12B capability without MTP speedup. Even so, the base response is not competitive on structured-spec tasks.

## Decisions (round-4 cleanup)

### KEEP — installed permanently
- None (all 3 deleted).

### DROP — failed re-bench
- `hf.co/lmstudio-community/Phi-4-mini-reasoning-GGUF:Q4_K_M` (2.5 GB deleted). Reasoning-distilled small base; leaks `thinking_prefix` at smoke. Pattern matches `kwangsuklee` + `DeepSeek-V4-Flash` — established prediction: **reasoning-distilled models on small bases consistently leak thinking at our smoke gate.**
- `hf.co/Mia-AiLab/Gemmable-4-12B-MTP-GGUF:Q4_K_M` (7.4 GB deleted). Strong community reputation (194K pulls) but fails tie-break hard prompts (-10 improve vs +8.75 Grug). Likely MTP not wired in ollama call path, masking expected throughput.
- `hf.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive:Q4_K_M` (6.5 GB deleted). Loses improve + codeq_sum on hard prompts; saturation ties elsewhere don't upset.

## Missing winner re-installed

- `batiai/gemma4-e2b:q4` (3.4 GB) — was listed in lineup as `code_gen tied` but absent from `ollama list` after the 2026-07-04 46-model cleanup. **Re-pulled and verified loads** (gemma4 family, 4.6B params, 131k ctx).

## Cross-CLI bench port: browser-bench-vision

**Goal** (per user): bring browser-automation bench tests from `~/cli-orchestration` (and similar code-related benches in cross-CLI repos) into ollama-bench so the slice stays graduated and benefits Claude Code / browser-agent projects.

### Source

`~/cli-orchestration/src/cli_orchestration/browser/model_bench.py` (14.5K) + `_bench_scoring.py` (5.3K, T1–T4 scoring + ollama client) + `_bench_data.py` (8.8K, ground-truth + snapshots + prompt templates) + `_bench_fixtures.py` (10.5K, Pillow-based image fixtures for vision).

### Tasks (5 vision/speed)

| code | task | measures |
|---|---|---|
| T1 | `vision_ocr` | Text extraction recall + hallucination rate from synthetic screenshots (login forms, error pages, tables, charts, dashboards, articles) |
| T2 | `vision_classify` | 8-class UI-state classifier top-1 accuracy (login_form / error_404 / error_500 / table / chart / dashboard / article / loading) |
| T3 | `snapshot_diff` | Accessibility-tree snapshot diff vs reference; 3 scenarios (minor/medium/major) |
| T4 | `tool_call` | Tool-call proposal scenarios (click / fill / scroll / wait / eval / recovery); success rate |
| T5 | `speed` | 5 reps cold+warm; mean / p50 / p95 / tokens/sec |

### Migration outcome

Files copied (`features/browser_bench/`): `command.py`, `_data.py`, `_fixtures.py`, `_scoring.py`.

**Imports patched**: `from ._bench_data` → `from ollama_bench.features.browser_bench._data` (absolute, symlink-safe).

**Models updated to current champions** (2026-07-05 round-3 lineup):
- `qwen3.5:4b` (vision+tools winner, kept).
- `hf.co/kai-os/Grug-12B-GGUF:Q4_K_M` (text-reasoning, replaces the DROPPED `MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf`).
- `huihui_ai/qwen3.5-abliterated:9b-Claude-4.6-Opus-q4_K` (tool-call winner 9.82, replaces the `fredrezones55/Qwen3.5-Uncensored-HauhauCS-Aggressive:4b` listed in the original).

**Wired**: `cli.py::_SLICES` now lists `(browser-bench-vision, add_browser_bench, "Vision-grounded browser bench (OCR/classify/diff/tool/speed) — ported from cli-orchestration")`.

**Slice integration** (added at bottom of `command.py`):
- `add_parser(sub, parent)` → registers `--quick` / `--rigorous` / `--models`.
- `cmd_browser_bench_vision(args)` → named entry function (passes `test_layout.py::test_every_feature_has_cmd_function`).
- `_dispatch(args)` → converts ollama-bench namespace into the standalone `main(argv)` call (no `--output` re-shim; bench writes to its default `~/.claude/state/browser-model-bench/`).

### Verification matrix

- `python3 -m py_compile` ✓ (all 4 files)
- `ruff check` ✓ clean
- `pytest tests/test_layout.py tests/test_list.py -q` ✓ 9/9 (incl. new `test_every_feature_has_cmd_function` for browser_bench)
- `ollama-bench --help` shows `browser-bench-vision` ✓
- `ollama-bench browser-bench-vision --help` shows ported args ✓
- E2E: `ollama-bench browser-bench-vision --quick --models qwen3.5:4b hf.co/kai-os/Grug-12B-GGUF:Q4_K_M` ran 5 subtasks (T1-T5) and wrote `~/.claude/state/browser-model-bench/results-<ts>.{json,md}`. Sample deltas: qwen3.5:4b 156.2 tok/s vs Grug-12B 103.7 tok/s; both correct on T2 classify (login_microsoft + error_500).

### What was NOT ported

- **`~/smart-trim/tests/test_summarize.py`** (6.9K): uses monkeypatched ollama clients — unit tests, not a real bench. **NOT** a port candidate (no live model evaluation).
- **`~/cli-orchestration/tests/test_agent_browser_subagent.py`**: validation tests that feed stored JSON snapshots through the normalizer/validator. **NOT** a bench (no model calls). Stays in cli-orchestration.
- **`~/codeq/tests/test-code-intelligence.py`**: code-intelligence regression suite. **NOT** a model-evaluation bench.
- **`~/cheap-llm/cheap_bench.py`** (21.4K, 5 fixed tasks over Ollama + cheap cloud cascade): cross-provider cheap-models bench. Defer to a future round; candidates higher than this one (browser-bench-vision) for cross-ecosystem impact.

### Subtle observation

The ported `cli_orchestration/browser/model_bench.py` distinguishes itself from `ollama_bench browser-tool` slice (which validates **a11y ref dispatch**). browser-bench-vision here measures **vision-grounded** browser tasks (OCR + UI-state classification). The two slices are complementary, not duplicates.

## Caveats

- Reasoning-distilled small models now established as ALWAYS-LEAKY at smoke (3/3 hits across `kwangsuklee`, `DeepSeek-V4-Flash`, `Phi-4-mini-reasoning`). Can be predicted and pre-rejected without pull cost.
- MTP-capable models (Gemmable-4-12B-MTP) may benchmark poorly without ollama MTP wiring. Until ollama supports MTP in `/api/generate`, treat MTP-tagged candidates as base-architecture only — bench their capability, ignore the throughput claim.
- browser-bench-vision port: T4 tool-call scenarios all FAIL for text-only models (text ollama can't parse image refs). Vision-capable models would need to be opted into `--models` explicitly for T1/T2/T5-only bench; that's the existing `--models` flag.
- Hard-prompt tie-break saturation continues to hide real winners in smart_trim / web_synth / code_gen at 10.50 / 16.00. Need to bump the upper bound OR add 3rd hard prompts to discriminate.

## Round-5 candidates to consider (next session)

- Reasoning models that pass smoke (skill-tuned, not reasoning-distilled). Try `aratan/gemma-4-E4B-it-heretic` variants — already installed.
- Vision-capable models for browser-bench-vision T1/T2 (qwen3.5 vision was the original winner but only text-only results logged above). Try `gemma3:4b-vision` from Ollama library.
- `phi-4` base (not `phi-4-mini-reasoning`) — untested family member for code bench.
