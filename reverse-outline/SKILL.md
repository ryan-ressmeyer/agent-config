---
name: reverse-outline
description: Use when assessing the structural integrity of a manuscript or long-form document, when checking whether a paper's argument flows logically, or when preparing for structural revision
---

# Reverse Outline

## Overview

Compress a manuscript into a flat list of core claims to expose its logical skeleton. Each bullet captures the single essential claim of a section or paragraph in 1-2 sentences. The resulting outline is then critiqued for gaps, redundancies, logical leaps, and missing transitions.

## When to Use

- Checking whether a paper's argument flows logically end-to-end
- Preparing for structural revision before line editing
- Evaluating whether sections are in the right order
- Identifying redundant or missing sections
- Invoked by `manuscript-review` during the structural stage

## Workflow

### Step 1: Identify the manuscript

Ask the user to point to the document. Read the full document.

### Step 2: Generate the reverse outline

For each major unit of the document (generally at the section or subsection level), extract the single core claim in 1-2 sentences. Output as a flat bullet list — do NOT preserve the document's section hierarchy. The flat structure makes logical flow (or breaks in it) immediately visible.

**Format:**
```
- [Claim from first unit]
- [Claim from second unit]
- [Claim from third unit]
- ...
```

Present the reverse outline to the user before proceeding to critique.

### Step 3: Critique the skeleton

Read the flat outline as a standalone argument. This is a heavy synthesis task: you must hold the entire argument in mind and evaluate its architecture. **Focus exclusively on structural issues** — problems that require moving, cutting, adding, or reorganizing sections. Do NOT report minor issues (typos, grammar, formatting, citation errors, word choice). Those belong to copy editing and line editing stages. Reporting them here wastes cognitive effort that should go toward deep structural analysis and muddies the value of the review.

Evaluate:

1. **Logical flow:** Does each claim follow from the previous? Are there leaps where intermediate reasoning is missing?
2. **Gaps:** Are there claims that need to be made but aren't present? Places where the reader would ask "but what about...?"
3. **Redundancies:** Are any two bullets making essentially the same claim? Could they be merged or is one unnecessary?
4. **Ordering:** Would rearranging any bullets strengthen the argument's progression?
5. **Balance:** Are some parts of the argument developed in far more detail than others? Is that imbalance intentional or a sign of structural weakness?
6. **Delayed payoff:** Does the text promise something (a claim, a punchline, an explanation) and then delay delivery? Delayed gratification is acceptable *if* the intervening material maintains tension toward the payoff — the reader should feel the pieces coming together, see how the setup connects to what was promised. It is NOT acceptable to insert a tangential argument between the promise and the payout. The test: does the intervening material make the reader want the payoff *more*, or does it make them forget what was promised?

Output the critique as a structured list of issues, each with:
- **Location:** Which bullet(s) are involved
- **Severity:** major | moderate (no minor — if it's minor, it's not structural)
- **Type:** gap | redundancy | logical-leap | ordering | balance | delayed-payoff
- **Issue:** What the problem is

### Step 4: Save output

Save the reverse outline and its critique to `reviews/YYYY-MM-DD/reverse-outline.md` alongside the manuscript. Create the `reviews/YYYY-MM-DD/` directory if it doesn't exist. Use today's date. If a file with that name already exists (e.g., after structural edits and re-evaluation), version it (`-v2`, `-v3`, etc.).

**Output format:**
```markdown
# Reverse Outline — [Document Name]

Generated: YYYY-MM-DD

## Outline

- [Claim 1]
- [Claim 2]
- ...

## Structural Critique

### 1. [Issue title]
- **Location:** Bullets N-M
- **Severity:** [major | moderate | minor]
- **Type:** [gap | redundancy | logical-leap | ordering | balance]
- **Issue:** [Description]

### 2. ...
```

### Step 5: Present to user

Present the critique to the user. Ask whether any issues warrant structural revision before moving to line editing.

## Rules

1. **Flat list only.** Do not reproduce the document's hierarchy. The point is to see the argument stripped of its structure.
2. **One claim per bullet.** If a section makes multiple claims, it gets multiple bullets.
3. **Claims, not summaries.** Each bullet states what the text *argues*, not what it *discusses*. "Orientation tuning sharpens over 100ms post-stimulus" not "This section discusses temporal dynamics of orientation tuning."
4. **Critique, don't fix.** Identify issues. Do not propose directions for revision or specific rewrites — that is the orchestrator's and user's job.
5. **Always save output.** Even when invoked standalone, persist to `reviews/`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Preserving document hierarchy in outline | Flatten to single-level list — hierarchy obscures logical leaps |
| Writing summaries instead of claims | Extract the argument, not the topic |
| Skipping critique and just presenting outline | The critique IS the value — outline alone is just compression |
| Proposing fixes or directions for revision | Identify the issue only — revision planning is the user's and orchestrator's job |
| Reporting typos, grammar, or formatting issues | These are copy/line-editing concerns — structural review must ignore them entirely |
