#!/usr/bin/env python3
"""Embedding retrieval eval: does the RIGHT doc rank first for a semantic query?

This is the metric that matters for the ecosystem's embedding use (semantic
memory recall in .memory-bank, web-research rerank) — NOT generative quality.
Queries are SEMANTIC PARAPHRASES (few shared words with the target) so a good
embedder wins on meaning, a weak one on keyword overlap.

Per model: recall@1, recall@3, MRR, dim, total embed time, avg latency."""
import json, math, time, urllib.request

OLLAMA = "http://localhost:11434"

# 12 realistic memory-bank-style chunks across the ecosystem domains
CORPUS = [
    "Authentication uses JWT tokens. verify_jwt() checks token expiry against current time; refresh_token() issues new access tokens. Login sessions persist via httpOnly cookies set at sign-in.",
    "n8n workflow fails on Dynamics 365 PATCH: error 0x80072530 means a PATCH with empty body. Wrap the HTTP node in a NodeApiError catch to handle credential or URL problems.",
    "Azure Functions deploy via the AzureFunctionApp@1 pipeline task. Run locally with func start. Never do a manual zip-push deploy without explicit user opt-in — pipeline is the default.",
    "Local Ollama models were benchmarked across 6 rounds. qwen3.5:4b is the universal default (clean, fast, 3.4GB). Reasoning-distilled models leak chain-of-thought under think=False and were pruned.",
    "The Edit tool writes LF line endings; if HEAD has CRLF, every diff shows ^-{CRLF}/^+{LF} noise. Fix with git-eol-check.py --fix and declare a .gitattributes eol policy.",
    "Python files require mandatory type hints on all params and returns. Run ruff check scoped to modified files only; the auto-format hook formats each edited .py per-file. Validate the repo with ruff format --check .",
    "Test runners must run with bounded workers (--max-workers=1 on WSL2), --watch=false, and a wall-time timeout cap. Unbounded defaults saturate the CPU to 100% for minutes.",
    "Each project has its own .memory-bank/. semsearch embeds chunks with a local embedding model and ranks by numpy cosine similarity; the index re-embeds only files whose mtime changed.",
    "RTK compresses verbose command output ~60-90%. Never wrap test runners or git diff/show — their structured failure output and ^+/^- anchors must stay raw for the model to parse.",
    "The Supabase MCP is read-only. Verify RLS policies before any schema change. Use execute_sql for queries and get_advisors(type=security) to audit.",
    "Web research uses a local-first stack: SearXNG at :8080 is the primary engine, with Z.AI/MiniMax as fallback and a local Ollama model for rerank. web-research.py orchestrates search/read/research.",
    "Swarm fans out a task to several PAYG models in parallel; the Fusion API is web-grounded. The controller synthesizes a 5-field analysis (consensus, contradictions, gaps, unique insights, blind spots).",
    # --- Spanish chunks (the ecosystem memory-bank is bilingual ES/EN) ---
    "La autenticación utiliza tokens JWT. La función verify_jwt() comprueba la expiración del token contra la hora actual; refresh_token() emite nuevos tokens de acceso. La sesión del usuario persiste mediante cookies httpOnly al iniciar sesión.",
    "El deploy de Azure Functions se hace con la tarea AzureFunctionApp@1 del pipeline. Localmente se prueba con func start. Nunca se debe hacer un zip-push manual sin autorización explícita del usuario; el pipeline es la vía por defecto.",
    "Los hooks bloquean operaciones destructivas: rm -rf /, git push --force a main, DROP de tablas. block-dangerous.sh intercepta comandos peligrosos antes de que se ejecuten y protege además archivos sensibles como .env y *.pem.",
    "La memoria del proyecto vive en .memory-bank/. Las decisiones de arquitectura se guardan en systemPatterns.md; el progreso de tareas en progress.md; el contexto activo en activeContext.md. Cada proyecto tiene su propio banco aislado.",
]
# 12 semantic queries (8 EN + 4 ES) — paraphrases, target = CORPUS index
QUERIES = [
    ("how do users stay signed in across requests", 0),
    ("the CRM integration step broke on update", 1),
    ("how to ship my serverless code to the cloud", 2),
    ("which local AI runs fastest for trivial jobs", 3),
    ("why does my commit show strange line-ending changes", 4),
    ("require signatures on python function params", 5),
    ("my unit tests freeze the whole machine", 6),
    ("look up notes by meaning instead of exact words", 7),
    # Spanish semantic queries → target Spanish chunks
    ("cómo hago para que el usuario siga conectado entre peticiones", 12),
    ("subir mi código serverless a producción", 13),
    ("qué reglas evitan que borre todo por accidente", 14),
    ("dónde se guarda el historial de decisiones del proyecto", 15),
]


