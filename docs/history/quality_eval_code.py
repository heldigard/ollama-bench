"""Show CODE and REASON outputs for evaluation."""
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
print("TASK: CODE - Python async retry_with_backoff with type hints + backoff + jitter")
print("="*100)
print("Prompt: Write async function retry_with_backoff(fn, max_attempts=3, base_delay=0.5)")
print("       Retries fn on ConnectionError, TimeoutError. Exponential backoff with jitter.")
print("       Return result on success, raise last exception. Include type hints + docstring.")
print("-"*100)

for r in by_prompt.get("CODE", []):
    print(f"\n### {r['model']} ({r['tok_s']} tok/s, {r['total_s']}s)")
    out = r['output']
    # Show full code
    print(out[:1500] + ("\n[...truncated...]" if len(out) > 1500 else ""))

print("\n\n" + "="*100)
print("TASK: REASON - Sprint capacity problem")
print("="*100)
print("Sprint capacity 40/sp. 200pt backlog. 3 sprints left. Velocity 35,42,38 (avg 38.3).")
print("Can they finish? Min additional velocity? Show work.")
print("-"*100)

for r in by_prompt.get("REASON", []):
    print(f"\n### {r['model']} ({r['tok_s']} tok/s, {r['total_s']}s)")
    out = r['output']
    print(out[:1000] + ("\n[...truncated...]" if len(out) > 1000 else ""))