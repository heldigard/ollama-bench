# benchmark-refactor-2026-07-08
> Deep memory topic. Read on demand; keep entries factual.


## 2026-07-08T01:39:45Z
2026-07-08 benchmark refactor complete. New canonical task scorers replace saturating first_pass_score for deep: improve/codeq_sum/smart_trim/web_synth/code_gen now use 18 total varied cases, task-specific metrics, detail JSONL, discrimination stats. Smoke now skips bge-* embeddings and deep includes strippable reasoning leaks by default after cleaning; --strict-clean preserves legacy exclusion. Rebench on 20 generative models: improve SetneufPT 6.60; codeq_sum jaahas/crow 9.23; smart_trim fredrezones55/Qwopus3.5 11.25; web_synth aratan/gemma-4-E4B-it-heretic Q6 12.50 tied with cryptidbleh opus; code_gen zfujicute/OmniCoder 11.65. Specialized benches: tool/browser/pdf_extract all led by functiongemma; bug_finding led by zfujicute; embeddings tied embeddinggemma + bge-m3 MRR 1.0. Runtime output cleaning policy propagated to shared ollama_client, agent-memory, cheap-llm, cli-orchestration. Residual: tool_call/browser_tool still near-saturated below #1, need multi-turn/retry adversarial cases.
