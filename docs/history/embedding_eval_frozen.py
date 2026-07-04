import importlib.util, math, sys, json
from pathlib import Path
SCRIPTS = "/home/eldi/.claude/scripts"
sys.path.insert(0, SCRIPTS)
spec = importlib.util.spec_from_file_location("ms", f"{SCRIPTS}/memory-semantic.py")
ms = importlib.util.module_from_spec(spec); spec.loader.exec_module(ms)
import ollama_client as oc

FROZEN = Path("/tmp/frozen_corpus.json")
if not FROZEN.exists():
    root = Path("/home/eldi/.memory-bank")
    chunks = []
    for p in sorted(root.rglob("*.md")):
        for ch in ms.chunk_file(p):
            if ch["text"].strip():
                chunks.append((p.relative_to(root).as_posix(), ch["text"]))
    FROZEN.write_text(json.dumps(chunks)); print(f"frozen {len(chunks)} chunks", flush=True)
else:
    chunks = json.loads(FROZEN.read_text()); print(f"loaded frozen {len(chunks)} chunks", flush=True)

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
def norm(v):
    n = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]
MODELS = ["nomic-embed-text","embeddinggemma","nomic-embed-text-v2-moe"]
print(f"{'MODEL':26} {'MRR':>6} {'dim':>5} {'ranks'}")
for model in MODELS:
    cvecs = [(norm(v) if (v:=oc.embed(t, model=model)) else None) for _,t in chunks]
    rr = []
    for q, expected in QUERIES:
        qv = oc.embed(q, model=model)
        if not qv: rr.append(99); continue
        qv = norm(qv)
        ranked = sorted(((sum(a*b for a,b in zip(qv,cv)), h) for cv,(h,_) in zip(cvecs,chunks) if cv), reverse=True)
        rr.append(next((i+1 for i,(_,h) in enumerate(ranked) if expected in h), 99))
    mrr = sum(1.0/r for r in rr)/len(rr)
    dim = len(next(v for v in cvecs if v))
    print(f"{model:26} {mrr:>6.3f} {dim:>5} {' '.join(f'{r:>3}' for r in rr)}", flush=True)
