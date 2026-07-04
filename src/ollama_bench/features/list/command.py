"""list - enumerate installed Ollama models + flag incompat / warnings."""
from __future__ import annotations

import sys
from pathlib import Path

from ollama_bench.shared.config import (
    LEAKY_THINK_MODELS_SUBSTR,
    OLLAMA_0_23_INCOMPAT_MODELS,
)
from ollama_bench.shared.ollama import get_models


def _warnings_for(name: str) -> list[str]:
    """Per-model warnings (Ollama version incompat, leaky family, etc.)."""
    warnings: list[str] = []
    if name in OLLAMA_0_23_INCOMPAT_MODELS:
        warnings.append("OLLAMA_0_23_INCOMPAT")
    if any(sub in name for sub in LEAKY_THINK_MODELS_SUBSTR):
        warnings.append("LEAKS_THINK")
    return warnings


def cmd_list(args) -> int:
    """`ollama-bench list` entry point."""
    out_path = Path(args.output) if args.output else None
    fh = out_path.open("w") if out_path else None
    sink = fh if fh else sys.stdout
    n_warn = 0
    try:
        print("# Installed Ollama models", file=sink)
        for m in get_models():
            name = m.get("name", "?")
            size_mb = round(m.get("size", 0) / (1024 ** 2))
            quant = m.get("details", {}).get("quantization_level", "?")
            warnings = _warnings_for(name)
            n_warn += len(warnings) > 0
            warn_s = f"  [WARN: {','.join(warnings)}]" if warnings else ""
            print(f"{name}\t{size_mb} MB\t{quant}{warn_s}", file=sink)
        print(f"\n# Total: {len(get_models())} models, {n_warn} flagged", file=sink)
    finally:
        if fh:
            fh.close()
            print(f"Wrote {out_path}", file=sys.stderr)
    return 0


def add_parser(sub, parent):
    p = sub.add_parser("list", parents=[parent], help="Enumerate installed models (TSV + warnings).")
    p.add_argument("-o", "--output", help="Output TSV path (default: stdout).")
    p.set_defaults(cmd=cmd_list)
