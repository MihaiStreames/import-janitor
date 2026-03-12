from __future__ import annotations

import ast
from pathlib import Path

import networkx as nx

from .models import Cycle
from .models import ImportKind
from .models import Import
from .models import ModuleImports
from .resolver import is_stdlib
from .resolver import is_third_party


def _is_type_checking_block(node: ast.If) -> bool:
    """Detect `if TYPE_CHECKING:` blocks"""
    match node.test:
        case ast.Name(id="TYPE_CHECKING"):
            return True
        case ast.Attribute(attr="TYPE_CHECKING"):
            return True
    return False


def _extract_from_node(
    node: ast.Import | ast.ImportFrom,
    is_type_checking: bool,
) -> list[Import]:
    imports = []

    if isinstance(node, ast.Import):
        for alias in node.names:
            imports.append(
                Import(
                    kind=ImportKind.REGULAR,
                    module=alias.name,
                    alias=alias.asname,
                    is_type_checking=is_type_checking,
                    lineno=node.lineno,
                )
            )

    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        names = tuple(a.name for a in node.names)

        if names == ("*",):
            kind = ImportKind.STAR
        elif module == "__future__":
            kind = ImportKind.FUTURE
        else:
            kind = ImportKind.FROM

        imports.append(
            Import(
                kind=kind,
                module=module,
                names=names,
                is_type_checking=is_type_checking,
                lineno=node.lineno,
            )
        )

    return imports


def extract_imports(path: Path, module_name: str) -> ModuleImports:
    source = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source, filename=str(path))

    except SyntaxError as e:
        # don't crash on unparseable files, caller decides what to do
        raise ValueError(f"Could not parse {path}: {e}") from e

    result = ModuleImports(path=path, module_name=module_name)

    for node in ast.walk(tree):
        # detect TYPE_CHECKING blocks
        if isinstance(node, ast.If) and _is_type_checking_block(node):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    result.imports.extend(_extract_from_node(child, is_type_checking=True))
            continue  # already handled children

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            result.imports.extend(_extract_from_node(node, is_type_checking=False))

    return result


def path_to_module(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def build_graph(root: Path) -> tuple[nx.DiGraph, list[ValueError]]:
    """Returns the import graph and any parse errors encountered"""
    g = nx.DiGraph()
    errors: list[ValueError] = []

    py_files = list(root.rglob("*.py"))

    for path in py_files:
        module_name = path_to_module(path, root)
        g.add_node(module_name)

        try:
            mod_imports = extract_imports(path, module_name)

        except ValueError as e:
            errors.append(e)
            continue

        for imp in mod_imports.imports:
            if imp.is_type_checking:
                continue  # TYPE_CHECKING imports don't cause runtime cycles

            module = imp.module
            # resolve relative
            # TODO: need level from ast node (we'll add that to Import model)
            if is_stdlib(module) or is_third_party(module, root):
                continue

            g.add_edge(module_name, module)

    return g, errors


def find_cycles(g: nx.DiGraph) -> list[Cycle]:
    return [Cycle(modules=list(cycle)) for cycle in nx.simple_cycles(g)]
