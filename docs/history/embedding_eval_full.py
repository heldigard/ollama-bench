#!/usr/bin/env python3
"""Comprehensive embedding-model eval for the home memory bank.
Criteria (user): quality (MRR) > context > speed. 12 in-corpus semantic bilingual
queries against the full home .memory-bank. Per-model corpus caching for fast reruns.
"""
import importlib.util, math, sys, json, hashlib, subprocess
from pathlib import Path
SCRIPTS = "/home/eldi/.claude/scripts"
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location("ms", f"{SCRIPTS}/memory-semantic.py")
ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
import ollama_client as oc

CORPUS_ROOT = Path("/home/eldi/.memory-bank")
CACHE = Path("/tmp/eval_cache"); CACHE.mkdir(exist_ok=True)

# 12 queries -> expected topic file (all confirmed in home bank). Semantic, bilingual.
QUERIES = [
    ("RTK output compression hook security shell injection bypass", "rtk-token-optimization"),
    ("Codex Gemini Kimi Qwen skill sync symlink cron periodic", "cli-changelog-watch"),
    ("MCP servers removed dropped replaced by skills SearXNG firecrawl", "mcp-setup"),
    ("context graph two-hop join traversal supersede aliases jsonl triples", "memory-bank-design"),
    ("cross-CLI agent coordination registry heartbeat stale cooldown lease", "agent-sessions"),
    ("swarm coding workhorse pool controller spec parallel kimi qwen", "swarm-coding-pool"),
    ("cheap local LLM cascade benchmark models tested pruned ollama", "tested-models"),
    ("caveman token compression prose cross-CLI shared state lite full ultra", "caveman-cross-cli"),
    ("git CRLF LF line ending pre-commit hook unix2dos Edit tool java", "git-eol-guard"),
    ("Azure Functions Python programming model v2 decorator trigger", "azure-functions-python-version"),
    ("vertical slice guard PostToolUse hook budget LOC cohesion split", "cli-config-audit"),
    ("decisiones patrones sistema 2026 memoria auto-maintain refresco", "system-patterns-detail"),
]

# stable corpus
chunks = []
for p in sorted(CORPUS_ROOT.rglob("*.md")):
    for ch in ms.chunk_file(p):
        if ch["text"].strip():
            chunks.append((p.relative_to(CORPUS_ROOT).as_posix(), ch["text"]))
corpus_hash = hashlib.sha256("|".join(t for _, t in chunks).encode()).hexdigest()[:12]
print(f"corpus: {len(chunks)} chunks (hash {corpus_hash})\n", flush=True)

def norm(v):
    n = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]

def model_ctx_dim_size(model):
    try:
        out = subprocess.run(["ollama","show",model], capture_output=True, text=True, timeout=15).stdout
    except Exception:
        return "?","?","?"
    ctx = dim = size = "?"
    for line in out.splitlines():
        if "num_ctx" in line or "context length" in line.lower(): ctx = line.split()[-1]
        if "embedding length" in line.lower(): dim = line.split()[-1]
        if line.strip().endswith("GB") or line.strip().endswith("MB"):
            if "size" in line.lower() or ":" in line: size = line.split()[-1]
    return ctx, dim, size

def cached_corpus_vecs(model):
    cf = CACHE / f"{model.replace(':','_')}_{corpus_hash}.json"
    if cf.exists():
        try:
            data = json.loads(cf.read_text())
            if len(data) == len(chunks): return data
        except Exception: pass
    vecs = []
    for i, (_, txt) in enumerate(chunks):
        v = oc.embed(txt, model=model)
        vecs.append(norm(v) if v else None)
        if i % 100 == 0: print(f"  {model}: {i}/{len(chunks)}", flush=True)
    try: cf.write_text(json.dumps(vecs))
    except Exception: pass
    return vecs

MODELS = ["mxbai-embed-large","nomic-embed-text","qwen3-embedding:4b",
          "qwen3-embedding:8b","embeddinggemma","nomic-embed-text-v2-moe"]

print(f"{'MODEL':26} {'MRR':>6} {'dim':>5} {'ctx':>8} {'ranks':<28}")
print("-"*80)
for model in MODELS:
    # skip if not pulled
    try:
        alive = subprocess.run(["ollama","show",model], capture_output=True, timeout=15)
        if alive.returncode != 0:
            print(f"{model:26}   (not installed, skip)"); continue
    except Exception:
        print(f"{model:26}   (show failed, skip)"); continue
    cvecs = cached_corpus_vecs(model)
    rr = []
    for q, expected in QUERIES:
        qv = oc.embed(q, model=model)
        if not qv: rr.append(0.0); continue
        qv = norm(qv)
        ranked = sorted(((sum(a*b for a,b in zip(qv,cv)), h) for cv,(h,_) in zip(cvecs,chunks) if cv), reverse=True)
        rank = next((i+1 for i,(_,h) in enumerate(ranked) if expected in h), 99)
        rr.append(rank)
    mrr = sum(1.0/r for r in rr)/len(rr)
    _, dim, _ = model_ctx_dim_size(model)
    ctx, _, size = model_ctx_dim_size(model)
    dim_actual = len(next(v for v in cvecs if v))
    ranks_str = " ".join(f"{r:>2}" for r in rr)
    print(f"{model:26} {mrr:>6.3f} {dim_actual:>5} {str(ctx)[:8]:>8} {ranks_str}")
