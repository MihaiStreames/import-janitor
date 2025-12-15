from collections.abc import Sequence
import libcst as cst
import libcst.metadata as metadata
import libcst.helpers as helpers
from pathlib import Path
from typing import List, Optional
import msgspec


class ImportInfo(msgspec.Struct):
    module: Optional[str]
    names: Sequence[Optional[str]]
    is_relative: bool
    lineno: int


class ImportCollector(cst.CSTVisitor):
    """Collects all imports from a module"""

    METADATA_DEPENDENCIES = (metadata.PositionProvider,)

    def __init__(self):
        self.imports: List[ImportInfo] = []

    def visit_Import(self, node: cst.Import) -> None:
        """Handle: import foo, bar"""
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                module = helpers.get_full_name_for_node(name.name)
                self.imports.append(
                    ImportInfo(
                        module=module,
                        names=[module.split(".")[-1]] if module else [],
                        is_relative=False,
                        lineno=self._get_lineno(node),
                    )
                )

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Handle: from foo import bar, baz"""
        if node.module is None:
            return

        module = helpers.get_full_name_for_node(node.module)
        is_relative = len(node.relative) > 0

        # Handle star imports
        if isinstance(node.names, cst.ImportStar):
            names = ["*"]
        else:
            names = [
                helpers.get_full_name_for_node(name.name)
                for name in node.names
                if isinstance(name, cst.ImportAlias)
            ]

        self.imports.append(
            ImportInfo(
                module=module,
                names=names if names else [],
                is_relative=is_relative,
                lineno=self._get_lineno(node),
            )
        )

    def _get_lineno(self, node) -> int:
        pos = self.get_metadata(metadata.PositionProvider, node)
        return pos.start.line if pos else -1


def analyze_file(filepath: Path) -> List[ImportInfo]:
    """Analyze a Python file and return all imports"""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    module = cst.parse_module(source)
    wrapper = cst.MetadataWrapper(module)
    collector = ImportCollector()

    wrapper.visit(collector)
    return collector.imports
