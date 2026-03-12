# 🧹 import-janitor

A best-effort Python import fixer. Detects import cycles, enforces import hygiene and automatically applies fixes.

Built for developers who want clean imports without thinking about them and for teams who want to enforce that standard in CI.

## What it does

**Detection (always safe, always stable)**

- Finds circular import cycles across your entire project
- Flags `from foo import *` star imports
- Identifies imports that should be behind `TYPE_CHECKING`
- Detects relative imports that should be absolute
- Checks compatibility with PEP 690 lazy import semantics (Python 3.14+)

**Fixes (graduated stability -> see below)**

- Inserts `from __future__ import annotations` where missing
- Rewrites relative imports to absolute
- Moves type-only imports behind `TYPE_CHECKING` guards
- Wraps heavy imports as lazy imports
- Suggests cycle-breaking strategies (manual confirmation required)

## Opinions

`import-janitor` is opinionated. These are not configurable (they are the point):

**Always Absolute Imports**

Relative imports (`from . import foo`) are fine in small packages but become a maintenance burden as projects grow. `import-janitor` rewrites them to absolute form. Your imports should be readable without knowing where in the package tree you are.

**All type-only imports behind `TYPE_CHECKING`**

If an import is only used in type annotations, it has no business running at import time. It slows startup, can cause cycles, and signals that your runtime and type-checking concerns are not separated. `import-janitor` moves these behind `if TYPE_CHECKING:` and adds `from __future__ import annotations` to make it work at runtime.

**No Star Imports Ever**

`from foo import *` is a namespace landmine. It makes it impossible to know where names come from, breaks static analysis, and makes refactoring fragile. `import-janitor` flags every star import and, where possible, rewrites it to explicit names.

**Lazy imports for heavy dependencies**

Slow startup is a symptom of importing everything at module load time. If a dependency is only needed in one code path, it should be imported there or wrapped as a lazy import (PEP 690). `import-janitor` detects heavy imports at module level and can wrap them using Python 3.14's native lazy import semantics or a compatible fallback for earlier versions.

## Stability model

Not all fixes are equal. `import-janitor` uses an explicit stability model so you always know what you're getting:

| Feature | Stable | Unstable |
|---|---|---|
| Cycle detection | x | |
| Star import detection | x | |
| `__future__` insertion | x | |
| Absolute import rewriting | x | |
| `TYPE_CHECKING` guard insertion | | x |
| Lazy import wrapping | | x |
| Cycle-breaking suggestions | | x |

Stable fixes ship in the base package. Unstable fixes require the `unstable` extra and may produce incorrect results in edge cases. ALWAYS review the diff before applying!

```bash
pip install `import-janitor`           # stable only
pip install `import-janitor`[unstable] # includes heuristic fixes
```

## Usage

```bash
# report issues, exit 1 if any found (safe for CI)
janitor check ./src

# show what would change, don't write anything
janitor diff ./src

# apply stable fixes
janitor fix ./src

# apply stable + unstable fixes (requires [unstable])
janitor fix ./src --unstable
```

All commands support `--format json` for machine-readable output.

## Non-goals

- **!Not a formatter!** Use `ruff format` or `black` for formatting. `import-janitor` only touches imports.
- **!Not a linter!** Use `ruff` for general lint rules. `import-janitor` focuses on structural import problems that linters don't solve.
- **!Not a type checker!** It uses heuristics to detect type-only imports, not full type inference. It will sometimes be wrong! There's a reason why fixes are `[unstable]`.
- **!Not magic!** Circular imports are sometimes a symptom of architectural problems. `import-janitor` can suggest fixes, but it cannot redesign your module structure for you.

## Python version support

`import-janitor` supports Python 3.11 and above, through the 3.14 beta series (to confirm).

Python 3.14 compatibility is tested against the beta release. PEP 690 lazy import support targets the 3.14 final specification. *Behavior may change as the spec settles.*

## Architecture

`import-janitor` is split into two packages:

- **`janitor-core`**: the analysis and transformation engine. Pure logic, no CLI concerns. Can be used as a library if you want to build tooling on top of it.
- **`import-janitor`**: the CLI. A thin wrapper around `janitor-core` using Typer and Rich.

A Rust port of the core engine is planned. The Python implementation is the reference. *The Rust port will be a performance optimization, not a rewrite (at least not for now).*

## Status

Pre-alpha. The detection pipeline (`check`) is being built. `diff` and `fix` follow. Do not use in production yet.

## License

MIT. Do what you want with it.
