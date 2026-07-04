# New Benchmarks Roadmap (2026-07-04)

> **Question (user):** "what other cross-cli dynamics can use these models, and
> what new benchmarks do you need to classify them for those new tasks?"
>
> Cross-references the ecosystem map (agent audit 2026-07-04) against the
> current 5 deep tasks (+ bug_finding). Every row = a LOCAL-Ollama consumer in
> `~/.claude/` that is NOT yet covered by a bench task.

## Current coverage (already benched)

| deep task | cross-cli consumer(s) it covers |
|---|---|
| `improve` | prompt-improve hook, harness-proposer |
| `codeq_sum` | codeq summary/context/relations, project-memory maintain, ollama-summarize |
| `smart_trim` | smart-trim PreCompact hook |
| `web_synth` | web-research synthesis step |
| `code_gen` | on-demand code generation |
| `bug_finding` (separate slice) | diff-review, code-review bug hunting |

## New benchmarks needed (priority order)

### P0 — structured-output / ground-truth tasks (deterministic scoring, highest value)

1. **`tool_call`** — emit a valid JSON tool-call for a natural-language request
   + a tools schema. Score = `{valid_json, right_tool, right_args}`.
   - **Consumer**: agent-browser, n8n tool calls, MCP tool dispatch, Azure Functions bindings.
   - **Why P0**: tool-calling is the fastest-growing model use case; current bench
     has ZERO structured-output coverage. A model that writes great prose but
     emits broken JSON is unusable for agents.
   - **Scoring**: ground-truth (parse JSON + exact-match tool name + arg schema
     check). No keyword noise.

2. **`classification`** — classify a prompt into `{code, web, doc, trivial, security}`
   or an error into `{auth, timeout, config, syntax, network}`. Multi-class.
   - **Consumers**: prompt-router (41 routes), caveman-classify, error-classify,
     test-triage, n8n-lint error mapping.
   - **Why P0**: the harness runs classification on EVERY prompt (prompt-router
     stage 3). Mis-routing = wrong skill loaded = degraded answer. Currently
     zero bench coverage for the most-fired local-model role.
   - **Scoring**: macro-F1 + exact-match accuracy on a labeled set (≥30 items).

3. **`rerank`** — given a query + 10 candidate docs, return top-3.
   - **Consumer**: web-research rerank step (`search --smart`), search-swarm,
     memory semsearch re-ranking.
   - **Why P0**: rerank quality drives every "search → ground" workflow. nDCG@3
     vs a gold ranking.
   - **Scoring**: nDCG@3 (information-retrieval standard).

4. **`embedding_retrieval`** — proper eval of `embeddinggemma` vs `nomic-embed-text`
   vs any new embed model. MRR + recall@5 on a query→passage set.
   - **Consumer**: memory-semantic (semindex/semsearch), RAG, semrecall.
   - **Why P0**: the `embedding` slice is scaffolding only today; the real eval
     lives in a separate script. Embedding choice drives every semantic-search
     recall number in the harness.
   - **Scoring**: MRR + recall@k on a bilingual labeled set (the existing 12-query
     bilingual set used for the embeddinggemma win is the seed).

### P1 — quality tasks with rubric scoring

5. **`extract_fields`** — extract a structured field set from a PDF page / verbose
   dump (the pdf-extract-structured + extract-tool-output roles).
   - **Consumers**: pdf-extract-structured.py, extract-tool-output.py, error-classify.
   - **Scoring**: field-level precision/recall vs gold JSON (abstention counted
     as TN, not penalty — matches the pdf-extract contract).

6. **`draft_gen`** — generate a commit message / PR description from a diff.
   - **Consumers**: commit-draft.py, pr-draft.py, changelog-generator.
   - **Scoring**: Conventional-Commits format compliance + LLM-judge rubric
     (subject + body quality). Pairs with the existing `judge` slice.

7. **`judge_consistency`** — score the SAME input twice (temp>0); does the model
   give the same score? Reliability of the LLM-as-judge path.
   - **Consumer**: any feature using a local model as a judge / scorer.
   - **Scoring**: score-delta + Cohen's kappa across N repeats.

### P2 — harder, propose-only for now

8. **`multi_turn`** — 3-turn conversation; does the model retain earlier facts?
   Needs conversation state (new infra). Lower priority — the harness is mostly
   single-shot local calls.

9. **`reasoning`** — chain-of-thought correctness on verifiable problems (math,
     logic, off-by-one). Score = final-answer correctness (NOT reasoning trace).
   - **Why P2**: the bug_finding slice already exercises reasoning-on-code; a
     dedicated math/reasoning bench is lower marginal value for a code-centric
     harness.

## Think-strip unlock (2026-07-04, user-driven)

The bench now has a `--strip` mode (`deep --strip`) that strips
`<think>/<reasoning>/<reflection>/<output>/<|channel|>` traces before scoring,
and smoke tags leaky models `strippable=1` when their ONLY leaks are
thinking-trace tags. This UNLOCKS a whole class of strong reasoning models
previously hard-disqualified (DeepSeek-R1 distills, Qwen3-thinking, GPT-OSS,
LFM, Gemma-4 abliterated merges that leak `<|channel|>`).

**New bench task this enables**: `reasoning_stripped` — bench leaky reasoning
models on their CLEANED answer. Directly serves the user's ask: "modelos que
descartamos por thinking leaks podrían aprovecharse si limpiamos eso."

## Implementation order (proposed)

1. `tool_call` slice (P0, ground-truth, biggest gap) — next session.
2. `classification` slice (P0, highest fire-rate consumer).
3. Promote `embedding_retrieval` from scaffolding to real eval (P0).
4. `rerank` slice (P0).
5. `extract_fields` + `draft_gen` (P1, rubric — needs the LLM-judge upgrade first).

Each new slice = `features/<slice>/command.py` + register in `cli.py::_SLICES`
+ `tests/test_<slice>.py` (vertical-slice rule). Ground-truth slices come first
because they need no LLM-judge (deterministic, cheap, regression-proof).
