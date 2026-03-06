---
name: theme-synthesize
description: Use when creating or updating cross-paper thematic synthesis documents that trace how ideas evolved across multiple papers in the literature database
---

# Theme Synthesize

## Overview

Create or update a thematic synthesis document in `themes/` that traces how an idea, method, or phenomenon evolved across multiple papers. This is a **synthesis**, not a list of summaries — it reads as a coherent narrative.

## When to Use

- User asks about patterns or themes across papers in the database
- Enough papers (3+) share a theme tag and no synthesis exists yet
- A new paper was added that significantly changes an existing theme narrative
- User explicitly asks to synthesize or connect papers on a topic

## Database Context

Theme documents live at `references/themes/<theme-name>.md`. Each theme document lists the papers it covers in its YAML frontmatter — this is the sole source of truth for theme-paper associations (individual paper entries in `index.yaml` do NOT have theme tags).

## Workflow

### Step 1: Gather Papers

Collect all papers tagged with the theme from `index.yaml`, or use a list provided by the user. Read their summaries.

If using `database-search`:
```bash
uv run database-search/scripts/search_database.py --theme <theme-name> --database references/
```

### Step 2: Read Summaries

Read each paper's `<id>-summary.md`. Focus on:
- Questions asked (do they evolve over time?)
- Methods used (do they improve?)
- Results (do they converge or conflict?)
- Inferences (how does understanding shift?)
- Subject/preparation (does the finding generalize across species/models?)

### Step 3: Write the Synthesis

Create `themes/<theme-name>.md` following this structure:

```markdown
# Theme Title — Descriptive Subtitle

## Overview
2-3 sentences framing the core question this theme addresses.

## Historical Arc
Chronological narrative tracing how understanding evolved.
Group by eras or turning points, not by individual paper.

1. **Early work (Years)** — Who established the foundation? What was the initial framing?
2. **Key advances (Years)** — What shifted the field? New methods, surprising results?
3. **Current state (Years)** — Where does understanding stand now?

## Key Findings Across Papers
Synthesized findings organized by sub-question or claim.
Compare and contrast across papers. Note:
- Points of agreement
- Points of disagreement or tension
- Methodological differences that might explain discrepancies
- Species/model differences

## Key Figures
Reference the most illustrative figures from papers in the database:

LastName & SeniorAuthor (Year), Fig. N — description of what it shows:
![Caption](../paper-id/paper-id-figures/figN-description.png)

## Methodological Evolution
How have the methods for studying this question changed?
What can newer methods reveal that older ones couldn't?

## Open Questions
- What remains unknown?
- What contradictions are unresolved?
- What experiments would help?

## Papers in This Theme
- paper-id-1
- paper-id-2
- paper-id-3
```

### Step 4: Present for Review

Show the draft to the user. Ask:
- "Does this narrative accurately capture the arc of this topic?"
- "Are there papers I should include that aren't in the database yet?"
- "Any themes you'd like to split or merge?"

## Writing Principles

- **Synthesize, don't summarize.** "Three studies found X" not "Study A found X. Study B also found X."
- **Show evolution.** How did later work build on or challenge earlier work?
- **Note species/model differences.** A finding in macaque that hasn't been tested in mouse is different from a finding replicated across species.
- **Be specific.** Include effect sizes, sample sizes, methodological details where they matter for the narrative.
- **Reference key figures.** Point to the most compelling visualizations in the database.
- **Flag gaps.** What should have been studied but wasn't?

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Study-by-study summaries | Organize by theme/question, not by paper |
| Missing chronological context | Show how ideas evolved over time |
| Ignoring methodological differences | Note when different methods yield different results |
| No species/model comparison | Always note which subjects were used across studies |
| Forgetting to update theme tags | Run update_index.py for all papers in the theme |
| Static document | Update when new papers are added to the theme |
