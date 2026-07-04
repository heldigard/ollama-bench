"""Vertical-slice integrity gate.

Enforces the structural rules from CLAUDE.md:
  - Each features/<slice>/ has exactly one cmd_<slice> in command.py
  - shared/ never imports from features/
  - No cross-feature imports (except via shared)
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "src" / "ollama_bench"


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text())
    except SyntaxError:
        return None


def _imports_from(path: Path) -> set[str]:
    """Return set of module paths imported by `path`."""
    tree = _parse(path)
    if tree is None:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                found.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                found.add(node.module)
    return found


def _cmd_functions_in_command(slice_dir: Path) -> list[str]:
    """Find cmd_* functions defined in command.py of slice."""
    cmd = slice_dir / "command.py"
    if not cmd.exists():
        return []
    tree = _parse(cmd)
    if tree is None:
        return []
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("cmd_")
    ]


def test_every_feature_has_command_py():
    """Every features/<slice>/ must have a command.py."""
    features = ROOT / "features"
    if not features.exists():
        pytest.fail("no features/ directory")
    for slice_dir in sorted(features.iterdir()):
        if not slice_dir.is_dir() or slice_dir.name.startswith("_"):
            continue
        cmd = slice_dir / "command.py"
        assert cmd.exists(), f"{slice_dir.name}/command.py missing"


def test_every_feature_has_cmd_function():
    """Each command.py should define at least one cmd_* function."""
    for slice_dir in sorted((ROOT / "features").iterdir()):
        if not slice_dir.is_dir() or slice_dir.name.startswith("_"):
            continue
        cmds = _cmd_functions_in_command(slice_dir)
        assert len(cmds) >= 1, f"{slice_dir.name}/command.py has no cmd_* function"


def test_shared_never_imports_features():
    """shared/ must not import from features/ (one direction only)."""
    shared = ROOT / "shared"
    for f in shared.rglob("*.py"):
        imps = _imports_from(f)
        assert not any("ollama_bench.features" in i for i in imps), (
            f"{f} imports from features (forbidden direction)"
        )


def test_no_cross_feature_imports():
    """Features must not import other features (use shared/ instead)."""
    features = ROOT / "features"
    slice_names = {d.name for d in features.iterdir() if d.is_dir()}
    for slice_dir in sorted(features.iterdir()):
        if not slice_dir.is_dir() or slice_dir.name.startswith("_"):
            continue
        for f in slice_dir.rglob("*.py"):
            imps = _imports_from(f)
            for imp in imps:
                # Look for sibling-feature imports
                for other in slice_names:
                    if other != slice_dir.name:
                        if f"ollama_bench.features.{other}" in imp:
                            pytest.fail(
                                f"{f} imports from features.{other} "
                                f"(cross-feature, use shared/ instead)"
                            )


def test_cli_lists_all_slices():
    """cli.py must import add_parser from every feature."""
    cli = (ROOT / "cli.py").read_text()
    features_dir = ROOT / "features"
    for slice_dir in features_dir.iterdir():
        if not slice_dir.is_dir() or slice_dir.name.startswith("_"):
            continue
        assert f"features.{slice_dir.name}" in cli, (
            f"cli.py missing import for {slice_dir.name}"
        )
