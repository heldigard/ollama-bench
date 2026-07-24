"""embedding - embedding model evaluation."""

from __future__ import annotations

import json
import sys
import time
import urllib.request

from ollama_bench.shared.config import OLLAMA_URL


def get_embedding(model: str, prompt: str) -> dict:
    """Single Ollama /api/embed call. Returns {embedding, dt}."""
    body = json.dumps({"model": model, "prompt": prompt}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except Exception as e:
        return {"err": str(e)[:200]}
    return {
        "dt": round(time.perf_counter() - t0, 2),
        "embedding": data.get("embedding", []),
        "dim": len(data.get("embedding", [])),
    }


def cosine(a, b):
    """Cosine similarity of two equal-length vectors."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


TEST_PAIRS = (
    ("Python list vs tuple", "Difference between a Python list and a tuple"),
    ("hello world", "goodbye world"),
    ("cat sat on mat", "feline rested on rug"),
    ("machine learning", "deep learning"),
)


def cmd_embedding_eval(args):
    """Test embedding model: cosine similarity on TEST_PAIRS."""
    model = args.model
    print(f"# embedding eval: {model}", file=sys.stderr)
    for t1, t2 in TEST_PAIRS:
        e1 = get_embedding(model, t1)
        e2 = get_embedding(model, t2)
        if "err" in e1 or "err" in e2:
            print(f"  ERR: {e1.get('err', e2.get('err'))}", file=sys.stderr)
            return 1
        sim = cosine(e1["embedding"], e2["embedding"])
        print(f"  cos('{t1[:30]}' vs '{t2[:30]}') = {sim:.3f}", file=sys.stderr)
    return 0


def add_parser(sub, parent):
    p = sub.add_parser("embedding", parents=[parent], help="Embedding model evaluation.")
    sp = p.add_subparsers(dest="emb_cmd", required=True)
    ec = sp.add_parser("eval", parents=[parent], help="Run embedding model on TEST_PAIRS.")
    ec.add_argument("-m", "--model", required=True, help="Embedding model tag.")
    ec.set_defaults(cmd=cmd_embedding_eval)
