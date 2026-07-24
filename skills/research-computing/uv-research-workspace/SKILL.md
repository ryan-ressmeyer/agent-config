---
name: uv-research-workspace
description: Use when creating a new Python research project workspace, adding sub-repositories to an existing workspace, or managing cross-repo dependencies with uv workspaces
---

# UV Research Workspace

## Overview

Manage Python research projects as **uv workspaces with git sub-repositories**. Each sub-repo is its own git repo and Python package, but all share a single `.venv` via the workspace. This gives you modularity (reusable code split across repos), reproducibility (locked dependencies), and flexibility (each repo also works standalone).

## Why This Pattern

Research code tends toward either monolithic repos (hard to reuse across projects) or scattered repos (dependency hell, `sys.path` hacks, duplicated code). The uv workspace pattern solves both:

- **Shared environment**: one `.venv`, one `uv sync`, all repos see each other
- **Independent repos**: each sub-repo has its own git history, can be cloned alone
- **Standalone fallback**: PEP 508 `@ git+...` URLs in dependency lines mean repos work outside the workspace too
- **Future-proof**: new paper repos just declare dependencies on existing utility repos

## The Dual Dependency Pattern

This is the critical technique. When one workspace member depends on another:

```toml
# In [project] dependencies — the git URL is used when this repo is standalone
dependencies = [
    "my-utils @ git+https://github.com/user/my-utils",
]

# In [tool.uv.sources] — workspace resolution overrides the git URL
[tool.uv.sources]
my-utils = { workspace = true }
```

**How it works:**
- **Inside workspace**: `{ workspace = true }` takes priority, resolves to the local checkout
- **Outside workspace**: `[tool.uv.sources]` is ignored, the `@ git+...` URL is used

This also works for optional dependencies:
```toml
[project.optional-dependencies]
extras = [
    "OtherRepo @ git+https://github.com/user/OtherRepo",
]

[tool.uv.sources]
OtherRepo = { workspace = true }
```

## Operation 1: Create a New Workspace

### Step 1: Create the root directory and git repo

```bash
mkdir my-project && cd my-project
git init
```

### Step 2: Create root `pyproject.toml`

```toml
[project]
name = "my-project"
version = "0.0.0"
description = "Description of the research project"
requires-python = ">=3.11, <3.13"

[tool.uv.workspace]
members = [
    # Add sub-repos here as they are added
]
```

- `requires-python` should be consistent across all members.
- The root project has no dependencies of its own — it just defines the workspace.

### Step 3: Add sub-repos

Clone existing repos or create new ones (see Operation 2). Add each to the `members` list.

### Step 4: Create `clone.sh`

A convenience script that clones all member repos:

```bash
#!/bin/bash
git clone https://github.com/user/repo1
git clone https://github.com/user/repo2
```

This is how collaborators (or you on a new machine) reconstruct the workspace.

### Step 5: Create `.gitignore`

```
.venv/
__pycache__/
*.egg-info/
```

### Step 6: Create `CLAUDE.md`

Create a root-level `CLAUDE.md` that documents the workspace structure, member repos, and conventions. Keep it up to date as the project evolves.

### Step 7 (optional): Register IPython kernel

Ask the user if they want a shared IPython kernel for VSCode/Jupyter:

```bash
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=my-project
```

This creates one kernel for the whole workspace. Do not create per-repo kernels.

### Step 8: Sync and verify

```bash
uv sync --all-packages
```

## Operation 2: Add a Sub-Repo

### Option A: Clone an existing repo

```bash
git clone https://github.com/user/existing-repo
```

### Option B: Create a new repo

```bash
mkdir new-repo && cd new-repo
git init
```

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "new-repo"
version = "0.0.0"
description = "What this repo does"
requires-python = ">=3.11, <3.13"
dependencies = []

[tool.setuptools.packages.find]
where = ["."]
```

### Wire it into the workspace

1. Add to root `pyproject.toml` members list:
   ```toml
   [tool.uv.workspace]
   members = [
       "existing-member",
       "new-repo",
   ]
   ```

2. Add to `clone.sh`

3. If it depends on other workspace members, use the dual dependency pattern (see below)

4. If other members depend on it, update their `pyproject.toml` files too

5. Verify: `uv sync --all-packages`

## Operation 3: Manage Cross-Repo Dependencies

### Adding a dependency on another workspace member

In the dependent repo's `pyproject.toml`, add both pieces:

```toml
[project]
dependencies = [
    "other-repo @ git+https://github.com/user/other-repo",
]

[tool.uv.sources]
other-repo = { workspace = true }
```

### Adding an optional dependency group

```toml
[project.optional-dependencies]
extras = [
    "OtherRepo @ git+https://github.com/user/OtherRepo",
]

[tool.uv.sources]
OtherRepo = { workspace = true }
```

A downstream repo can pull in the extras:
```toml
dependencies = [
    "upstream-repo[extras] @ git+https://github.com/user/upstream-repo",
]
```

### Removing a cross-repo dependency

Remove from both `dependencies` (or `optional-dependencies`) and `[tool.uv.sources]`.

### After any change

Always verify:
```bash
uv sync --all-packages
```

If resolution fails, check:
- Package name in `dependencies` matches the `name` in the dependency's `pyproject.toml`
- The repo is listed in workspace `members`
- `{ workspace = true }` is present in sources for every workspace member that appears in dependencies

## Key Rules

- **One `.venv` for the whole workspace.** Never create per-repo venvs.
- **Always use `uv run`** — never bare `python` or `pip`.
- **`requires-python` must be consistent** across all workspace members.
- **All sub-repos use `setuptools` build backend** with `[tool.setuptools.packages.find]`.
- **Verify with `uv sync --all-packages`** after any structural change.
- **Keep CLAUDE.md updated** as workspace structure evolves.
