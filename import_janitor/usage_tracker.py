import libcst as cst
import libcst.metadata as metadata
from typing import Set, Dict
import msgspec


class Usage(msgspec.Struct):
    name: str
    in_type_annotation: bool
    lineno: int


class UsageTracker(cst.CSTVisitor):
    """Tracks where imported names are used"""

    METADATA_DEPENDENCIES = (metadata.PositionProvider,)

    def __init__(self, imported_names: Set[str]):
        self.imported_names = imported_names
        self.usages: Dict[str, list[Usage]] = {name: [] for name in imported_names}
        self._in_annotation = False

    def visit_Annotation(self, node: cst.Annotation) -> None:
        self._in_annotation = True

    def leave_Annotation(self, original_node: cst.Annotation) -> None:
        self._in_annotation = False

    def visit_Name(self, node: cst.Name) -> None:
        if node.value in self.imported_names:
            pos = self.get_metadata(metadata.PositionProvider, node)
            self.usages[node.value].append(
                Usage(
                    name=node.value,
                    in_type_annotation=self._in_annotation,
                    lineno=pos.start.line if pos else -1,
                )
            )


def is_type_only_import(filepath, import_name: str, imported_names: Set[str]) -> bool:
    """Check if an import is only used in type annotations"""
    with open(filepath, "r") as f:
        source = f.read()

    module = cst.parse_module(source)
    wrapper = cst.MetadataWrapper(module)
    tracker = UsageTracker(imported_names)
    wrapper.visit(tracker)

    # Check if all usages are in type annotations
    for name in imported_names:
        usages = tracker.usages.get(name, [])
        if not usages:
            continue  # Unused import
        if any(not u.in_type_annotation for u in usages):
            return False

    return True
