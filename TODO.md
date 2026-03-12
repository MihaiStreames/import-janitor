# TODO

Ordered by dependency. Do not start a section until everything above it is done and tested.

---

## Phase 0 - Foundation

These are prerequisites for everything. Nothing else is started until this is solid.

- [ ] `models.py` - rewrite from scratch
  - [x] `ImportKind` enum: `REGULAR | FROM | STAR | FUTURE`
  - [x] `Import` frozen dataclass with `kind, module, names, alias, is_type_checking, lineno, level`
  - [ ] `ModuleImports` dataclass with `path, module_name, imports`
  - [ ] `Diagnostic` dataclass with `path, lineno, kind, message, fix`
  - [ ] `Fix` dataclass with `kind, lineno, new_text`
  - [ ] `CycleReport` msgspec Struct (for JSON output only)

- [ ] `resolver.py` - rewrite from scratch, keep the logic
  - [ ] `is_stdlib(module: str) -> bool`
  - [ ] `is_third_party(module: str, project_root: Path) -> bool`
  - [ ] `resolve_relative(module, level, current_module) -> str`
  - [ ] Unit tests for all three - edge cases: level=0 no-op, level=2 double-dot, module=None for `from . import x`

- [ ] `parser.py` - new file, replaces the broken `extract_imports` in graph.py
  - [ ] Targeted statement traversal (NOT `ast.walk`)
  - [ ] Correct `TYPE_CHECKING` detection without double-visiting nodes
  - [ ] Handles: top-level imports, `if TYPE_CHECKING:`, imports inside functions/classes (flagged separately)
  - [ ] Unit tests covering: star imports, future imports, relative imports, nested TYPE_CHECKING

---

## Phase 1 - Graph

Depends on: Phase 0

- [ ] `graph.py` - rewrite
  - [ ] `path_to_module(path, root) -> str`
  - [ ] `discover_files(root) -> list[Path]` - respects `.gitignore` and excludes patterns
  - [ ] `build_graph(modules) -> nx.DiGraph` - excludes TYPE_CHECKING edges, excludes stdlib/third-party
  - [ ] `find_cycles(graph) -> list[Cycle]`
  - [ ] Monorepo: accept multiple roots, classify cross-package imports correctly
  - [ ] Unit tests: simple cycle, no cycle, cross-package edge, TYPE_CHECKING edge excluded

---

## Phase 2 - Passes (stable)

Depends on: Phase 1. Each pass is independent so they can be built in parallel.

- [ ] `passes/cycles.py`
  - [ ] Wraps `find_cycles`, emits one `Diagnostic` per cycle (on the module closing the loop)
  - [ ] No Fix - cycle-breaking is manual

- [ ] `passes/unused.py`
  - [ ] Collect `bound_names` from imports
  - [ ] Walk `tree.body` for `ast.Name` references
  - [ ] Handle: `__all__` re-exports, aliases, TYPE_CHECKING imports (never flag these)
  - [ ] Emit `Diagnostic` with `Fix(kind="remove_line")`

- [ ] `passes/absolute.py`
  - [ ] For each import with `level > 0`, resolve and emit replacement
  - [ ] Emit `Diagnostic` with `Fix(kind="replace_line")`

---

## Phase 3 - Rewriter

Depends on: Phase 2

- [ ] `transforms/rewriter.py`
  - [ ] Apply a list of `Fix` objects to source text
  - [ ] Sort fixes by lineno descending (apply bottom-up to preserve line numbers)
  - [ ] Handle: remove_line, replace_line, insert_before
  - [ ] Never write if dry-run
  - [ ] Write atomically (write to temp, rename) - never corrupt a file on failure

---

## Phase 4 - CLI

Depends on: Phase 3

- [ ] `cli.py` - Typer app
  - [ ] `janitor check <path>` - exits 1 if any diagnostics
  - [ ] `janitor diff <path>` - prints unified diff, exits 1 if any diagnostics
  - [ ] `janitor fix <path>` - applies stable fixes, exits 1 if unfixable diagnostics remain
  - [ ] `--experimental` flag - unlocks experimental passes
  - [ ] `--format json` - machine-readable output
  - [ ] `--exclude` - glob patterns to skip

- [ ] `output.py`
  - [ ] Rich formatted output for terminal
  - [ ] JSON serialization via msgspec

---

## Phase 5 - Experimental passes

Depends on: Phase 4 (need the `--experimental` flag infrastructure first)

- [ ] `passes/type_checking.py`
  - [ ] Second AST pass that identifies annotation-only positions
  - [ ] Annotation positions: function args, return types, variable annotations, string annotations
  - [ ] Runtime exclusions: `isinstance()`, `issubclass()`, default arg values, `typing.cast()`
  - [ ] Emit `Diagnostic` with Fix that moves import behind `TYPE_CHECKING` and inserts `from __future__ import annotations`
  - [ ] Document clearly: this is heuristic, it will be wrong sometimes

---

## Phase 6 - CI / Pre-commit

Depends on: Phase 4

- [ ] Pre-commit hook
  - [ ] `hooks:` entry in repo, runnable via `pre-commit install`
  - [ ] Runs `janitor check` only (no auto-fix on commit)
  - [ ] Fast path: only check files changed in the commit (use `--files` arg)

- [ ] GitHub Actions action
  - [ ] `action.yml` with `path` and `fail-on` inputs
  - [ ] Surfaces diagnostics as PR annotations (using `::error file=...` syntax)
  - [ ] Separate action for `fix` + auto-commit (opt-in, not default)

---

## Phase 7 - Packaging

Depends on: Phase 6

- [ ] `pyproject.toml` for both `janitor-core` and `import-janitor`
- [ ] `[tool.import-janitor]` config section in user's `pyproject.toml`
  - [ ] `packages` - list of package roots (monorepo support)
  - [ ] `exclude` - glob patterns
  - [ ] `experimental` - bool, replaces the flag for CI use
- [ ] Publish `janitor-core` to PyPI separately (so tools can depend on it without the CLI)

---

## Known limitations (not bugs, won't fix in Python)

- Dynamic imports (`importlib`, `__import__`) - invisible to static analysis
- `from x import *` rewriting - requires runtime introspection
- Speed on large projects - Rust port is the answer, not optimization of Python
- TYPE_CHECKING migration correctness - heuristic by design, documented as experimental
