# import-janitor TODO

## Project Goal

Build an opinionated tool that analyzes and optimizes Python imports following ruff/isort/black rules.

---

## Core Features

### 1. TYPE_CHECKING Import Migration ✅ (In Progress)

**Status:** Foundation laid with `analyzer.py`

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

---

### 2. Relative vs Absolute Import Normalization

**Status:** Not started

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

---

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

---

### 4. `__all__` Deduplication & Re-export Optimization

**Status:** Not started

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

---

### 5. Config Integration (ruff/isort/black)

**Status:** Not started

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

---

## Architecture & Infrastructure

### Code Organization

- [ ] `analyzer.py` - Import detection and parsing
- [ ] `usage_tracker.py` - Find where imports are used (partially done)
- [ ] `classifier.py` - Classify imports (type-only, internal/external)
- [ ] `graph.py` - Build and analyze import dependency graph
- [ ] `transformer.py` - Rewrite imports using libcst
- [ ] `config.py` - Parse and manage configuration
- [ ] `package_analyzer.py` - Analyze package structure and `__all__`
- [ ] `cli.py` - Command-line interface (basic version exists)
- [ ] `reporter.py` - Format and display results

### Testing

- [ ] Basic test structure
- [ ] Tests for import analysis
- [ ] Tests for usage tracking
- [ ] Tests for TYPE_CHECKING migration
- [ ] Tests for relative/absolute conversion
- [ ] Tests for circular dependency detection
- [ ] Tests for `__all__` optimization
- [ ] Integration tests on real projects
- [ ] Edge case tests

### CLI Features

- [ ] Basic commands:
  - [ ] `import-janitor check <path>` - Analyze and report issues
  - [ ] `import-janitor fix <path>` - Apply fixes automatically
  - [ ] `import-janitor graph <path>` - Visualize import graph
- [ ] Options:
  - [ ] `--dry-run` - Show what would change
  - [ ] `--diff` - Show git-style diffs
  - [ ] `--check-only` - Exit with error if issues found (for CI)
  - [ ] `--config <path>` - Custom config file
  - [ ] `--verbose` - Detailed output
  - [ ] `--feature <name>` - Enable specific features only
- [ ] Output formats:
  - [ ] Human-readable text
  - [ ] JSON (for tooling)
  - [ ] GitHub Actions annotations

### Safety & Quality

- [ ] Dry-run mode by default for destructive changes
- [ ] Confidence levels for transforms (only apply high-confidence by default)
- [ ] Preserve formatting as much as possible with libcst
- [ ] Generate git-compatible diffs
- [ ] Backup original files option
- [ ] Incremental mode (only process changed files)
- [ ] Exit codes for CI integration
- [ ] Comprehensive logging

---

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

---

## Future Enhancements (V2+)

- [ ] Auto-fix unused imports
- [ ] Suggest import aliases for long names
- [ ] Detect and fix import shadowing
- [ ] Optimize import order beyond isort
- [ ] Integration with LSP for editor support
- [ ] Pre-commit hook integration
- [ ] GitHub Action
- [ ] Support for other languages (via plugins?)
- [ ] Performance optimization (parallel processing)
- [ ] Caching for large codebases
- [ ] Watch mode for continuous checking

---

## Release Checklist

### v0.1.0 - MVP

- [ ] TYPE_CHECKING migration working
- [ ] Basic CLI functional
- [ ] Core tests passing
- [ ] README with examples
- [ ] MIT License

### v0.2.0 - Full Features

- [ ] All 5 core features implemented
- [ ] Config integration complete
- [ ] Comprehensive test suite
- [ ] Documentation site

### v1.0.0 - Production Ready

- [ ] Battle-tested on real projects
- [ ] Performance optimized
- [ ] Full CI/CD pipeline
- [ ] Publish to PyPI
- [ ] Community feedback incorporated

---

## Current Priority

**Phase 1: Complete TYPE_CHECKING Migration** (Current focus)

1. Finish usage_tracker.py
2. Add type annotation detection
3. Implement transformer for TYPE_CHECKING blocks
4. Write comprehensive tests
5. Manual testing on real code

Once Phase 1 is solid, move to Phase 2 (Relative/Absolute normalization) or Phase 3 (Circular dependency detection) based on what's most valuable.

---

## 1. Purpose

