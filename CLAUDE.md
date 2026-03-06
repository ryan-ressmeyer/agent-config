# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A library of Claude Code skills for a solo visual neuroscience researcher. Skills codify the scientific process — literature discovery, grant writing, experimentation, data analysis, publication — into reusable LLM-assisted workflows. Sources: [obra/superpowers](https://github.com/obra/superpowers) (process skills) and [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) (scientific skills).

## Architecture

Each skill is a directory at the repo root containing:
- `SKILL.md` — the main skill document (required), with YAML frontmatter (`name`, `description`)
- `references/` — heavy reference material (markdown files)
- `assets/` — templates
- `scripts/` — Python scripts with PEP 723 inline metadata (run via `uv run script.py`, NOT bare `python`)

### Skill Categories

- **Process/meta skills**: `skills-prelude`, `designing-plans`, `writing-plans`, `executing-plans`, `dispatching-parallel-agents`, `verification-before-completion`, `writing-skills`, `python-environment`
- **Literature review system**: `literature-review` (orchestrator), `literature-writer`, `citation-fetch`, `pdf-retrieve`, `paper-summarize`, `database-check`, `database-search`, `theme-synthesize` — see `literature-review-system.md` for design doc
- **Scientific domain skills**: `citation-management` (legacy), `scientific-brainstorming`, `scientific-critical-thinking`, `scientific-visualization`, `scientific-writing`, `research-grants`
- **Software engineering skills**: `systematic-debugging`, `test-driven-development`

### Key Conventions

- **Skills are invoked via the `Skill` tool**, not by reading SKILL.md files directly
- **`skills-prelude`** bootstraps skill discovery — invoke relevant skills BEFORE any response
- **Python**: ALL execution goes through `uv run`. Never use bare `python`, `python3`, or `pip`. Skill scripts use PEP 723 inline metadata for self-contained dependency management, separate from any project environment.
- **Skill descriptions** must start with "Use when..." and describe only triggering conditions, never workflow summaries (Claude will shortcut on description summaries instead of reading the full skill)
- **New skills follow TDD**: baseline test (RED) → write skill (GREEN) → close loopholes (REFACTOR). See `writing-skills` skill.

## Running Skill Scripts

```bash
# All Python scripts use PEP 723 inline metadata — uv handles deps automatically
# Literature review system scripts:
uv run citation-fetch/scripts/fetch_metadata.py --doi <doi>
uv run citation-fetch/scripts/fetch_citation_graph.py --doi <doi> --paper-id <id> --output-dir references/<id>/
uv run pdf-retrieve/scripts/find_open_access.py --doi <doi>
uv run paper-summarize/scripts/update_index.py --database references/ --id <id> --title "..."
uv run paper-summarize/scripts/update_bibtex.py --database references/ --id <id> --entry '...'
uv run database-check/scripts/check_integrity.py references/
uv run database-search/scripts/search_database.py "query" --database references/
```

## Rendering Skill Flowcharts

```bash
# Render Graphviz dot diagrams embedded in SKILL.md files
./writing-skills/render-graphs.js <skill-directory>
./writing-skills/render-graphs.js <skill-directory> --combine
```
