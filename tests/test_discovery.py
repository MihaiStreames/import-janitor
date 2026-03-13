from janitor.discovery import discover_modules
from janitor.discovery import find_package_roots
from janitor.discovery import module_to_path
from janitor.discovery import path_to_module
import pytest


@pytest.fixture
def pkg_tree(tmp_path):
    files = [
        "packages/auth/__init__.py",
        "packages/auth/models.py",
        "packages/auth/utils/__init__.py",
        "packages/auth/utils/helpers.py",
        "packages/api/__init__.py",
        "src/shared/__init__.py",
        "scripts/migrate.py",  # not in a package
    ]
    for f in files:
        p = tmp_path / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("")
    return tmp_path


def test_find_package_roots(pkg_tree):
    roots = find_package_roots(pkg_tree)
    rel = {r.relative_to(pkg_tree).as_posix() for r in roots}
    assert rel == {"packages", "src"}


def test_path_to_module_init(pkg_tree):
    root = pkg_tree / "packages"
    assert path_to_module(root / "auth/__init__.py", root) == "auth"


def test_path_to_module_nested(pkg_tree):
    root = pkg_tree / "packages"
    assert path_to_module(root / "auth/utils/helpers.py", root) == "auth.utils.helpers"


def test_discover_modules_skips_scripts(pkg_tree):
    modules = discover_modules(pkg_tree)
    names = {name for _, name in modules}
    assert "migrate" not in names  # scripts/migrate.py has no __init__.py parent


def test_module_to_path_file(pkg_tree):
    root = pkg_tree / "packages"
    assert module_to_path("auth.models", root) == root / "auth/models.py"


def test_module_to_path_package(pkg_tree):
    root = pkg_tree / "packages"
    assert module_to_path("auth", root) == root / "auth/__init__.py"


def test_module_to_path_missing(pkg_tree):
    root = pkg_tree / "packages"
    assert module_to_path("auth.nonexistent", root) is None
