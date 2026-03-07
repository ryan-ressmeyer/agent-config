---
name: theme-synthesize
description: Use when creating or updating cross-paper thematic synthesis documents that trace how ideas evolved across multiple papers in the literature database
---

# Theme Synthesize

## Overview

Create or update a thematic synthesis document in `themes/` that connects findings across multiple papers on a shared topic. The goal is an objective synthesis that reports what each study found and where findings relate to each other — not an editorial narrative or a list of summaries.

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
- Questions asked
- Methods used (species, preparation, stimuli)
- Results (effect sizes, sample sizes, specific numbers)
- Inferences *as stated by the authors* (not your own interpretation)
- Subject/preparation (note species for every finding)

### Step 3: Write the Synthesis

Create `themes/<theme-name>.md` following this structure:

```markdown
# Theme Title — Descriptive Subtitle

## Scope
State how many papers this theme draws on. Note what perspectives,
subfields, or alternative viewpoints are NOT represented in the database.
Be honest about the limited view.

## Overview
2-3 sentences framing the core question. Do not claim consensus or
state "it is now understood" — just frame the question.

## Findings by Study
Present what each study found, attributed to the authors.
Use "AuthorName et al. (Year) found/measured/concluded..."
Do not editorialize or add superlatives.

## Points of Contact Across Studies
Where findings from different papers relate to each other.
Organize by sub-question or claim, not by paper.
Always attribute: "Study A found X; Study B found Y in a different preparation."
Note:
- Where results are consistent across studies (with species/method noted)
- Where results differ or create tension
- Methodological differences that may explain discrepancies

## Key Figures
Reference figures from papers in the database (if extracted):

LastName & SeniorAuthor (Year), Fig. N — description of what it shows:
![Caption](../paper-id/paper-id-figures/figN-description.png)

## Open Questions From These Papers
Questions that arise from the papers in the database.
Do not speculate about answers — just identify the gaps.

## Suggested Papers to Add
Propose specific types of papers (or specific papers if known)
that would broaden the theme or address open questions.

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

### Objectivity Directives (MANDATORY)

You are working from a small subset of a larger literature. You must stay within the bounds of what the papers in the database actually say.

1. **Report findings, don't narrate history you haven't read.** Do not claim a paper "began the modern understanding" or was "the first to show X" unless it explicitly says so. The database is a subset of the field.
2. **Attribute claims to specific papers.** Instead of "converging evidence shows X," write "Burr et al. (1994) found X; Reppas et al. (2002) found Y in a different preparation." Every claim needs an author attached.
3. **Don't synthesize consensus that may not exist.** Avoid phrases like "it is now understood that," "the definitive evidence," or "has progressively narrowed." State what each study found and let the reader draw connections.
4. **Flag your blind spots explicitly.** State how many papers the theme draws on. Note which perspectives or subfields might be missing from the database. Include a Scope section at the top of every theme.
5. **Distinguish a paper's own claims from your inferences.** If a paper concludes "the LGN is the most likely site," write "the authors concluded that..." Don't elevate it to established fact.
6. **Avoid superlatives and certainty language.** Do not use "definitive," "critical," "striking," "the most parsimonious," "key," "crucial," or similar editorializing. Describe what was measured and found.
7. **Mention limitations only when they bear on interpretation.** Don't catalog every caveat for every paper. Only note limitations when they affect whether a specific claim in the synthesis actually holds.
8. **Suggest follow-up papers after the theme.** End with a section proposing papers that could broaden the theme or address open questions, rather than speculating about answers yourself.

### General Principles

- **Be specific.** Include effect sizes, sample sizes, species, and methodological details where they matter.
- **Note species/model differences.** A finding in macaque is not the same as a finding in cat or human — state which species each result comes from.
- **Reference key figures** from papers in the database when available.
- **Organize by finding, not by paper** when drawing connections across studies. But attribute each finding to its source.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Editorializing beyond the papers | Attribute every claim to a specific paper; use "the authors concluded" not "this shows" |
| Claiming historical firsts | Don't say "first to show X" unless the paper itself says so — you haven't read the whole literature |
| Synthesizing consensus from a small database | State what N papers found; don't generalize to "the field" |
| Superlatives and certainty language | Replace "definitive," "striking," "key" with neutral descriptions |
| Missing scope statement | Always include a Scope section noting how many papers and what perspectives are absent |
| Cataloging every limitation | Only mention limitations when they affect interpretation of a specific claim |
| No follow-up suggestions | End with suggested papers to broaden the theme |
| Forgetting to update theme tags | Run update_index.py for all papers in the theme |
| Static document | Update when new papers are added to the theme |
