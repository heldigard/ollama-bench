# Memory Index
> Project: ollama-bench — vertical-slice CLI for local Ollama model evaluation

## Read First
- CONTEXT.md: current state (11 subcommands, 22-model lineup, harness wiring)
- REFERENCE.md: stable facts (CLI surface, scoring rubrics, leak patterns)
- systemPatterns.md: architectural decisions (vertical-slice, two-pass scoring)
- topics/local-ollama-lineup.md: 16 LLM winners + per-role map (re-bench 2026-07-04)
- topics/harness-wiring-2026-07-04.md: cross-CLI consumer → champion map (which tool runs which model) + live-env drift gotcha
- topics/bench-methodology.md: smoke → deep → tie-break → bug-finding pipeline (+ `--strip` think-strip mode, 14 leak patterns)
- topics/new-benchmarks-roadmap-2026-07-04.md: 8 new bench dimensions mapped to cross-cli consumers (tool_call landed)
- topics/new-models-bench-2026-07-04.md: 4 HF candidates benched — huihui = NEW bug_finding #1 (17.98 > 15.21)
- topics/quant-comparison-2026-07-04.md: Q4 vs Q8 evidence (Q4 is the ceiling)
- topics/ollama-0.23.2-gemma4-q4_0-incompat.md: resolved (Ollama 0.31.1 fixed it)

## Update Rules
- Decision -> systemPatterns.md
- Task done -> progress.md
- Failed approach -> dead-ends.md
- "Recuerda esto" -> activeContext.md or REFERENCE.md
- Deep context -> topics/<slug>.md
- 2026-07-04T15:30:00Z | status:live | ollama-bench is a public open-source Python CLI for evaluating local Ollama models. Public repo: https://github.com/heldigard/ollama-bench.

## Layout
```
.memory-bank/
├── MEMORY.md            (this file)
├── CONTEXT.md           current state (re-bench 2026-07-04)
├── REFERENCE.md         stable CLI / scoring facts (10 subcommands)
├── systemPatterns.md    architectural decisions
├── activeContext.md     recent handoff
├── currentTask.md       active focus
├── progress.md          bench history
├── dead-ends.md         failed approaches
└── topics/
    ├── local-ollama-lineup.md                  (16 winners, re-bench)
    ├── bench-methodology.md                    (4-stage pipeline)
    ├── quant-comparison-2026-07-04.md          (Q4 vs Q8 — Q4 ceiling)
    └── ollama-0.23.2-gemma4-q4_0-incompat.md   (resolved by Ollama 0.31.1)
```

## Out of scope (do NOT track here)
- `agent-sessions.md` — auto-managed by the home coordination registry, gitignored.
- Raw bench outputs — live in `~/.cache/ollama-bench/`, regenerable via CLI.