from pathlib import Path
from import_janitor.analyzer import analyze_file
import tempfile


def test_simple_import():
    code = """
import os
import sys
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        imports = analyze_file(Path(f.name))
        assert len(imports) == 2
        assert imports[0].module == "os"
        assert imports[1].module == "sys"


def test_from_import():
    code = """
from typing import List, Dict
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        imports = analyze_file(Path(f.name))
        assert len(imports) == 1
        assert imports[0].module == "typing"
        assert set(imports[0].names) == {"List", "Dict"}
