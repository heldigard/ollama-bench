"""cli.py - argparse multi-command root.

Sub-commands map to cmd_<sub> in features/<slice>/command.py.
Adding a slice = import its add_parser and append to _SLICES.
"""

from __future__ import annotations

import argparse

from ollama_bench import __version__
from ollama_bench.features.browser_tool.command import add_parser as add_browser_tool
from ollama_bench.features.bug_finding.command import add_parser as add_bug_finding
from ollama_bench.features.deep.command import add_parser as add_deep
from ollama_bench.features.embedding.command import add_parser as add_embedding
from ollama_bench.features.embedding_retrieval.command import add_parser as add_embedding_retrieval
from ollama_bench.features.judge.command import add_parser as add_judge
from ollama_bench.features.lfm_variant.command import add_parser as add_lfm
from ollama_bench.features.list.command import add_parser as add_list
from ollama_bench.features.multi_domain.command import add_parser as add_multi_domain
from ollama_bench.features.pdf_extract.command import add_parser as add_pdf_extract
from ollama_bench.features.report.command import add_parser as add_report
from ollama_bench.features.smoke.command import add_parser as add_smoke
from ollama_bench.features.tie_break.command import add_parser as add_tie_break
from ollama_bench.features.tool_call.command import add_parser as add_tool_call

# Each slice registers: (slug, add_parser_fn, brief_help).
# Order matters for --help output (alphabetical-ish but smoke first as default).
_SLICES = [
    ("smoke", add_smoke, "1-prompt leak gate per model (fast filter)"),
    ("deep", add_deep, "5-task x N model bench"),
    ("tie-break", add_tie_break, "Re-bench tied candidates with harder prompts"),
    ("bug-finding", add_bug_finding, "Diff-review bench (count bugs found)"),
    ("tool-call", add_tool_call, "Structured JSON tool-call bench (ground-truth)"),
    ("browser-tool", add_browser_tool, "Ref-grounded a11y action bench (snap+ref)"),
    ("pdf-extract", add_pdf_extract, "Schema field-extraction bench (abstention)"),
    ("lfm-variant", add_lfm, "codeq summary tie-break for LFM family"),
    ("multi-domain", add_multi_domain, "Legacy 4-domain bench"),
    ("judge", add_judge, "LLM-as-judge helpers"),
    ("embedding", add_embedding, "Embedding model evaluation"),
    ("embedding-retrieval", add_embedding_retrieval, "Embedding MRR + recall@5 (ground-truth)"),
    ("list", add_list, "Enumerate installed models + flag incompat"),
    ("report", add_report, "Generate markdown ranking from bench results"),
]


def _build_parent() -> argparse.ArgumentParser:
    """Common flags attached via parents=[]. Empty for now; reserved for future flags."""
    return argparse.ArgumentParser(add_help=False)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="ollama-bench",
        description="Local Ollama model evaluation suite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  ollama-bench list                                    # installed + warn flags
  ollama-bench smoke                                    # 1-prompt leak gate
  ollama-bench deep                                     # 5-task x N model bench
  ollama-bench tie-break -w 'qwen3.5:4b' 'Huihui gemma4-12B abliterated'
  ollama-bench lfm-variant                              # LFM family think-strip
  ollama-bench report build                             # render TSV -> MD ranking
""",
    )
    ap.add_argument("--version", action="version", version=f"ollama-bench {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    parent = _build_parent()
    for _slug, add_parser_fn, _brief in _SLICES:
        add_parser_fn(sub, parent)

    args = ap.parse_args()
    return args.cmd(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
