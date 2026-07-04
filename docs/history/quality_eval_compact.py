"""Show COMPACT and LONGCTX outputs."""
import json
from pathlib import Path

OUTPUT_DIR = Path("/home/eldi/bench/ollama/quality_test")
all_results = []
for f in sorted(OUTPUT_DIR.glob("*.json")):
    if f.name == "all.json":
        continue
    data = json.load(open(f))
    all_results.extend(data)

by_prompt = {}
for r in all_results:
    by_prompt.setdefault(r["label"], []).append(r)

print("="*100)
print("TASK: COMPACT (session → 5-bullet handoff)")
print("="*100)
print("PROMPT: Session about pytest ModuleNotFoundError + pythonpath fix + payment test deferred.")
print("-"*100)

for r in by_prompt.get("COMPACT", []):
    print(f"\n### {r['model']} ({r['tok_s']} tok/s, {r['total_s']}s)")
    print(r['output'][:1000])

print("\n\n" + "="*100)
print("TASK: LONGCTX (~2K token session → structured handoff)")
print("="*100)
print("PROMPT: 500-error debugging session, connection pool fix, deploy plan.")
print("-"*100)

for r in by_prompt.get("LONGCTX", []):
    print(f"\n### {r['model']} ({r['tok_s']} tok/s, {r['total_s']}s)")
    print(r['output'][:1000])