from pathlib import Path
import tempfile
import textwrap

from janitor.graph import extract_imports
from janitor.models import ImportKind


def make_file(source: str) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w")
    f.write(textwrap.dedent(source))
    f.flush()
    return Path(f.name)


def test_regular_import():
    p = make_file("import os")
    result = extract_imports(p, "mymod")
    assert result.imports[0].module == "os"
    assert result.imports[0].kind == ImportKind.REGULAR


def test_type_checking_guard():
    p = make_file("""
        from __future__ import annotations
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            import heavy_thing
    """)
    result = extract_imports(p, "mymod")
    tc = [i for i in result.imports if i.is_type_checking]
    assert any(i.module == "heavy_thing" for i in tc)


def test_star_import():
    p = make_file("from os.path import *")
    result = extract_imports(p, "mymod")
    assert result.imports[0].kind == ImportKind.STAR
