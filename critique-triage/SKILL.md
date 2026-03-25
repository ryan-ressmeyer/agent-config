---
name: critique-triage
description: Use when synthesizing and prioritizing critiques from multiple section reviews, when planning manuscript revisions from collected feedback, or when deciding which issues to address first after a round of critique
---

# Critique Triage

## Overview

Synthesize critiques from multiple `section-critique` outputs (or any structured critique files) into a deduplicated, prioritized revision plan. Identifies patterns across sections, flags issues that escalate to structural problems, and presents a ranked list of revision priorities for the user to approve.

## When to Use

- After running `section-critique` on multiple sections
- When you have accumulated critique files and need to decide what to act on
- When planning a revision pass based on collected feedback
- Invoked by `manuscript-review` after the line editing critique phase

## Workflow

### Step 1: Locate critique files

By default, consume all `critique-*.md` files in the current `reviews/YYYY-MM-DD/` directory. If the user wants to filter (e.g., only triage critiques from specific sections), ask which files to include.

### Step 2: Read and parse all critiques

Read each critique file. Extract all individual critiques with their metadata (severity, type, location, section).

### Step 3: Deduplicate

Identify critiques across different sections that describe the same underlying issue. For example:
- Section A and Section C both note that a key term is used inconsistently
- Multiple sections flag that a particular citation doesn't support the claim made

Group duplicates and note which sections they appear in — recurrence across sections increases the issue's priority.

### Step 4: Cluster by theme

Group related (but not duplicate) critiques into thematic clusters:
- All critiques about evidentiary support
- All critiques about internal consistency
- All critiques about unstated assumptions
- All critiques about a specific claim or finding

### Step 5: Identify structural escalations

Some line-level critiques, when viewed together, reveal structural problems:
- Multiple sections making the same logical leap suggests a missing section
- Contradictions between sections suggest a structural reorganization is needed
- A cluster of "unsupported claim" critiques in the same area suggests a gap in the argument

Flag these explicitly as **structural escalations** when a structural change would be the most parsimonious way to resolve multiple severe line-level critiques at once. The threshold is not a specific count — it's about whether reorganization, addition, or removal of a section would resolve the issues more cleanly than addressing each critique individually.

### Step 6: Rank and prioritize

Rank all issues (deduplicated, clustered, and escalated) by:
1. **Structural escalations** — highest priority, address before line edits
2. **Major severity issues** — especially those appearing in multiple sections
3. **Moderate severity** — especially thematic clusters
4. **Minor severity** — individual minor issues

### Step 7: Present revision plan

Present the prioritized list to the user as a revision plan. For each item:
- What the issue is
- Where it appears (sections, line numbers)
- Whether it's a structural escalation or a line-level issue
- Suggested direction for revision (not specific edits)

### Step 8: Save output

Save to `reviews/YYYY-MM-DD/triage.md`.

**Output format:**
```markdown
# Critique Triage

Generated: YYYY-MM-DD
Sources: [list of critique files consumed]

## Structural Escalations

### 1. [Issue title]
- **Sections affected:** [list]
- **Underlying problem:** [description]
- **Direction:** [suggestion]

## Major Issues

### 1. [Issue title]
- **Severity:** major
- **Sections:** [where it appears]
- **Critique summary:** [consolidated description]
- **Direction:** [suggestion]

## Moderate Issues
...

## Minor Issues
...

## Statistics
- Total critiques processed: N
- Duplicates removed: N
- Structural escalations: N
- Major: N | Moderate: N | Minor: N
```

## Rules

1. **Consume all critique files by default.** Only filter when the user explicitly asks.
2. **Deduplicate aggressively.** The same issue flagged in multiple sections should appear once with all locations noted.
3. **Escalate when warranted.** Patterns of line-level issues that indicate structural problems must be flagged — this is the triage's highest-value output.
4. **Direction, not prescription.** Like the critique skills, suggest directions for revision, not specific rewrites.
5. **Always save output.** Persist to `reviews/` even when invoked standalone.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Listing all critiques without deduplication | The whole point is synthesis — merge duplicates |
| Missing structural escalations | Look for patterns across sections, not just within them |
| Ranking by count instead of impact | A single major issue outranks ten minor ones |
| Proposing specific edits | Stay at the direction level — the user and orchestrator handle editing |
| Ignoring cross-section contradictions | These are the most valuable finds — always flag them |
