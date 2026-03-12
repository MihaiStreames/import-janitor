from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from pathlib import Path

import msgspec


class ImportKind(Enum):
    REGULAR = 1
    FROM = 2
    STAR = 3
    FUTURE = 4


@dataclass(frozen=True, slots=True)
class Import:
    kind: ImportKind
    module: str  # always absolute after resolution
    names: tuple[str, ...] = ()  # empty for REGULAR/STAR
    alias: str | None = None  # import foo as f
    is_type_checking: bool = False  # inside TYPE_CHECKING block
    lineno: int = 0
    level: int = 0  # 0 = absolute, 1 = current package, etc. (for ImportFrom only)


@dataclass(slots=True)
class ModuleImports:
    path: Path
    module_name: str  # dotted, e.g. "janitor.graph"
    imports: list[Import] = field(default_factory=list)


@dataclass(slots=True)
class Cycle:
    modules: list[str]  # ordered cycle path

    def __str__(self) -> str:
        chain = " → ".join(self.modules)
        return f"{chain} → {self.modules[0]}"  # show it loops back


# msgspec for any JSON output (--format json flag later)
class CycleReport(msgspec.Struct):
    cycles: list[list[str]]
    file_count: int
    error_count: int
