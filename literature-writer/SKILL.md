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

## Writing Blacklist (MANDATORY)

Apply to all drafts and edits. These patterns are hallmarks of AI-generated prose and must be avoided.

### CRITICAL — never use

| Pattern | Example |
|---------|---------|
| Corrective Escalation | "It's not just X; it's Y" |
| Fragment Pivot | "They ran the test three times. The result? Nothing worked" |
| Weighty Pivot | "But here's the thing:" / "And yet." |
| Forced Exaggeration Adjectives | absolutely, literally, incredibly, utterly |
| Symmetrical Antithesis | "Not about X — about Y" |
| Hedged Superlative | "could be one of the most significant..." |
| Temporal Urgency Frame | "Now, more than ever..." |
| Stacked Intensifiers | "truly remarkable, genuinely unprecedented" |
| Epiphanic Closing | "In the end, maybe the real X was the Y we made..." |
| Self-Congratulation | "We believe this represents a significant contribution" |
| Lexical Gentrification | leverage, synergy, paradigm shift, unpack, scaffold |
| Enumerated Profundity | "There are three things you need to understand about X" |
| Catch Pivot | "But here's the catch:" |
| Real Question Pivot | "The real question is..." |
| Nobody's Talking About | "Here's the thing nobody is talking about" |
| That's the Real Story | "That's the real story" |
| This Is Where It Gets Interesting | "This is where it gets interesting" |
| False Reframe | "It's not about X, it's about Y" |

### HIGH — almost never use

| Pattern | Example |
|---------|---------|
| Uncomfortable Truth Setup | "The uncomfortable truth is..." |
| Rhetorical Question as Transition | "So what does this mean? Let's explore." |
| Throat-Clearing Opener | "In today's rapidly changing landscape..." |
| Cosmic Zoom-Out | "At its core, this is really about what it means to be human" |
| Obvious Concession | "Of course, not everyone agrees. And that's okay." |
| Emphatic Triplet | "Fast. Reliable. Scalable." |
| Passive Voice | "It was found that..." |
| Pregnant Standalone | "She didn't know it yet, but everything was about to change." |
| Stacked Synonyms | "fundamental, foundational, and far-reaching" |
| Nominalization Bloat | "the implementation of this methodology enables the facilitation of" |
| Hollow Adjectives | novel, powerful, robust, challenging, non-trivial |
| What Most People Miss | "What most people miss is..." |
| Why It Matters Header | "Why It Matters" (as a section header or standalone sentence) |

### MODERATE — only with strong justification

| Pattern | Example |
|---------|---------|
| Cascading Relative Clauses | Multiple nested "which/that" clauses |
| Falsely Modest Claim | "While only a small step, this could be a paradigm shift" |
| Paving-the-Way Closer | "This paves the way for future work" |
| Editorial Adverbs | Interestingly, Notably, Remarkably, Crucially |
| Redundant "In other words" | Only valid when re-expressing in a genuinely simpler register |
| Performative Hedging | "It's worth noting that..." / "Importantly,..." |
| False Intimacy Address | "You've probably noticed..." (acceptable in blogs when genuine) |
| Dead Metaphor Labor | "doing the heavy lifting" |

### Voice Principles

- Calm, direct, somewhat information-dense. No decorative sentences.
- Conversational tone is fine when it helps clarity, not when it's performative.
- Adjectives earn their place or get cut.
- Transitions mark real logical moves, not theatrical ones.
- Let results carry their own weight. Never announce their importance.
- Rigorous, always. Especially in papers. Playful in blogs is acceptable, but rigor is maintained.

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
| Using wrong citation keys | Always use the paper ID from the database |
| Not checking theme documents | Themes show how papers in the database relate to each other |
| "It is well established that X" | State what specific papers found — don't claim consensus from a small database |
| Superlatives ("landmark study," "clearly demonstrates") | Describe findings neutrally without editorializing |
| Elevating authors' interpretations to fact | "Authors concluded X" not "X is the case" when the claim is an inference |
| Claiming historical firsts ("the first to show") | Don't assert priority unless the paper itself does — you haven't read the full literature |
