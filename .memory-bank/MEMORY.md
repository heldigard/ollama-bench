# Memory Index
> Project: ollama-bench — vertical-slice CLI for local Ollama model evaluation

## Read First
- CONTEXT.md: current state (active subcommands, model lineup snapshot)
- REFERENCE.md: stable facts (CLI surface, scoring rubrics, leak patterns)
- systemPatterns.md: architectural decisions (one-process, multi-command)
- topics/ollama-0.23.2-gemma4-q4_0-incompat.md: critical Ollama version incompatibility
- topics/local-ollama-lineup.md: validated lineup (per-role winners)
- topics/bench-methodology.md: leak gate first, multi-prompt second

## Update Rules
- Decision -> systemPatterns.md
- Task done -> progress.md
- Failed approach -> dead-ends.md
- "Recuerda esto" -> activeContext.md or REFERENCE.md
- Deep context -> topics/<slug>.md
- 2026-07-04T15:30:00Z | status:live | ollama-bench is a public open-source Python CLI for evaluating local Ollama models. Public repo: https://github.com/heldigard/ollama-bench. Package name on PyPI: ollama-bench.

## Layout
```
.memory-bank/
├── MEMORY.md            (this file)
├── CONTEXT.md           current state
├── REFERENCE.md         stable CLI / scoring facts
├── systemPatterns.md    architectural decisions
├── activeContext.md     recent handoff
├── currentTask.md       active focus
├── progress.md          bench history
├── dead-ends.md         failed approaches
└── topics/
    ├── local-ollama-lineup.md                 (copied from ~/.memory-bank)
    ├── bench-methodology.md                   (NEW)
    └── ollama-0.23.2-gemma4-q4_0-incompat.md  (copied from user memory)
```