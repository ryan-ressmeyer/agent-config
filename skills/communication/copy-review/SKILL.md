---
name: copy-review
description: Use when checking a manuscript for grammar, punctuation, terminology consistency, and stylistic issues, or when performing a final polish pass before submission
---

# Copy Review

## Overview

Perform a copy-level review of a manuscript, checking for grammar, syntax, punctuation, terminology consistency, and stylistic issues. Activates the `style-guide` skill for stylistic compliance. Operates at the paragraph level, dispatching subagents for parallel review when the document is large.

## When to Use

- Final polish pass before submission
- Checking grammar and punctuation after substantive edits
- Ensuring terminology consistency across a document
- Invoked by `manuscript-review` during the copy editing stage

## Workflow

### Step 1: Identify the manuscript

Ask the user to point to the document. Read the full document.

### Step 2: Activate style guide

**REQUIRED SUB-SKILL:** Use `style-guide` to establish voice standards and the blacklist for this review.

### Step 3: Divide into review units and dispatch subagents

Divide the document into paragraph-level review units. If the document would produce more than 10 review units, batch adjacent paragraphs into larger chunks (aim for 5-10 chunks).

Dispatch a subagent for each review unit. Each subagent receives its chunk plus the full-document terminology list (built in this step by scanning the whole document for term variants before dispatching). The terminology scan must happen at the document level before dispatch so that each subagent can flag inconsistencies against the canonical list.

### Step 4: Review each unit

Each subagent checks:

1. **Grammar and syntax:** Subject-verb agreement, tense consistency, sentence fragments, run-on sentences, dangling modifiers.
2. **Punctuation:** Comma usage, semicolons, colons, quotation marks, hyphens vs. em-dashes.
3. **Terminology consistency:** Are the same concepts referred to with the same terms throughout? Flag any term that appears in multiple forms (e.g., "receptive field" vs. "RF" without prior definition of the abbreviation).
4. **Style guide compliance:** Apply the `style-guide` blacklist and voice principles. Flag any violations.
5. **Reference formatting:** Are citations, figure references, and cross-references formatted consistently?
6. **Line numbers:** Reference specific line numbers when available.

### Step 5: Compile results

Collect all subagent results into a single output document. For each issue:
- **Location:** Line number or paragraph reference
- **Type:** grammar | punctuation | terminology | style | reference-format
- **Issue:** What the problem is
- **Suggestion:** Specific fix (unlike critique skills, copy-level issues have clear right answers)

### Step 6: Present to user

Present the compiled results to the user. Walk through issues by type (terminology consistency first, since it affects the whole document, then grammar/punctuation/style by location).

### Step 7: Save output

Save to `reviews/YYYY-MM-DD/copy-review.md`.

**Output format:**
```markdown
# Copy Review

Generated: YYYY-MM-DD
Document: [file path]
Style guide: applied

## Issues

### 1. [Short description]
- **Location:** [line/paragraph]
- **Type:** [grammar | punctuation | terminology | style | reference-format]
- **Issue:** [description]
- **Suggestion:** [specific fix]

### 2. ...

## Terminology Consistency Report

| Term | Variants Found | Recommended |
|------|---------------|-------------|
| [term] | [variant1, variant2] | [recommended form] |

## Statistics
- Total issues: N
- Grammar: N | Punctuation: N | Terminology: N | Style: N | Reference: N
```

## Rules

1. **Always activate `style-guide`.** Copy review without the style guide is incomplete.
2. **Suggest specific fixes.** Unlike structural and line critique, copy issues have determinate solutions.
3. **Flag terminology inconsistency across the whole document.** This requires document-level awareness, not just paragraph-level.
4. **Don't re-litigate content.** Copy review is about form, not substance. If a claim is wrong, that's a `section-critique` issue, not a copy issue.
5. **Always save output.** Persist to `reviews/`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Critiquing content instead of form | Copy review is grammar/style only — substance belongs to section-critique |
| Skipping style-guide activation | Always activate — it defines what "correct" style means |
| Missing cross-document terminology inconsistency | Build the terminology table from the whole document, not section by section |
| Not providing specific fixes | Copy issues have clear solutions — provide them |