def embed(model: str, text: str) -> list[float]:
    body = json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embeddings", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    return d.get("embedding") or d.get("embeddings", [[]])[0]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def eval_model(model: str):
    t0 = time.time()
    try:
        doc_vecs = [embed(model, d) for d in CORPUS]
    except Exception as e:
        return {"model": model, "error": f"{type(e).__name__}: {e}"}
    q_vecs = [embed(model, q) for q, _ in QUERIES]
    total_t = time.time() - t0
    dim = len(doc_vecs[0]) if doc_vecs else 0
    r1 = r3 = mrr = 0
    per = []
    for (q, target), qv in zip(QUERIES, q_vecs):
        ranked = sorted(range(len(CORPUS)), key=lambda i: cosine(qv, doc_vecs[i]), reverse=True)
        rank = ranked.index(target) + 1
        r1 += rank == 1
        r3 += rank <= 3
        mrr += 1.0 / rank
        per.append(rank)
    n = len(QUERIES)
    return {"model": model, "dim": dim, "recall@1": r1 / n, "recall@3": r3 / n,
            "MRR": mrr / n, "ranks": per, "total_s": round(total_t, 2),
            "per_embed_ms": round(total_t / (len(CORPUS) + len(QUERIES)) * 1000, 1)}


def main():
    models = ["qwen3-embedding:4b",   # current
              "qwen3-embedding:8b", "bge-m3", "mxbai-embed-large", "nomic-embed-text"]
    print(f"{'model':<22}{'dim':>6}{'R@1':>7}{'R@3':>7}{'MRR':>7}{'total_s':>9}{'ms/embed':>10}  ranks")
    rows = []
    for m in models:
        r = eval_model(m)
        if "error" in r:
            print(f"{m:<22}  ERR {r['error'][:50]}")
            continue
        rows.append(r)
        print(f"{m:<22}{r['dim']:>6}{r['recall@1']:>7.2f}{r['recall@3']:>7.2f}{r['MRR']:>7.2f}"
              f"{r['total_s']:>9}{r['per_embed_ms']:>10}  {r['ranks']}")
    # unload all
    for m in models:
        try:
            urllib.request.urlopen(urllib.request.Request(f"{OLLAMA}/api/generate",
                data=json.dumps({"model": m, "keep_alive": 0}).encode(),
                headers={"Content-Type": "application/json"}), timeout=10)
        except Exception:
            pass
    best = max(rows, key=lambda r: (r["MRR"], r["recall@1"])) if rows else None
    if best:
        print(f"\nBest retrieval: {best['model']} (MRR={best['MRR']:.2f}, R@1={best['recall@1']:.2f}, "
              f"dim={best['dim']}, {best['per_embed_ms']}ms/embed)")
    json.dump(rows, open("/home/eldi/bench/ollama/results_embed.json", "w"), indent=2)
    print("Saved: /home/eldi/bench/ollama/results_embed.json")
    print("EMBED_EVAL_DONE")


if __name__ == "__main__":
    main()
