---
name: python-environment
description: Use once before running any Python script or command — including when invoked as part of another skill. Must be checked before ANY Python execution to ensure correct environment usage. NEVER use system python — always route through uv.
---

# Python Environment Management

## The Iron Law

**NEVER use bare `python`, `python3`, or `pip` commands. ALL Python execution goes through `uv`.**

System Python is not reproducible. Reproducibility is non-negotiable in science.

## First Contact with a Python Project

When you start working in a directory for the first time, check the environment:

```bash
# Check for existing project environment
ls pyproject.toml .python-version .venv/ 2>/dev/null
```

**If `pyproject.toml` exists:**
1. Run `uv sync` to ensure `.venv` is up to date
2. Use `uv run` for ALL commands: `uv run python script.py`, `uv run pytest`, etc.

**If `pyproject.toml` does NOT exist but the project needs Python:**
1. Initialize with `uv init`
2. Add dependencies with `uv add <package>`
3. Use `uv run` for everything

**If `.venv` exists but no `pyproject.toml`:**
1. This is a legacy setup — ask the user if they want to migrate to `uv`
2. Until migrated, activate the venv: `source .venv/bin/activate`

## Running Project Python Code

Always use `uv run` in project directories:

```bash
# Running scripts
uv run python my_script.py
uv run python -m my_module

# Running tools
uv run pytest
uv run mypy .
uv run ruff check .

# Interactive
uv run python  # starts REPL in project environment
uv run ipython
uv run jupyter lab
```

### Never Do This

| Bad | Why | Good |
|-----|-----|------|
| `python script.py` | Uses system Python, missing project deps | `uv run python script.py` |
| `python3 script.py` | Same problem | `uv run python script.py` |
| `pip install pandas` | Installs to system, not reproducible | `uv add pandas` |
| `pip install -r requirements.txt` | Legacy, not tracked in lockfile | `uv add` each dep or migrate to pyproject.toml |
| `python -m pytest` | Wrong environment | `uv run pytest` |

## Adding Dependencies to Projects

```bash
# Add a runtime dependency
uv add numpy

# Add a dev dependency
uv add --dev pytest ruff mypy

# Add with version constraint
uv add "scipy>=1.10"
```

Never use `pip install` in a project. It bypasses the lockfile and breaks reproducibility.

## Skills Scripts: Inline Metadata (Separate from Projects)

Scripts in the skills library are self-contained — they use [PEP 723 inline script metadata](https://peps.python.org/pep-0723/) and run in isolated cached environments, completely separate from any project.

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "bibtexparser"]
# ///
```

```bash
uv run /path/to/skills/skill-name/scripts/script.py [args]
```

`uv` automatically creates a cached environment per unique dependency set. No setup needed.

### Writing New Skill Scripts

Always include the PEP 723 header. Keep dependency lists minimal — only what the script directly imports.

### Do NOT mix skill deps with project deps

Skill scripts and project code use separate environments. Never install skill dependencies into a project, and never install project dependencies for a skill script.

## Checking uv Availability

If `uv` is not found:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
