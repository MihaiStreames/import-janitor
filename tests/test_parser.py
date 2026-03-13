from pathlib import Path

from janitor.models import ImportKind
from janitor.parser import parse_imports
import pytest


DUMMY_PATH = Path("/path/to/module.py")


def test_regular_import():
    result = parse_imports("import os", DUMMY_PATH)
    assert len(result.imports) == 1
    imp = result.imports[0]
    assert imp.kind == ImportKind.REGULAR
    assert imp.module == "os"
    assert imp.alias is None


def test_aliased_import():
    result = parse_imports("import sys as system", DUMMY_PATH)
    imp = result.imports[0]
    assert imp.module == "sys"
    assert imp.alias == "system"


def test_from_import():
    result = parse_imports("from .baz import qux", DUMMY_PATH)
    imp = result.imports[0]
    assert imp.kind == ImportKind.FROM
    assert imp.module == "baz"
    assert imp.level == 1


def test_future_import():
    result = parse_imports("from __future__ import annotations", DUMMY_PATH)
    assert result.imports[0].kind == ImportKind.FUTURE


def test_star_import():
    result = parse_imports("from math import *", DUMMY_PATH)
    imp = result.imports[0]
    assert imp.kind == ImportKind.STAR
    assert imp.module == "math"


def test_type_checking_block():
    src = """
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import typing
"""
    result = parse_imports(src, DUMMY_PATH)
    tc_imports = [i for i in result.imports if i.is_type_checking]
    assert len(tc_imports) == 1
    assert tc_imports[0].module == "typing"


def test_nested_import():
    src = """
def func():
    import math
"""
    result = parse_imports(src, DUMMY_PATH)
    assert any(i.module == "math" for i in result.imports)


def test_syntax_error_raises():
    with pytest.raises(SyntaxError):
        parse_imports("def (", DUMMY_PATH)
