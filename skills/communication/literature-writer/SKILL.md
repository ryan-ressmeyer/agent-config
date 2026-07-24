---
name: literature-writer
description: Use when writing scientific paper sections (introduction, discussion, or any section needing citations) that should draw on papers from the literature database
---

# Literature Writer

## Overview

Use the literature database to assist writing scientific paper sections. Draws citations exclusively from the database, connects findings across papers, and flags gaps where needed papers are missing. All claims must be grounded in what the cited papers actually found.

## When to Use

- Writing an introduction that needs to cite prior work
- Writing a discussion connecting results to existing literature
- Inserting citations into any manuscript section
- Building a narrative arc for a paper's background
- Checking if claims in a draft have citation support in the database

## Database Context

The literature database lives in ansa (default remote: `kamaji`). Citation keys are paper `properties.citekey`. Pull context with `ansa` over HTTP:

- `ansa search "<query>"` — full-text across titles, abstracts, scratchpads, notes, collections
- `ansa query '{"type":"paper","where":{...}}'` — structured filters (year, journal, citekey, etc.)
- `ansa paper scratchpad <UUID>` — the user's QLMRI summary for a paper
- `ansa collection ls --kind theme` + `ansa collection members <theme-uuid>` — thematic syntheses (the synthesis text is a `note` attached to the theme collection; pull it via `GET /api/nodes/<theme-uuid>/notes`)
- `ansa paper similar <UUID>` — semantic neighbors when looking for adjacent work

No `index.yaml`, no `references.bib`, no `references/<id>/` folders. BibTeX export from ansa is not implemented yet — when the manuscript needs a `.bib`, ask the user or assemble manually from `ansa node get <UUID>` metadata.

## Workflow

### Step 1: Understand the Writing Task

Ask the user:
- What section are they writing? (introduction, discussion, methods background, etc.)
- What is the central claim or narrative?
- What citation style? (LaTeX `\cite{key}`, numbered, author-year, etc.)

### Step 2: Search the database

Find relevant papers:

```bash
ansa search "query terms"
# or structured:
ansa query '{"type":"paper","where":{"year":{"ge":2015}},"limit":50}'
```

For theme-level narrative, pull existing theme syntheses:

```bash
ansa collection ls --kind theme
ansa collection members <theme-uuid>
curl -s http://kamaji:7327/api/nodes/<theme-uuid>/notes
```

### Step 3: Load context

For each relevant paper, read its scratchpad — that's the user's QLMRI summary:

```bash
ansa paper scratchpad <paper-uuid>
```

Also pull node metadata for the citation skeleton:

```bash
ansa node get <paper-uuid>
```

When the writing draws on a theme, read the synthesis note attached to the theme collection before drafting — it already contains the narrative connections.

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

**Citation keys** are each paper's `properties.citekey` in ansa (e.g., `smith-jones-2019`, `vaswani2017attention`). Get one with `ansa node get <uuid> | jq -r '.properties.citekey'`.

### Step 5: Flag Gaps

If a claim needs a citation but no supporting paper exists in the database:

> "This claim about X needs a citation, but I don't have a supporting paper in the database. Would you like to search for one?"

Offer to switch to `ansa-literature-review` to add the missing paper.

### Step 6: Reference Key Figures

When a figure from the database illustrates a point being discussed:

> "Smith & Jones (2019), Fig. 2 shows the temporal sharpening you're describing — you might reference this in the text or include a version as a figure in your manuscript."

## Section-Specific Guidance

### Introduction

- Consult theme documents for which papers relate to each other and how
- Start broad, narrow to the specific question
- Every factual claim needs a citation attributed to specific authors
- End with the gap your paper fills
- Do not write "it is well known that" or "extensive work has shown" — state what specific papers found

### Discussion

- Connect your results to specific findings in the database
- Use QLMRI summaries to make precise comparisons (your methods vs. theirs, your results vs. theirs)
- Acknowledge when your findings conflict with database papers
- Note species/model differences between your work and cited papers
- Suggest future directions informed by open questions in theme documents

### Methods (Background)

- When methods build on prior work, cite the originals
- Use QLMRI Methods sections for accurate descriptions of what prior papers did

## Objectivity Directives (MANDATORY)

Scientific writing makes arguments, but those arguments must be grounded in what the cited papers actually reported. You are working from a limited database, not the full literature.

1. **Attribute findings to specific papers.** Write "Burr et al. (1994) found X" not "it has been shown that X" or "X is well established." Every factual claim needs an author attached.
2. **Don't overstate what a citation supports.** If a paper found something in cat, don't cite it as though the finding applies to all mammals. State what was found and in what preparation.
3. **Don't claim consensus from your database.** You have a subset of the literature. Don't write "it is widely accepted" or "extensive evidence demonstrates" based on a handful of papers. State what the specific cited papers found.
4. **Avoid superlatives and certainty language.** Do not write "clearly demonstrates," "conclusively shows," "the most important," "a landmark study," etc. Describe findings neutrally.
5. **Distinguish authors' conclusions from facts.** "Burr et al. (1994) concluded that suppression occurs before V1" is different from "suppression occurs before V1." Use the former when the claim is an interpretation.
6. **Don't narrate history you haven't read.** Don't write "the first study to show X" or "pioneering work by" unless the paper itself makes that claim. You haven't read the whole literature.
7. **Flag what you don't know.** If the database doesn't have papers representing an alternative viewpoint, say so rather than writing as though the available papers tell the whole story.

## Rules

1. **Only cite papers in the database.** Never fabricate citations or cite papers you haven't verified exist in ansa (`ansa search` or `ansa query` first).
2. **Use database citation keys.** Keys come from each paper's `properties.citekey` (`firstauthor-seniorauthor-year` shape).
3. **Flag gaps, don't guess.** If a citation is needed but missing, tell the user.
4. **Match the user's style.** LaTeX `\cite{}`, author-year, numbered — follow whatever they're using.
5. **Be specific in citations.** Don't just cite a paper — say what finding from that paper supports the claim.
6. **Note subject differences.** If citing a macaque study to support a claim about mouse, flag the species gap.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Citing papers not in the database | Verify with `ansa search` / `ansa query` before citing; flag gaps |
| Generic citations ("as shown previously") | Specify what was shown and by whom |
| Ignoring species/model differences | Note when cited evidence is from a different subject |
| Using wrong citation keys | Always use the paper ID from the database |
| Not checking theme documents | Themes show how papers in the database relate to each other |
| "It is well established that X" | State what specific papers found — don't claim consensus from a small database |
| Superlatives ("landmark study," "clearly demonstrates") | Describe findings neutrally without editorializing |
| Elevating authors' interpretations to fact | "Authors concluded X" not "X is the case" when the claim is an inference |
| Claiming historical firsts ("the first to show") | Don't assert priority unless the paper itself does — you haven't read the full literature |
