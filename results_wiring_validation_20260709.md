# Wiring Validation - 2026-07-09

Ollama 0.31.2, seed 42, two response sets per role plus a fresh final run. The
benchmark uses each consumer's protocol (`chat-fallback` for prompt improvement
and compaction; `generate` for code summaries). The final scorer caps speed at
0.25, applies proportional length penalties, rejects ungrounded files/stacks,
scores alternative semantic phrasings, and weights authority, error-branch,
security, and verification cases at 2x.

## Results

| role | model | run 1 | run 2 | protocol | decision |
|---|---|---:|---:|---|---|
| improve | cryptidbleh/gemma4-claude-opus-4.6 | 3.50 | 3.50 | chat-fallback | PRIMARY |
| improve | Negentropy Opus 4.7 9B | 2.70 | 2.70 | chat-fallback | FALLBACK |
| improve | Qwopus3.5-4B | 1.94 | 1.94 | chat-fallback | third |
| codeq_sum | batiai/gemma4-e4b | 9.18 | 9.18 | generate | PRIMARY |
| codeq_sum | Qwopus3.5-4B | 8.99 | 8.99 | generate | FALLBACK |
| codeq_sum | jaahas/crow:9b | 8.87 | 8.87 | generate | not wired |
| smart_trim | batiai/gemma4-e2b | 11.81 | 11.81 | chat-fallback | PRIMARY |
| smart_trim | cryptidbleh/gemma4-claude-opus-4.6 | 11.63 | 11.63 | chat-fallback | SECONDARY |
| smart_trim | SC117/heretic-QAT | 10.79 | 10.79 | chat-fallback | not wired |

## What Changed

The prompt incident is now one of four fidelity cases: grounded ranking,
read-only scope, cross-project ownership, and absent conversation context.
Code summaries now distinguish cache-hit fallback from cache-miss rethrow and
check exception invariants. Compaction cases preserve superseded/current model
state, negative secret constraints, and partial verification.

The two stored response sets produce identical final rankings. A fresh run also
kept the same order (improve 2.97/2.03, codeq 9.18/8.99, smart_trim 11.81/11.63),
showing that small score movement does not change the wiring decision.

Raw TSV/Markdown/detail JSONL artifacts remain under
`~/.cache/ollama-bench/results/wiring_*_{semantic_r1,semantic_r2,final_r1}*`.
