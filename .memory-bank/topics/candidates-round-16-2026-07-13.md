# Candidate screen round 16 — quality-first (2026-07-13)

## Decision rule

Throughput and disk size are secondary. A candidate changes a live role only
after it passes smoke, beats the relevant installed champion on task quality,
and repeats that advantage in a fresh controlled comparison. Ties and one-run
signals do not rewire a consumer.

## Tested candidates

| Candidate | Relevant result | Decision |
|---|---|---|
| `empero-ai/Qwythos-9B-v2-GGUF:Q4_K_M` | Smoke clean. `codeq_sum` 9.35 vs installed Qwythos 9.39; `code_gen` 10.46 vs 10.38 only against its own predecessor, not the role champion. | Reject / delete: no material quality win. |
| `batiai/Qwen3-Embedding-4B-GGUF:Q6_K` | MRR 0.938, recall@5 1.000. `embeddinggemma` and `bge-m3` both remain 1.000 / 1.000. | Reject / delete: lower retrieval precision. |
| `batiai/Granite-4.1-8B-GGUF:Q4_K_M` | Smoke clean. Isolated `improve` signal 3.00, but fresh 3-way replication 2.33 vs TeichAI 2.46 and Negentropy 2.03. | Reject / delete: quality advantage did not replicate. |

Artifacts: `~/.cache/ollama-bench/results/{qwythos_v2,batiai_qwen3_embedding4,granite}_round16_*`.

## Screened but not benchmarked

- `batiai/gemma-4-E2B-it-GGUF`, `batiai/gemma-4-E4B-it-GGUF`, and
  `batiai/LFM2.5-8B-A1B-GGUF` duplicate families already measured locally.
  LFM also needs a clean-output compatibility gate before it can serve any
  contract-sensitive role.
- `batiai/Qwen3-Reranker-{0.6B,4B,8B}-GGUF` now have deterministic nDCG@3/MRR@3
  coverage through the `rerank` slice. The first Q6 4B run is rejected before
  quality comparison: Ollama exposes it with embedding/tools/thinking capability
  but rejects completion, while the existing local rerank consumer uses a
  completion contract. Do not wire it unless the consumer adopts a compatible
  native reranking API and that API is independently benched.
- The remaining Qwen embedding variants cannot improve the current tiny suite
  by inference: the 4B model lost to an existing 1.000 MRR baseline. Test a
  larger variant only after a harder multilingual retrieval set exists.
- `Flux`, `Moondream`, `Fara`, `MIRA`, `batisee`, and `batisay-*` are image,
  vision, or ASR models. They require their respective benchmark slices, not
  text-generation comparison.
- Ornith, Dolphin, Heretic variants, and unquantized/base-only models remain
  outside the general harness lineup until a role-specific bench is available.
  Abliterated or uncensored variants must not enter security, judge, or shared
  context routes merely because they pass smoke.

## Live wiring

No primary or fallback changed in this round. `smart_trim` remains
SC117 -> HauhauCS under the quality-first policy; E2B is not wired from its
single-round signal.
