"""File system discovery for Python packages and modules."""

from pathlib import Path


def find_package_roots(base: Path) -> list[Path]:
    """Discover top-level Python package roots under a directory.

    A package root is the parent directory of a package that has
    ``__init__.py`` but whose own parent does not.

    Parameters
    ----------
    base : Path
        Root directory to recursively search.

    Returns
    -------
    list[Path]
        Sorted list of directories that act as package roots.

    Examples
    --------
    Directory structure::

        project/
            auth/
                __init__.py
                models.py
            utils/
                __init__.py

    >>> find_package_roots(Path("project"))
    [Path("project")]
    """
    roots: set[Path] = set()
    for dir_path in base.rglob("*"):
        if not dir_path.is_dir():
            continue

        if not (dir_path / "__init__.py").is_file():
            continue

        parent = dir_path.parent
        if not (parent / "__init__.py").is_file():
            roots.add(parent)

    return sorted(roots, key=lambda p: p.as_posix())


def path_to_module(path: Path, root: Path) -> str:
    """Convert a Python file path to its dotted module name.

    Parameters
    ----------
    path : Path
        Absolute path to a Python file belonging to a package.
    root : Path
        Package root (parent directory of the top-level package).

    Returns
    -------
    str
        Fully-qualified module name.

    Notes
    -----
    ``__init__.py`` files map to the package itself.

    Examples
    --------
    >>> path_to_module(Path("project/auth/models.py"), Path("project"))
    'auth.models'

    >>> path_to_module(Path("project/auth/__init__.py"), Path("project"))
    'auth'
    """
    relative = path.relative_to(root)
    if relative.name == "__init__.py":
        relative = relative.parent
    else:
        relative = relative.with_suffix("")

    return ".".join(relative.parts)


def discover_modules(base: Path) -> list[tuple[Path, str]]:
    """Discover all importable modules under a directory.

    Standalone ``.py`` files outside a package hierarchy are ignored.

    Parameters
    ----------
    base : Path
        Root directory to search.

    Returns
    -------
    list[tuple[Path, str]]
        List of ``(path, module_name)`` pairs.

    Examples
    --------
    >>> discover_modules(Path("project"))
    [
        (Path("project/auth/__init__.py"), "auth"),
        (Path("project/auth/models.py"), "auth.models"),
    ]
    """
    modules: list[tuple[Path, str]] = []
    for root in find_package_roots(base):
        for pyfile in sorted(root.rglob("*.py")):
            modules.extend([(pyfile, path_to_module(pyfile, root))])
    return modules


def module_to_path(module_name: str, root: Path) -> Path | None:
    """Resolve a dotted module name to its source file path.

    Parameters
    ----------
    module_name : str
        Dotted module name (e.g. ``"auth.models"``).
    root : Path
        Package root directory to search under.

    Returns
    -------
    Path | None
        Absolute path to the module file if found, otherwise ``None``.

    Notes
    -----
    Resolution order:

    1. ``module.py``
    2. ``module/__init__.py``

    Examples
    --------
    >>> module_to_path("auth.models", Path("project"))
    Path("project/auth/models.py")

    >>> module_to_path("auth", Path("project"))
    Path("project/auth/__init__.py")
    """
    parts = module_name.split(".")
    as_file = root.joinpath(*parts).with_suffix(".py")
    as_pkg = root.joinpath(*parts) / "__init__.py"

    if as_file.is_file():
        return as_file
    if as_pkg.is_file():
        return as_pkg
    return None
