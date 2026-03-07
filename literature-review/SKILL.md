---
name: literature-review
description: Use when building or expanding a literature database, adding papers, summarizing research, exploring citation graphs, or interactively reviewing scientific literature on a topic
---

# Literature Review

## Overview

Interactive orchestrator for building a paper database one paper at a time. The user drives the pace — the agent speeds up and organizes the process of collecting, summarizing, and synthesizing scientific literature.

**This is not automation.** The goal is collaborative learning: the user reads and engages with each paper while the agent handles metadata, organization, and discovery of related work.

## When to Use

- Starting a literature review on a new topic
- Adding papers to an existing database
- User provides a DOI, PMID, title, or PDF to process
- User asks questions about papers in the database
- User wants to explore what's related to a paper they just read
- User wants to synthesize themes across papers

## Database Location

Default: `references/` in the current working directory.

Check `CLAUDE.md` for override:
```markdown
## Literature Database
Database path: /path/to/references
```

Or ask the user at session start if unclear.

## Core Loop

```
User provides topic / paper / question
  → Route to appropriate mode
  → Execute sub-skills
  → Present results for review
  → Surface candidates for next papers
  → User decides next step
  → Repeat
```

## Modes

### Discovery Mode

**Trigger:** User gives a topic or asks "what papers exist about X?"

1. Use `citation-fetch` to search Semantic Scholar / PubMed:
   ```bash
   uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --query "search terms" --limit 10
   ```
2. Present results with titles, authors, years, and abstracts
3. User selects which papers to add
4. For each selected paper, proceed to Processing Mode

### Processing Mode

**Trigger:** User provides a DOI, PMID, title, or says "add this paper"

Execute these sub-skills in sequence:

1. **citation-fetch** — Get metadata, generate index entry and BibTeX
   ```bash
   uv run ~/.claude/skills/citation-fetch/scripts/fetch_metadata.py --doi 10.xxx/yyy
   ```

2. **citation-fetch** — Get citation graph (references, cited-by, related)
   ```bash
   uv run ~/.claude/skills/citation-fetch/scripts/fetch_citation_graph.py \
     --doi 10.xxx/yyy \
     --paper-id firstauthor-seniorauthor-year \
     --output-dir references/firstauthor-seniorauthor-year/ \
     --database-path references/
   ```

3. **pdf-retrieve** — Find and download the PDF
   ```bash
   uv run ~/.claude/skills/pdf-retrieve/scripts/find_open_access.py --doi 10.xxx/yyy
   ```
   - If open-access URL found: download with `curl`
   - If not found: ask the user to place it at `references/<id>/<id>.pdf`

4. **paper-summarize** — Read PDF, write QLMRI summary, update index and bib
   - Read the PDF with the user
   - Write QLMRI summary to `references/<id>/summary.md`
   - Update `index.yaml` (note: `--database` takes the **directory**, not the yaml file; `--authors` and `--subject` take **JSON strings**; `--has-pdf`/`--has-summary` take **"true"/"false"** not bare flags):
     ```bash
     uv run ~/.claude/skills/paper-summarize/scripts/update_index.py \
       --database references/ \
       --id firstauthor-seniorauthor-year \
       --title "Paper title" \
       --authors '["Last, First", "Last2, First2"]' \
       --year 2019 \
       --journal "Journal Name" \
       --doi "10.xxx/yyy" \
       --subject '["macaque"]' \
       --summary "1-3 sentence summary" \
       --status summarized \
       --has-pdf true \
       --has-summary true
     ```
   - Update `references.bib` (pass BibTeX via `--entry` string or `--entry-file`):
     ```bash
     uv run ~/.claude/skills/paper-summarize/scripts/update_bibtex.py \
       --database references/ \
       --id firstauthor-seniorauthor-year \
       --entry '@article{firstauthor-seniorauthor-year,
         author = {Last, First and Last2, First2},
         title = {Paper title},
         journal = {Journal Name},
         year = {2019},
         doi = {10.xxx/yyy}
       }'
     ```
   - Present summary for review

5. **Surface next papers** — Show candidates from citation graph
   - "This paper cites N papers not in your database..."
   - "It's cited by M papers..."
   - "I found K related papers..."
   - "Would you like to add any of these next?"

### Synthesis Mode

**Trigger:** User asks about themes, patterns, or connections across papers

1. Use `database-search` to find relevant papers
2. Use `theme-synthesize` to create/update theme documents
3. Present synthesis for review

### Question Mode

**Trigger:** User asks a question about the literature

1. Use `database-search` to find relevant papers:
   ```bash
   uv run ~/.claude/skills/database-search/scripts/search_database.py "query" --database references/
   ```
2. Read relevant summaries and theme documents
3. Answer with citations to papers in the database
4. Flag if the question requires papers not yet in the database

### Maintenance Mode

**Trigger:** User asks to check or clean up the database

1. Run `database-check`:
   ```bash
   uv run ~/.claude/skills/database-check/scripts/check_integrity.py references/ --verbose
   ```
2. Present issues found
3. Offer to fix auto-fixable issues
4. Suggest papers that need summaries, themes that need updating

## Session Awareness

At the start of a session, if a database exists:
- Load `index.yaml` to understand what's already collected
- Note how many papers, which themes exist, any gaps
- Briefly tell the user: "Your database has N papers across M themes. N papers have summaries."

## Key Behaviors

- **One paper at a time.** Never batch-process. The user should engage with each paper.
- **Always surface candidates.** After processing a paper, show related work from citation graph.
- **Respect the user's pace.** Don't push to add more papers — present options and let them choose.
- **Use scripts for data operations.** Metadata fetching, index updates, and integrity checks go through Python scripts. Summary writing and synthesis are agent work.
- **Only cite what's in the database.** When answering questions, reference database papers. Flag gaps.
- **Suggest themes organically.** As the database grows, propose theme connections.

## Sub-Skill Reference

| Sub-Skill | Purpose | Has Scripts |
|-----------|---------|-------------|
| `citation-fetch` | Metadata + citation graph retrieval | `fetch_metadata.py`, `fetch_citation_graph.py` |
| `pdf-retrieve` | Find/download PDFs | `find_open_access.py` |
| `paper-summarize` | QLMRI summaries, index/bib updates | `update_index.py`, `update_bibtex.py` |
| `database-check` | Integrity verification | `check_integrity.py` |
| `database-search` | Local database search | `search_database.py` |
| `theme-synthesize` | Cross-paper thematic synthesis | (agent-driven) |
