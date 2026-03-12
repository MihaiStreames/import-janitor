# 🧹 import-janitor

An opinionated Python import fixer. Detects import problems and automatically applies fixes.

Built for developers who want clean imports without thinking about them and for teams who want to enforce that standard in CI.

> **Status:** Pre-alpha. Detection pipeline (`check`) is being built. `diff` and `fix` follow. Do not use in production yet.

---

## What it does

**Detection** (always safe, always stable)

- Finds circular import cycles across your entire project
- Flags `from foo import *` star imports
- Detects unused imports
- Identifies imports that should be behind `TYPE_CHECKING`
- Detects relative imports that should be absolute

**Fixes** (graduated stability - see [Stability Model](#stability-model))

- Rewrites relative imports to absolute
- Inserts `from __future__ import annotations` where missing
- Moves type-only imports behind `TYPE_CHECKING` guards
- Suggests cycle-breaking strategies (manual confirmation required)

---

## Opinions

`import-janitor` is opinionated. These defaults are not configurable (they are kinda the point?).

**Absolute imports, always**

Relative imports (`from . import foo`) are fine in small packages but become a maintenance burden as projects grow. `import-janitor` rewrites them to absolute form. Your imports should be readable without knowing where in the package tree you are.

**All type-only imports behind `TYPE_CHECKING`**

If an import is only used in type annotations, it has no business running at import time. It slows startup, can cause cycles, and signals that your runtime and type-checking concerns are not separated. `import-janitor` moves these behind `if TYPE_CHECKING:` and adds `from __future__ import annotations` to make it work at runtime.

**No star imports, ever**

`from foo import *` is a namespace landmine. It makes it impossible to know where names come from, breaks static analysis, and makes refactoring fragile. `import-janitor` flags every star import. Automatic rewriting is not supported (yet) as it requires runtime introspection to know what `*` expands to.

---

## Stability model

Not all fixes are equal. `import-janitor` uses an explicit stability model so you always know what you're getting.

| Feature | Stable | Experimental |
|---|---|---|
| Cycle detection | x | |
| Star import detection | x | |
| Unused import detection | x | |
| `__future__` insertion | x | |
| Absolute import rewriting | x | |
| `TYPE_CHECKING` guard insertion | | x |
| Lazy import wrapping | | x |
| Cycle-breaking suggestions | | x |

Stable fixes are always available. Experimental fixes require `--experimental` and may produce incorrect results in edge cases. **Always review the diff before applying!**

```bash
# stable only
janitor fix ./src

# stable + experimental
janitor fix ./src --experimental
```

---

## Usage

```bash
# report issues, exit 1 if any found (safe for CI)
janitor check ./src

# show what would change, don't write anything
janitor diff ./src

# apply stable fixes
janitor fix ./src

# apply stable + experimental fixes
janitor fix ./src --experimental

# machine-readable output
janitor check ./src --format json
```

---

## Monorepo support

`import-janitor` understands repo-level vs package-level boundaries.

```
repo/
  packages/
    auth/       <- package boundary
    api/        <- package boundary
    shared/     <- package boundary
```

Importing `shared` from within `api` is treated as an **internal-to-repo, external-to-package** import: it will be written as an absolute import, not a relative one. Importing within `api` itself follows the absolute-only rule too. There are no relative imports anywhere.

Configure package roots in `pyproject.toml`:

```toml
[tool.import-janitor]
packages = ["packages/auth", "packages/api", "packages/shared"]
```

---

## CI / Pre-commit integration

`import-janitor` ships as a pre-commit hook and a GitHub Actions action.

### Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/MihaiStreames/import-janitor
    rev: v0.1.0
    hooks:
      - id: import-janitor
        args: [check]
```

### GitHub Actions

```yaml
# .github/workflows/imports.yml
- uses: MihaiStreames/import-janitor-action@v1
  with:
    path: ./src
    fail-on: cycles,unused  # what triggers exit 1
```

---

## Non-goals

- **!Not a formatter!** Use `ruff format` or `black`. `import-janitor` only touches imports.
- **!Not a linter!** Use `ruff` for general lint. `import-janitor` handles structural import problems linters don't solve.
- **!Not a type checker!** `TYPE_CHECKING` migration uses heuristics, not full type inference. It will sometimes be wrong (that's why it's experimental).
- **!Not magic!** Circular imports are sometimes a symptom of architectural problems. `import-janitor` can suggest fixes but cannot redesign your module structure.

---

## Python version support

`import-janitor` supports Python 3.11 and above, through the 3.14 beta series (to confirm).

[!note]
> Python 3.14 compatibility is tested against the beta release. PEP 690 lazy import support targets the 3.14 final specification. *Behavior may change as the spec settles.*

## License

MIT. Do what you want with it.
