"""Data models for import representation."""

from enum import Enum
from pathlib import Path

from msgspec import Struct


class ImportKind(Enum):
    """Enumeration of Python import statement types.

    Attributes
    ----------
    REGULAR : int
        ``import foo`` or ``import foo as bar``.
    FROM : int
        ``from foo import bar`` or ``from foo import bar as baz``.
    STAR : int
        ``from foo import *``.
    FUTURE : int
        ``from __future__ import ...``.

    Examples
    --------
    >>> ImportKind.REGULAR
    <ImportKind.REGULAR: 1>
    """

    REGULAR = 1
    FROM = 2
    STAR = 3
    FUTURE = 4


class Import(Struct, frozen=True):
    """Representation of a single import statement.

    Attributes
    ----------
    kind : ImportKind
        Type of import statement.
    module : str
        Absolute module path after resolution.
    names : tuple[str, ...]
        Imported names. Empty for ``REGULAR`` imports.
    alias : str | None
        Optional alias (e.g. ``import foo as f``).
    is_type_checking : bool
        ``True`` if the import occurs inside ``if TYPE_CHECKING:``.
    lineno : int
        Line number of the import statement (1-based).
    level : int
        Relative import level (0 = absolute, 1 = ``.``, 2 = ``..``).

    Notes
    -----
    ``module`` is normalized to an absolute module path during import resolution.
    """

    kind: ImportKind = ImportKind.REGULAR
    module: str = ""
    names: tuple[str, ...] = ()
    alias: str | None = None
    is_type_checking: bool = False
    lineno: int = 0
    level: int = 0


class ModuleImports(Struct):
    """Collection of import statements discovered in a module.

    Attributes
    ----------
    path : Path
        Absolute path to the module file.
    module_name : str
        Fully-qualified dotted module name.
    imports : list[Import]
        Import statements found in the module.
    """

    path: Path = Path()
    module_name: str = ""
    imports: list[Import] = []
