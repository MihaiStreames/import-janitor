# 🧹 import-janitor

An opinionated tool to clean up and optimize Python imports.

## Features

- 🔍 Moves type-only imports into `TYPE_CHECKING` blocks
- 📦 Normalizes imports (relative for internal, absolute for external)
- 🔄 Detects circular dependencies
- ✨ Optimizes `__all__` re-exports
- ⚙️ Respects your ruff/isort/black configuration

## Installation

```bash
pip install import-janitor
```

## Usage

```bash
# Analyze a project
import-janitor check myproject/

# Fix imports automatically
import-janitor fix myproject/

# Dry run (show what would change)
import-janitor fix --dry-run myproject/
```
