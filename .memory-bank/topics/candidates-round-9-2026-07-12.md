# Candidates Round-9 — 2026-07-12 (Qwythos dethrones batiai in codeq_sum)

## TL;DR

**`hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M` is the new codeq_sum #1.**
batiai/gemma4-e4b:q4 demoted to fallback. Qwythos also validated as **code_gen #2 fallback**
(close to lift). web_synth lost (Qwythos #4 vs xentriom Q8_0 #1) — no promotion.

| task | Qwythos rank | score | winner held | delta |
|---|---|---|---|---|
| **codeq_sum** | **#1 (NEW)** | 9.40 | batiai 9.19 | **+2.3%** |
| code_gen | #2 (NEW) | 10.38 | lift 10.52 | -1.3% (close fallback) |
| web_synth | #4 | 8.84 | xentriom Q8_0 10.19 | -13% (lose) |
| improve | n/a | n/a | OmniCoder held | not benched (3-7 score too tied to judge drift) |
| smart_trim | n/a | n/a | HauhauCS-Balanced held | not benched (OmniCoder -0.3% in tb) |

## Method

3-stage, all on RTX 5080 16GB with Ollama 0.31.2:

1. **smoke** — 1-prompt leak gate. Qwythos: ok, strippable=0, dt=4.46s, tps=6.1.
2. **tie-break** vs `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2` (improvement-champion). 5 tasks, harder prompts.
3. **deep** — 4-way focused validation per task where tie-break indicated upside:
   - codeq_sum vs `batiai/gemma4-e4b:q4`, `jaahas/crow:9b`, `SetneufPT/Qwopus3.5-4B-Coder-MTP`
   - web_synth vs `TeichAI/Fable-5-v1`, `xentriom/composer2.5-v2:Q8_0`, `cryptidbleh/gemma4-claude-opus-4.6`
   - code_gen vs `lift-GGUF`, `SetneufPT`, `huihui_ai/qwen3.5-abliterated:9b`

## Tie-break (Qwythos vs OmniCoder, hard prompts)

| task | Qwythos | OmniCoder | delta | notes |
|---|---|---|---|---|
| improve | 4.03 | 4.18 | -3.7% | OmniCoder held |
| **codeq_sum** | **9.93** | 8.13 | **+22%** | signal → validated in deep 4-way |
| smart_trim | 9.77 | 10.03 | -0.3% | tie (below HauhauCS champion) |
| **web_synth** | **9.88** | 7.98 | **+24%** | signal → false positive (OmniCoder not web_synth champ) |
| **code_gen** | **6.33** | 5.65 | **+12%** | signal → validated in deep 4-way |

Tie-break vs OmniCoder was MISLEADING for web_synth: OmniCoder is not the
champion there (xentriom Q8_0 is). When Qwythos went head-to-head vs the real
champion + 3 deep top-4, it dropped to #4.

## Deep 4-way validation (the deciding rounds)

```
codeq_sum:
  Qwythos                   9.40  #1 (NEW, dethrone)
  batiai/gemma4-e4b:q4      9.19  #2 (fallback)
  SetneufPT/Qwopus3.5-4B    8.99
  jaahas/crow:9b            8.87

web_synth:
  xentriom/composer2.5:Q8_0 10.19  #1 (held; promoted from #2 to #1 deep-4-way)
  cryptidbleh/gemma4-opus   10.08  #2
  TeichAI/Fable-5-v1         9.92  #3 (was #1 round-7 combined; demoted)
  Qwythos                    8.84  #4

code_gen:
  lift-GGUF                 10.52  #1 (held)
  Qwythos                   10.38  #2 (close fallback candidate)
  SetneufPT/Qwopus3.5-4B    10.18
  huihui_ai/qwen3.5-ab9b    10.18
```

## What about the other 7 candidates (rejected pre-bench)?

| candidate | reason rejected pre-bench |
|---|---|
| `empero-ai/Qwable-9B-Claude-Fable-5-GGUF` | WebFetch no response (URL inaccessible, cannot verify) |
| `Reza2kn/Cosmos3-Nano-INT4-AWQ` | text-to-image/video; NOT LLM. Out of scope. |
| `DuoNeural/Cosmos3-Nano-GPTQ-4bit` | Mixture-of-Transformers video; custom nibble format. Out of scope. |
| `ProCreations/grug-9b` | Qwen3.5-9B finetune (Ornith-1.0-9B). Round-8 confirmed same-base finetunes lose vs round-7 champions. Skip. |
| `GnLOLot/MiniCPM5-1B-Claude-Opus-Fable5-Thinking` | No GGUF in repo (Safetensors only). Would need conversion. Cost > niche value (lineup has Negentropy-4B for low-VRAM). Skip. |
| `microsoft/GELab-Zero-4B-preview-Sico-Evolution` | GUI agent for Copilot/Edge. Bench is coding/reasoning/general. Out of scope unless new `gui_nav` task defined. |
| `ShaunGves/FastContext-1.0-4B-SFT` | Repo-explorer subagent. Useful but no slot in current 5-task lineup. Would require new task + smoke + bench. Skip pre-bench (YAGNI for now). |
| `google/gemma-4-E4B-it-qat-q4_0-gguf` (official) | **OLLAMA PULL FAILURE**: 4/4 GGUF chunks download (5.2GB + 991MB + 159B + 52B) but final 400 error during manifest registration. HF API says `gated:false`, Ollama refuses. Likely requires explicit Google license acceptance via Ollama not exposed via CLI flag. blocker NOT resolved — batiai community-fork remains primary upstream-validated option until Ollama 0.32+ or HF token changes gating. |

## Wiring updates applied (round-9)

Single source of truth: `~/ollama-bench/RANKING.md` + `src/ollama_bench/shared/config.py`.

- `src/ollama_bench/shared/config.py:42` → `primary_model_default = "hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M"` (was batiai)
- `src/ollama_bench/shared/config.py:43` → `fallback_model = "batiai/gemma4-e4b:q4"` (was SetneufPT)
- `src/ollama_bench/shared/config.py:44` → NEW `tertiary_model = "SetneufPT/Qwopus3.5-4B-Coder-MTP_Q4_64k_8GB-GPU:latest"`
- `RANKING.md` line 13 (wiring table), line 43 (deep #1 row), line 138 (`## Per-task PRIMARY` table) all updated
- `~/.zshrc:1134` → `export CODEQ_SUMMARY_MODEL="hf.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF:Q4_K_M"` (was batiai)
- `agent-memory maintain` reads `CODEQ_SUMMARY_MODEL` per `rules/code-intelligence-tools.md` → stays aligned automatically
- `model-drift-check.py` checks `src/ollama_bench/shared/config.py` primary against RANKING.md → tests/test_config_drift.py updated model: 6/6 pass

## Installed lineup delta

Before round-9: 22 models. After: 23 (Qwythos added; no deletions; batiai held as fallback).

## Decision matrix (next round trigger)

| condition | action |
|---|---|
| Round-10 finds a Qwythos 4B / 1B-2B low-VRAM variant that beats Negentropy-4B (3GB) in codeq_sum | add low-VRAM backup |
| Official `google/gemma-4-E4B` ollama pull works (new tag or new Ollama release) | re-bench vs Qwythos in codeq_sum (potential 3-way race) |
| Qwythos loses to anything in round-10 re-bench of codeq_sum | demote, restore batiai |
| `web_synth` xentriom Q8_0 12GB proves too heavy for shared hosting | promote Qwythos as web_synth fallback if tie-break still wins on lighter prompts |