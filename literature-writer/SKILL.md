---
name: literature-writer
description: Use when writing scientific paper sections (introduction, discussion, or any section needing citations) that should draw on papers from the literature database
---

# Literature Writer

## Overview

Use the literature database to assist writing scientific papers. Draws citations exclusively from the database, builds narrative arcs from theme documents, and flags gaps where needed papers are missing.

## When to Use

- Writing an introduction that needs to cite prior work
- Writing a discussion connecting results to existing literature
- Inserting citations into any manuscript section
- Building a narrative arc for a paper's background
- Checking if claims in a draft have citation support in the database

## Database Context

Reads from a literature database (default: `references/`):
- `index.yaml` — paper metadata and short summaries
- `references.bib` — BibTeX entries for LaTeX citation keys
- `themes/*.md` — thematic syntheses
- `<id>/<id>-summary.md` — QLMRI summaries

## Workflow

### Step 1: Understand the Writing Task

Ask the user:
- What section are they writing? (introduction, discussion, methods background, etc.)
- What is the central claim or narrative?
- What citation style? (LaTeX `\cite{key}`, numbered, author-year, etc.)

### Step 2: Search the Database

Find relevant papers using `database-search`:

```bash
uv run ~/.claude/skills/database-search/scripts/search_database.py "query terms" \
  --database references/ \
  [--subject macaque] \
  [--theme orientation-selectivity] \
  [--year-min 2015]
```

Also read relevant theme documents — they already contain synthesized narratives that can inform the writing.

### Step 3: Load Context

For each relevant paper, read:
1. The `index.yaml` short summary (always)
2. The QLMRI summary (for papers central to the argument)
3. Theme documents (for narrative structure)
4. Key figures (reference where they support the text)

### Step 4: Draft Text

Write the section with inline citations:

**For LaTeX:**
```latex
Orientation selectivity in V1 has been studied extensively in macaque
\cite{smith-jones-2019, lee-park-2021}. Early feedforward models
\cite{hubel-wiesel-1962} could not account for the temporal sharpening
observed in population recordings \cite{smith-jones-2019}.
```

**For markdown/general:**
```markdown
Orientation selectivity in V1 has been studied extensively in macaque
(Smith & Jones, 2019; Lee & Park, 2021). Early feedforward models
(Hubel & Wiesel, 1962) could not account for the temporal sharpening
observed in population recordings (Smith & Jones, 2019).
```

**Citation keys** always use the database paper IDs (e.g., `smith-jones-2019`) which match `references.bib` keys.

### Step 5: Flag Gaps

If a claim needs a citation but no supporting paper exists in the database:

> "This claim about X needs a citation, but I don't have a supporting paper in the database. Would you like to search for one?"

Offer to switch to `literature-review` to add the missing paper.

### Step 6: Reference Key Figures

When a figure from the database illustrates a point being discussed:

> "Smith & Jones (2019), Fig. 2 shows the temporal sharpening you're describing — you might reference this in the text or include a version as a figure in your manuscript."

## Section-Specific Guidance

### Introduction

- Build from theme documents — they already trace historical arcs
- Start broad, narrow to the specific question
- Cite foundational work first, then recent advances
- End with the gap your paper fills
- Every claim needs a citation

### Discussion

- Connect your results to specific findings in the database
- Use QLMRI summaries to make precise comparisons (your methods vs. theirs, your results vs. theirs)
- Acknowledge when your findings conflict with database papers
- Note species/model differences between your work and cited papers
- Suggest future directions informed by open questions in theme documents

### Methods (Background)

- When methods build on prior work, cite the originals
- Use QLMRI Methods sections for accurate descriptions of what prior papers did

## Rules

1. **Only cite papers in the database.** Never fabricate citations or cite papers you haven't verified are in `index.yaml`.
2. **Use database citation keys.** Keys match the paper ID format (`firstauthor-seniorauthor-year`) and are already in `references.bib`.
3. **Flag gaps, don't guess.** If a citation is needed but missing, tell the user.
4. **Match the user's style.** LaTeX `\cite{}`, author-year, numbered — follow whatever they're using.
5. **Be specific in citations.** Don't just cite a paper — say what finding from that paper supports the claim.
6. **Note subject differences.** If citing a macaque study to support a claim about mouse, flag the species gap.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Citing papers not in the database | Only cite papers in index.yaml — flag gaps instead |
| Generic citations ("as shown previously") | Specify what was shown and by whom |
| Ignoring species/model differences | Note when cited evidence is from a different subject |
| Writing a literature review instead of an argument | The intro/discussion should argue a point, not just review |
| Using wrong citation keys | Always use the paper ID from the database |
| Not checking theme documents | Themes contain pre-built narrative arcs — use them |
