"""embedding_retrieval — MRR + recall@5 eval for embedding models.

Ground-truth bench: each case has a query + N passages (one GOLD relevant, the
rest distractors). The embed model embeds the query + every passage; we rank
passages by cosine similarity to the query and score MRR (1/rank of the gold)
+ recall@5. This is the bench the harness needs for every semantic-search role
(memory-semantic semsearch/semrecall, RAG, semindex) — and the one that decides
whether bge-m3 (1024-d multilingual #1) justifies re-indexing vs the 768-d
embeddinggemma incumbent.

Hand-rolled cosine (no numpy dep — the package stays stdlib-only).

# vs-soft-allow  — end-to-end pipeline (cases -> embed -> rank -> MRR -> report).
"""

from __future__ import annotations

import argparse
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ollama_bench.shared.ollama import embed
from ollama_bench.shared.paths import result_path

# Each case: query + passages (1 gold at gold_idx, rest distractors). Bilingual
# (ES/EN) + harness-domain coverage so the winner is best for memory-semantic
# retrieval, not a generic benchmark.
CASES: list[dict] = [
    {
        "id": "code_chunk",
        "query": "function that splits text into token-bounded chunks",
        "passages": [
            "chunkText splits the input into buffers whose word count stays under maxTokens, flushing on overflow.",
            "sendChatMessage posts the trimmed draft to /chat and clears the field on success.",
            "validate_email returns False for None/empty/whitespace inputs using a stdlib re pattern.",
            "get_models fetches /api/tags and returns the installed model list.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "codeq_config",
        "query": "how do I set the model codeq uses for its summary enrichment",
        "passages": [
            "CODEQ_SUMMARY_MODEL env var selects the Ollama model for codeq summary/context/relations.",
            "OLLAMA_URL overrides the daemon base URL (default http://localhost:11434).",
            "seed=42 is pinned in CallOpts so bench runs are reproducible.",
            "think must stay TOP-LEVEL in the request body, not inside options.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "n8n_error",
        "query": "n8n Dynamics 365 error code 0x80072530",
        "passages": [
            "0x80072530 means a PATCH was sent without a body — include the entity payload.",
            "HTTP 401 in n8n usually means the service connection credentials expired.",
            "An inactive workflow won't trigger on schedule — activate it first.",
            "Timeout errors often point to a slow downstream API or a hung node.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "azure_func",
        "query": "azure functions python v2 programming model trigger setup",
        "passages": [
            "The Python v2 model uses the function_app decorator to register HTTP/timer/queue triggers.",
            "host.json configures logging and retry options for the whole function app.",
            "local.settings.json stores local dev app settings and is NOT committed to git.",
            "requirements.txt lists the Python deps the Azure Functions runtime installs.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "prompt_es",
        "query": "como mejoro un prompt vago del usuario",
        "passages": [
            "El hook prompt-improver reescribe prompts vagos cortos en specs estructurados antes de enrutar.",
            "smart-trim comprime el contexto en bullets de handoff al compactar.",
            "codeq summary da orientacion de 1 linea sobre el cuerpo de una funcion.",
            "web-research sintetiza multiples fuentes en un resumen citado.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "memory_loc",
        "query": "where do architectural decisions get recorded in the memory bank",
        "passages": [
            "systemPatterns.md holds durable architectural decisions and the reasoning behind them.",
            "progress.md tracks task completion status over time.",
            "currentTask.md captures the active focus for resuming work.",
            "activeContext.md stores recent handoff notes and live state.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "leak_strip",
        "query": "model emits thinking tags inside its answer field",
        "passages": [
            "detect_leaks flags <think>/<reasoning>/<output>/<|channel|> tags; leaks_are_strippable marks salvageable ones.",
            "seed=42 pins reproducible generation in CallOpts.",
            "num_ctx defaults to 4096 to keep responses cheap and avoid OOM.",
            "temperature 0.2 is the default sampling temperature for generation.",
        ],
        "gold_idx": 0,
    },
    {
        "id": "list_tuple",
        "query": "what is the difference between a python list and a tuple",
        "passages": [
            "A list is mutable (modifiable after creation); a tuple is immutable.",
            "A dict maps keys to values via a hash table.",
            "A set is an unordered collection of unique elements.",
            "A deque is a double-ended queue with fast pops from both ends.",
        ],
        "gold_idx": 0,
    },
]


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity, hand-rolled (no numpy). 0 if either is zero-vector."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b, strict=True):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / math.sqrt(na * nb)


def eval_model(model: str, timeout: int = 60) -> dict:
    """Embed all queries + passages for the model; return per-case ranks + MRR."""
    cases_out: list = []
    mrr_sum = 0.0
    recall5_sum = 0.0
    for c in CASES:
        q = embed(model, c["query"], timeout=timeout)
        if "err" in q:
            return {"model": model, "err": q["err"]}
        qv = q["vec"]
        sims: list[tuple[float, int]] = []
        for idx, p in enumerate(c["passages"]):
            pv = embed(model, p, timeout=timeout)
            if "err" in pv:
                return {"model": model, "err": pv["err"]}
            sims.append((_cosine(qv, pv["vec"]), idx))
        sims.sort(key=lambda t: -t[0])
        gold = c["gold_idx"]
        rank = next((i + 1 for i, (_, idx) in enumerate(sims) if idx == gold), len(sims) + 1)
        mrr_sum += 1.0 / rank
        recall5_sum += 1.0 if rank <= 5 else 0.0
        cases_out.append({"id": c["id"], "rank": rank})
    n = len(CASES)
    return {
        "model": model,
        "mrr": round(mrr_sum / n, 3),
        "recall5": round(recall5_sum / n, 3),
        "cases": cases_out,
    }


def cmd_embedding_retrieval(args: argparse.Namespace) -> int:
    """`ollama-bench embedding-retrieval` entry point."""
    models = args.models or []
    if not models:
        print("ERROR: --models required", file=sys.stderr)
        return 2
    print(
        f"# Embedding-retrieval bench: {len(models)} models x {len(CASES)} cases", file=sys.stderr
    )
    results: list = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(eval_model, m): m for m in models}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {"model": m, "err": str(e)}
            results.append(r)
            print(f"  [{i:2d}/{len(models)}] {m[:55]}  done", file=sys.stderr, flush=True)
    results.sort(key=lambda r: -r.get("mrr", -1.0))

    out_path = Path(args.output) if args.output else result_path("embedding_retrieval", ext="md")
    with out_path.open("w") as f:
        f.write("# Embedding-Retrieval Bench — MRR + recall@5 (bilingual, 8 cases)\n\n")
        f.write("Scoring: per case, rank the gold passage by cosine(query, passage); ")
        f.write("MRR = mean(1/rank), recall@5 = fraction gold in top-5.\n\n")
        f.write("| # | MRR | recall@5 | Model |\n|---|---|---|---|\n")
        for i, r in enumerate(results, 1):
            if "err" in r:
                f.write(f"| {i} | err | err | `{r['model']}` — {r['err'][:40]} |\n")
            else:
                f.write(f"| {i} | {r['mrr']:.3f} | {r['recall5']:.3f} | `{r['model']}` |\n")
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent: argparse.ArgumentParser) -> None:
    p = sub.add_parser(
        "embedding-retrieval",
        parents=[parent],
        help="Embedding eval — MRR + recall@5 on a bilingual retrieval set (ground-truth).",
    )
    p.add_argument("-m", "--models", nargs="+", required=True, help="Embedding models to bench.")
    p.add_argument("-o", "--output", help="Output MD path (default: cache dir).")
    p.set_defaults(cmd=cmd_embedding_retrieval)
