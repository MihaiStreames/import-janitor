"""AST-based import statement parser."""

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
        File path of the source, used in error messages.

    Returns
    -------
    ModuleImports
        All import statements found in the source.

    Raises
    ------
    SyntaxError
        If *source* contains invalid Python syntax.
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

            imports.extend(
                [
                    Import(
                        kind=kind,
                        module=node.module or "",
                        names=(alias.name,),  # instead of alias=None, we can use per-name aliases
                        # which means ImportFrom with multiple names needs multiple Import objects
                        alias=alias.asname,
                        is_type_checking=in_type_checking,
                        lineno=node.lineno,
                        level=node.level,
                    )
                    for alias in node.names
                ]
            )

    return ModuleImports(path=path, imports=imports)
