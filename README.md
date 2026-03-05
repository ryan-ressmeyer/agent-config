# LLM Skills for Scientific Research

A library of Claude Code skills tailored for a solo visual neuroscience researcher. These skills codify the scientific process — from literature discovery through grant writing, experimentation, data analysis, and publication — into reusable, composable workflows powered by LLM-assisted tooling.

## The Scientific Process & Where Skills Fit

### Phase 1: Discovery & Background Research

The work starts here — understanding what's known, finding gaps, and forming hypotheses.

| Skill | Purpose |
|-------|---------|
| **research-lookup** | Real-time literature search via Perplexity Sonar models for quick background checks and citation verification |
| **citation-management** | Search Google Scholar/PubMed, extract metadata from DOIs/PMIDs, format BibTeX, validate references |
| **literature-review** | Conduct systematic, multi-database literature reviews with screening, data extraction, synthesis, and PDF generation |
| **scientific-critical-thinking** | Evaluate methodology rigor, detect biases, assess statistical validity, identify logical fallacies in existing work |
| **scientific-brainstorming** | Generate novel hypotheses, explore interdisciplinary connections, identify research gaps worth pursuing |

### Phase 2: Grant Writing & Proposal Development

Translating ideas and preliminary findings into funded projects.

| Skill | Purpose |
|-------|---------|
| **research-grants** | Write competitive proposals for NSF, NIH, DOE, DARPA with agency-specific guidelines, templates, and budget prep |
| **scientific-writing** | IMRAD-structured prose, citation formatting, reporting guidelines (CONSORT, STROBE, PRISMA) — used here for aims pages and significance sections |

### Phase 3: Experimentation & Data Analysis

Collecting data (primarily from macaque and potentially marmoset visual neurophysiology experiments) and analyzing results.

| Skill | Purpose |
|-------|---------|
| **systematic-debugging** | Root-cause analysis for experiment code, data pipelines, and analysis scripts — no fixes without investigation first |
| **test-driven-development** | Write tests first for analysis code, stimulus generation, data processing pipelines |
| **scientific-visualization** | Publication-quality matplotlib/seaborn/plotly figures with colorblind accessibility, proper resolution, journal-specific formatting |

### Phase 4: Paper Writing & Publication

Synthesizing everything into manuscripts.

| Skill | Purpose |
|-------|---------|
| **scientific-writing** | Core manuscript skill — full IMRAD structure, two-stage outline-to-prose workflow, field-specific terminology |
| **scientific-visualization** | Data figures for results sections |
| **scientific-slides** | Conference talks, seminars, thesis defense presentations via Beamer templates |
| **citation-management** | Final reference list validation and formatting |

### Meta / Process Skills

These skills govern *how* the other skills get used — planning, execution, and quality control.

| Skill | Purpose |
|-------|---------|
| **skills-prelude** | Bootstraps skill discovery — ensures relevant skills are invoked before any response |
| **designing-plans** | General-purpose ideation for features, components, and designs (software-oriented counterpart to scientific-brainstorming) |
| **writing-plans** | Create bite-sized implementation plans with exact file paths and commands before touching code |
| **executing-plans** | Execute plans task-by-task with review checkpoints across sessions |
| **dispatching-parallel-agents** | Distribute independent tasks to multiple agents working simultaneously |
| **verification-before-completion** | No completion claims without fresh verification evidence — the final quality gate |
| **writing-skills** | TDD-based methodology for creating and testing new skills |
| **python-environment** | Enforces `uv run` for all Python execution — project code via `pyproject.toml`/`.venv`, skill scripts via PEP 723 inline metadata. No system Python, ever. |

## Skill Sources

- [obra/superpowers](https://github.com/obra/superpowers) — process skills (designing-plans, planning, debugging, TDD, verification)
- [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — scientific research skills (writing, visualization, grants, literature review)

## Changelog

- **2026-03-04**: Initial README mapping 20 skills from [superpowers](https://github.com/obra/superpowers) and [claude-code-templates](https://github.com/davila7/claude-code-templates) to a four-phase scientific workflow. Created `python-environment` skill to enforce `uv`-managed Python across all contexts (project code and skill scripts). Added PEP 723 inline metadata to all 11 existing Python scripts. Replaced bare `pip install` references in `citation-management` and `literature-review` SKILL.md files with `uv run` instructions.

## What's Next

- Map skills into concrete end-to-end workflows (e.g., "new project kickoff", "paper revision cycle")
- Adapt skills for visual neuroscience specifics (ephys data formats, stimulus libraries, animal protocol considerations)
- Add new skills for gaps in the pipeline (experimental design, statistical analysis planning, peer review response)
- Develop integration points between skills (e.g., literature review findings flowing into grant aims)
