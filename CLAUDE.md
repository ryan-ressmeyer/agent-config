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
- **Scientific domain skills**: `citation-management`, `literature-review`, `scientific-brainstorming`, `scientific-critical-thinking`, `scientific-visualization`, `scientific-writing`, `research-grants`
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
uv run citation-management/scripts/doi_to_bibtex.py <doi>
uv run citation-management/scripts/search_pubmed.py <query>
uv run literature-review/scripts/generate_pdf.py <args>
uv run scientific-visualization/scripts/figure_export.py <args>
```

## Rendering Skill Flowcharts

```bash
# Render Graphviz dot diagrams embedded in SKILL.md files
./writing-skills/render-graphs.js <skill-directory>
./writing-skills/render-graphs.js <skill-directory> --combine
```