This tool statically analyzes Python source code to **lint, normalize, and refactor imports** according to a strict, opinionated policy. Its goal is to eliminate the *common* causes of import-related bugs (ordering, cycles, ambiguity, star imports, path hacks) while **never silently changing runtime behavior**.

The tool is explicitly **best‑effort**: when correctness cannot be proven statically, it reports diagnostics and refuses to autofix.

---

## 2. Non‑Goals (Hard Boundaries)

The tool does **not**:

- Execute Python code
- Emulate import hooks or dynamic loaders
- Rewrite `sys.path` mutations
- Resolve imports that depend on runtime state
- Guarantee elimination of all circular dependencies
- Rewrite code that cannot be proven safe

Failure to autofix is a **designed outcome**, not an error.

---

## 3. Operating Assumptions

All analysis and rewrites assume:

- No runtime import hooks (`sys.meta_path` untouched)
- Deterministic filesystem layout
- Imports resolvable under standard PEP 328 / 420 rules
- Python version known (from config)

If these assumptions are violated, affected imports are marked **tainted**.

---

## 4. Import Policy (Enforced Rules)

### 4.1 Absolute vs Relative Imports

- **Within the same package** → relative imports
- **Outside the package** → absolute imports

Enforcement:

- Lint if rule violated
- Autofix only if target resolves unambiguously

---

### 4.2 Star Imports (`from x import *`)

Policy:

- Star imports are forbidden

Autofix conditions (all must hold):

- Target module source is available
- `__all__` is statically defined **or** used symbol set is provably minimal
- No `__getattr__` or dynamic export behavior

Otherwise:

- Emit lint error
- No rewrite

---

### 4.3 Import Formatting

Policy:

- One import per line
- Canonical ordering (stdlib → third‑party → local)

Always safe to autofix.

---

### 4.4 Type‑Only Imports

Policy:

- Symbols used **only** in annotations must not be imported at runtime

Preferred strategies:

1. `from __future__ import annotations`
2. `if TYPE_CHECKING:` blocks

Autofix only if:

- Symbol never appears in runtime context
- Python version compatibility confirmed

---

### 4.5 Circular Dependencies

Policy:

- Circular imports are allowed **only** if proven harmless

Classification:

- Type‑only cycles → allowed / auto‑fixable
- Deferred (function‑local) imports → auto‑fixable
- Attribute‑access during module init → error

Autofix strategies:

- Move imports into functions
- Move imports under `TYPE_CHECKING`
- Split interface vs implementation modules (suggested only)

---

### 4.6 `sys.path` Manipulation

Policy:

- Runtime modification of `sys.path` is forbidden

Behavior:

- Detect and classify mutations
- Mark all downstream imports as tainted
- Emit diagnostics
- **Never autofix**

Suggested remedies only (documentation, packaging, `-m` usage).

---

## 5. Internal Analysis Model

### 5.1 Module Graph

- Nodes: modules
- Edges: imports
- Edge types: runtime / type‑only / optional / star

Used for:

- Cycle detection
- Package boundary decisions

---

### 5.2 Symbol Tables

Per module:

- Definitions
- Imports
- Re‑exports
- `__all__`

---

### 5.3 Usage Map

Tracks symbol usage context:

- Runtime
- Annotation‑only
- Deferred (function scope)

---

### 5.4 Safety Flags

Each import is tagged with:

- resolvable / unresolvable
- safe to rewrite / unsafe
- tainted / clean

---

## 6. Processing Pipeline

### Pass 1: Parse & Index

- Parse AST
- Build module graph
- Build symbol tables

### Pass 2: Resolve

- Resolve names
- Classify imports
- Detect cycles

### Pass 3: Validate

- Check against import policy
- Produce diagnostics

### Pass 4: Rewrite (Best‑Effort)

- Apply **only** provably safe transformations
- Leave all others untouched

---

## 7. Guarantees

The tool guarantees:

- No silent behavior changes
- No speculative rewrites
- Deterministic output
- Clear diagnostics explaining every refusal

The tool does **not** guarantee:

- Full normalization of all imports
- Elimination of all cycles
- Compatibility with dynamic import patterns

---

## 8. Philosophy

This tool treats Python imports as **semantic infrastructure**, not formatting trivia.

Correctness > completeness.
Refusal > corruption.
