# LLM Skills for Scientific Research

A library of Claude Code skills tailored for a solo visual neuroscience researcher. These skills codify the scientific process — from literature discovery through data analysis and publication — into reusable, composable workflows powered by LLM-assisted tooling.

## The Scientific Process & Where Skills Fit

### Phase 1: Discovery & Background Research

Understanding what's known, finding gaps, and building a literature database.

| Skill | Purpose |
|-------|---------|
| **literature-review** | Interactive orchestrator for building a paper database — collecting, summarizing, and synthesizing scientific literature one paper at a time |
| **citation-fetch** | Retrieve citation metadata (from DOI, PMID, arXiv ID, title, or query), generate BibTeX, and fetch citation graphs (references, cited-by, related) |
| **pdf-retrieve** | Obtain paper PDFs, checking open-access sources first and prompting the user when paywalled |
| **paper-summarize** | Read a paper PDF and produce a structured QLMRI summary, then update the literature database |
| **database-search** | Search the local literature database by metadata, full-text, or citation graph connections |
| **database-check** | Verify literature database integrity — missing files, inconsistent metadata, orphaned entries |
| **theme-synthesize** | Create cross-paper thematic synthesis documents tracing how ideas evolved across multiple papers |
| **citation-management** | Legacy skill — Google Scholar/PubMed search, DOI-to-BibTeX extraction, reference validation |

### Phase 2: Manuscript Planning & Analysis

Turning data and literature into a manuscript plan before writing prose.

| Skill | Purpose |
|-------|---------|
| **manuscript-planning** | Collaborative dialogue to identify the strongest questions data can answer, co-design analyses, and organize findings into a narrative |
| **systematic-debugging** | Root-cause analysis for experiment code, data pipelines, and analysis scripts — no fixes without investigation first |
| **test-driven-development** | Write tests first for analysis code, stimulus generation, data processing pipelines |

### Phase 3: Paper Writing & Revision

Drafting, reviewing, and polishing manuscripts.

| Skill | Purpose |
|-------|---------|
| **literature-writer** | Write scientific paper sections drawing citations exclusively from the literature database |
| **manuscript-review** | Orchestrate the full review cycle — structural, line, and copy editing stages with adversarial critique subagents |
| **reverse-outline** | Compress a manuscript into core claims to expose its logical skeleton, then critique for gaps and logical leaps |
| **section-critique** | Adversarial critique of a specific section — believing pass (internal consistency) then doubting pass (questioning assertions) |
| **critique-triage** | Synthesize critiques from multiple section reviews into a deduplicated, prioritized revision plan |
| **copy-review** | Grammar, punctuation, terminology consistency, and stylistic polish before submission |
| **style-guide** | Voice standards and AI pattern elimination for all public-facing prose |

### Process / Meta Skills

These skills govern *how* the other skills get used — planning, execution, and quality control.

| Skill | Purpose |
|-------|---------|
| **skills-prelude** | Bootstraps skill discovery — ensures relevant skills are invoked before any response |
| **designing-plans** | Collaborative ideation for features, components, and designs before implementation |
| **writing-plans** | Create bite-sized implementation plans with exact file paths and commands before touching code |
| **executing-plans** | Execute plans task-by-task with review checkpoints across sessions |
| **verification-before-completion** | No completion claims without fresh verification evidence — the final quality gate |
| **writing-skills** | TDD-based methodology for creating and testing new skills |
| **python-environment** | Enforces `uv run` for all Python execution — project code via `pyproject.toml`/`.venv`, skill scripts via PEP 723 inline metadata. No system Python, ever. |
| **uv-research-workspace** | Create and manage Python research projects as uv workspaces with git sub-repositories |
| **git-commits** | Commit message formatting — single line, no Co-Authored-By trailer |

### Obsidian & Web Content

Skills for working with Obsidian vaults and extracting web content.

| Skill | Purpose |
|-------|---------|
| **obsidian-cli** | Interact with Obsidian vaults via CLI — read, create, search notes, manage tasks/properties, and develop/debug plugins and themes |
| **obsidian-markdown** | Create and edit Obsidian Flavored Markdown — wikilinks, embeds, callouts, frontmatter, tags |
| **obsidian-bases** | Create and edit Obsidian Bases (`.base` files) — views, filters, formulas, summaries for database-like note views |
| **json-canvas** | Create and edit JSON Canvas (`.canvas`) files — nodes, edges, groups for visual canvases, mind maps, flowcharts |
| **defuddle** | Extract clean markdown from web pages using Defuddle CLI — use instead of WebFetch for articles, docs, blog posts |

## Skill Sources

- [obra/superpowers](https://github.com/obra/superpowers) — process skills (designing-plans, planning, debugging, TDD, verification)
- [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — scientific research skills (original templates, since heavily reworked)
