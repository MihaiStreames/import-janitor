from __future__ import annotations

from functools import cache
from pathlib import Path
import sys


@cache
def _stdlib_modules() -> frozenset[str]:
    # 3.10+ only, but we only support 3.11+ anyway
    return frozenset(sys.stdlib_module_names)


def is_stdlib(module: str) -> bool:
    top = module.split(".", maxsplit=1)[0]
    return top in _stdlib_modules()


def is_third_party(module: str, project_root: Path) -> bool:
    """Anything not stdlib and not findable under project_root"""
    if is_stdlib(module):
        return False

    top = module.split(".", maxsplit=1)[0]
    return not (project_root / top).exists() and not (project_root / f"{top}.py").exists()


def resolve_relative(
    module: str,
    level: int,  # node.level from ast.ImportFrom
    current_module: str,  # dotted module name of the file doing the import
) -> str:
    """Convert relative import to absolute dotted name"""
    if level == 0:
        return module

    parts = current_module.split(".")
    # level=1 means current package, level=2 means parent, etc.
    base = parts[:-(level)]
    return ".".join(base + ([module] if module else []))
