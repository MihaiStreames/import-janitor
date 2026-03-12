from ast import Attribute
from ast import If
from ast import Import as astImport
from ast import ImportFrom
from ast import Name
from ast import parse
from ast import stmt
from collections.abc import Iterator
from pathlib import Path

from .models import Import
from .models import ImportKind
from .models import ModuleImports


def _is_type_checking_block(node: If) -> bool:
    if isinstance(node.test, Name) and node.test.id == "TYPE_CHECKING":
        return True

    return bool(
        isinstance(node.test, Attribute)
        and node.test.attr == "TYPE_CHECKING"
        and isinstance(node.test.value, Name)
        and node.test.value.id == "typing"
    )


def _child_statement_lists(node: stmt) -> list[list[stmt]]:
    result = []

    for field in ("body", "orelse", "finalbody"):
        val = getattr(node, field, [])
        if val:
            result.append(val)

    # handlers: list[ExceptHandler], each has its own body
    result.extend(handler.body for handler in getattr(node, "handlers", []))

    # match/case: cases is list[match_case], each has body
    result.extend(case.body for case in getattr(node, "cases", []))

    return result


def _walk_stmts(
    stmts: list[stmt], *, in_type_checking: bool
) -> Iterator[tuple[astImport | ImportFrom, bool]]:
    for node in stmts:
        if isinstance(node, (astImport, ImportFrom)):
            yield node, in_type_checking
        elif isinstance(node, If) and _is_type_checking_block(node):
            # recurse into body with flag flipped ON, never recurse into orelse
            yield from _walk_stmts(node.body, in_type_checking=True)
        else:
            # recurse into any other statement containers
            for child_stmts in _child_statement_lists(node):
                yield from _walk_stmts(child_stmts, in_type_checking=in_type_checking)


def parse_imports(source: str, path: Path) -> ModuleImports:
    """Parse Python source code to extract import statements.

    Parameters
    ----------
    source : str
        The Python source code to parse.
    path : Path
        The file path of the source code, used for error reporting.

    Returns
    -------
    ModuleImports
        A collection of all import statements found in the source code.
    """
    tree = parse(source, filename=str(path))
    imports = []

    for node, in_type_checking in _walk_stmts(tree.body, in_type_checking=False):
        if isinstance(node, astImport):
            imports.extend(
                [
                    Import(
                        kind=ImportKind.REGULAR,
                        module=alias.name,
                        alias=alias.asname,
                        is_type_checking=in_type_checking,
                        lineno=node.lineno,
                    )
                    for alias in node.names
                ]
            )
        else:  # ast.ImportFrom
            if node.module == "__future__":
                kind = ImportKind.FUTURE
            elif node.names[0].name == "*":
                kind = ImportKind.STAR
            else:
                kind = ImportKind.FROM

            imports.append(
                Import(
                    kind=kind,
                    module=node.module or "",
                    names=tuple(alias.name for alias in node.names),
                    alias=None,  # `from ... import ...` doesn't support aliasing the module itself
                    is_type_checking=in_type_checking,
                    lineno=node.lineno,
                    level=node.level,
                )
            )

    return ModuleImports(path=path, imports=imports)


# TODO: remove this once we have tests
if __name__ == "__main__":
    source = """
import os
import sys as system
from . import foo
from .. import bar
from .baz import qux
from __future__ import annotations

def func():
    import math
    if True:
        import datetime
    if False:
        from typing import TYPE_CHECKING

    a = 1
    if TYPE_CHECKING:
        import typing

    b = 2
    return a + b
"""
    from time import perf_counter

    time = None
    start = perf_counter()

    result = parse_imports(source, Path("/path/to/module.py"))

    end = perf_counter()
    time = end - start

    print(f"Parsing took {time:.4f} seconds")
    print(result)
