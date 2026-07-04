"""Quality evaluation - load individual files and judge."""
import json
from pathlib import Path

OUTPUT_DIR = Path("/home/eldi/bench/ollama/quality_test")

# Load all model results
all_results = []
for f in sorted(OUTPUT_DIR.glob("*.json")):
    if f.name == "all.json":
        continue
    data = json.load(open(f))
    all_results.extend(data)

# Group by prompt
by_prompt = {}
for r in all_results:
    by_prompt.setdefault(r["label"], []).append(r)

# Display
print("="*100)
print(f"QUALITY EVALUATION - {len(all_results)} outputs from {len({r['model'] for r in all_results})} models")
print("="*100)

# Show IMPROVE - most critical for user
print("\n" + "="*100)
print("TASK: IMPROVE (vague → structured spec)")
print("="*100)
print("PROMPT: 'I have this bug where the auth middleware crashes randomly. Stack trace points to jwt.js line 47 sometimes. Need to fix it. Tests pass locally but fail in CI 1/5 times.'")
print("-"*100)

for r in by_prompt.get("IMPROVE", []):
    print(f"\n### {r['model']} ({r['tok_s']} tok/s, {r['total_s']}s)")
    out = r['output']
    print(out[:1200] + ("\n[...truncated...]" if len(out) > 1200 else ""))