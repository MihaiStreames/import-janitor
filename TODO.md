# import-janitor TODO

## Project Goal

Build an opinionated tool that analyzes and optimizes Python imports following ruff/isort/black rules.

## Core Features

### 1. TYPE_CHECKING Import Migration ✅ (In Progress)

- [ ] Parse imports from files
- [ ] Track import metadata (module, names, line numbers)
- [ ] Complete usage tracker to find where imports are used
- [ ] Detect type-only usage contexts:
  - [ ] Function annotations (args, return types)
  - [ ] Variable type hints
  - [ ] Generic type arguments (`List[MyClass]`)
  - [ ] String annotations (forward references)
  - [ ] Handle `from __future__ import annotations`
- [ ] Identify runtime usage that prevents TYPE_CHECKING:
  - [ ] `isinstance()` / `issubclass()` checks
  - [ ] Actual code execution
  - [ ] Default argument values
- [ ] Transform imports to TYPE_CHECKING blocks:
  - [ ] Add `from typing import TYPE_CHECKING` if needed
  - [ ] Move type-only imports into `if TYPE_CHECKING:` block
  - [ ] Preserve import order and formatting
- [ ] Handle edge cases:
  - [ ] Multiple TYPE_CHECKING blocks
  - [ ] Mixed type/runtime imports from same module
  - [ ] Circular imports that can be fixed this way

### 2. Relative vs Absolute Import Normalization

- [ ] Build package structure analyzer:
  - [ ] Find all `__init__.py` files
  - [ ] Build package hierarchy tree
  - [ ] Determine package boundaries
- [ ] Classify each import:
  - [ ] Internal (within same package tree) → relative
  - [ ] External (third-party/stdlib) → absolute
- [ ] Implement transformations:
  - [ ] Convert internal imports to relative (`.module`, `..sibling`)
  - [ ] Keep external imports absolute
  - [ ] Handle top-level package imports (can't be more relative)
- [ ] Edge cases:
  - [ ] Namespace packages without `__init__.py`
  - [ ] Cross-package imports in monorepos
  - [ ] Distinguish stdlib vs third-party vs local

### 3. Circular Dependency Detection

**Status:** Not started

- [ ] Build module import graph:
  - [ ] Create directed graph of all imports
  - [ ] Track import relationships between files
- [ ] Implement cycle detection:
  - [ ] DFS-based cycle detection algorithm
  - [ ] Find all cycles in the graph
  - [ ] Report full cycle paths (A → B → C → A)
- [ ] Suggest fixes:
  - [ ] Identify type-only imports that can move to TYPE_CHECKING
  - [ ] Suggest lazy imports (import inside functions)
  - [ ] Flag architectural issues for manual review
- [ ] Integration:
  - [ ] Run before other transforms to avoid creating cycles
  - [ ] Exit with error if unfixable cycles exist
  - [ ] Option to continue with warnings

### 4. `__all__` Deduplication & Re-export Optimization

- [ ] Parse `__init__.py` files:
  - [ ] Extract `__all__` declarations
  - [ ] Parse all `from X import Y` statements
  - [ ] Track what each package exports
- [ ] Detect redundant re-exports:
  - [ ] Compare package's `__all__` with imported package's `__all__`
  - [ ] Identify complete pass-through (100% match)
  - [ ] Identify partial re-exports (subset)
- [ ] Optimize complete re-exports:
  - [ ] Replace individual imports with package import
  - [ ] Example: `from .subpkg import a, b, c` → `from . import subpkg`
  - [ ] Update `__all__` to export package instead
- [ ] Conservative mode:
  - [ ] Only optimize 100% matches by default
  - [ ] Flag for aggressive mode (optimize partials too)
- [ ] Verify correctness:
  - [ ] Ensure `package.subpkg.item` still works
  - [ ] Don't expose unintended items
- [ ] Handle transitive re-exports:
  - [ ] Detect chains (pkg3 → pkg2 → pkg1)
  - [ ] Suggest direct imports when appropriate

### 5. Config Integration (ruff/isort/black)

- [ ] Config file discovery:
  - [ ] Read `pyproject.toml` ([tool.ruff], [tool.isort], [tool.black])
  - [ ] Read `setup.cfg`
  - [ ] Read `.isort.cfg`, `ruff.toml`
  - [ ] Merge configs with priority
- [ ] Extract relevant settings:
  - [ ] Line length (for import splitting)
  - [ ] Known first-party packages (internal/external classification)
  - [ ] Force single line imports
  - [ ] Import sorting preferences
  - [ ] Excluded directories
- [ ] Apply settings:
  - [ ] Respect line length when rewriting
  - [ ] Use known-first-party for classification
  - [ ] Follow sorting rules
- [ ] Compatibility:
  - [ ] Don't conflict with existing formatters
  - [ ] Work alongside ruff/black/isort

## Edge Cases to Handle

### Import Edge Cases

- [ ] Star imports (`from x import *`)
- [ ] Dynamic imports (`__import__()`, `importlib`)
- [ ] Conditional imports (inside if/try blocks)
- [ ] `__init__.py` vs regular modules
- [ ] Relative imports at package boundaries
- [ ] Imports in type comments (Python 2 style)

### Type Checking Edge Cases

- [ ] Generic types with multiple type parameters
- [ ] Type variables and type aliases
- [ ] Protocol classes (runtime vs type-time)
- [ ] `typing.cast()` calls
- [ ] Type guards
- [ ] Overload decorators

### Package Structure Edge Cases

- [ ] Monorepos with multiple packages
- [ ] Namespace packages
- [ ] Editable installs with src layout
- [ ] Vendored dependencies
- [ ] Generated code (protobuf, etc.)
