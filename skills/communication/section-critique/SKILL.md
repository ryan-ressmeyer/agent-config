---
name: section-critique
description: Use when critically reviewing a specific section or text range of a manuscript, when performing adversarial analysis of a document's arguments, or when evaluating internal consistency and evidentiary support of scientific writing
---

# Section Critique

## Overview

Perform a thorough multi-level critique of a specific section of a manuscript. Reads the full document for context, then focuses on the target section at two levels: **internal critique** (consistency, logic, and prose quality within the text's own framework) and **external critique** (questioning premises, assertions, and evidence against outside knowledge). Outputs a brief assessment of the section's merits, a summary of issues found, and a tagged list of specific critiques.

This approach is inspired by Peter Elbow's "believing and doubting game" — the insight that rigorous critique requires both accepting a text's premises to test internal coherence *and* questioning those premises from outside the text. However, this skill operationalizes that insight as two concrete analytical levels rather than two rhetorical stances, because the believing/doubting framing can collapse into a positivity/negativity distinction that misses the point.

## When to Use

- Deep review of a specific section of a manuscript
- Evaluating whether a section's arguments hold up under scrutiny
- Identifying weaknesses before peer review
- Invoked by `manuscript-review` during the line editing stage

## Workflow

### Step 1: Identify the document and section

If the document and text range are not already known from context (e.g., when dispatched as a subagent with a specific range), prompt the user to point to:
1. The document (file path)
2. The text range to critique (line numbers, section heading, or other identifier)

### Step 2: Read full document for context

Read the entire document to understand:
- The overall argument and thesis
- How the target section fits into the larger structure
- What claims are made elsewhere that the target section depends on or supports

### Step 3: Re-read the target section

Re-read just the target section closely. Note specific claims, evidence cited, logical steps, and conclusions drawn.

### Step 4: Internal critique

Grant the text's premises and evaluate the section on its own terms:

**Logical consistency:**
- Do conclusions follow from the stated premises?
- Are there contradictions within the section or with other parts of the document?
- Does the reasoning contain logical fallacies (even granting the premises)?
- Are there claims made without any supporting argument, even internally?

**Prose and communication:**
- Is the writing clear and precise? Are key terms used consistently?
- Does the section's structure serve its argument?
- Are there sentences that are ambiguous, awkward, or obscure the intended meaning?
- Does the prose flow, or are there jarring transitions or missing connectives?

Tag each critique with severity (`major` | `moderate` | `minor`) and type (`consistency` | `logic` | `unsupported-claim` | `contradiction` | `clarity` | `structure` | `precision`). Include line numbers for each critique when available.

### Step 5: External critique

Now step outside the text's framework and question the assertions themselves:

- Is the evidence sufficient to support the claims? What alternative explanations exist?
- Are citations used accurately — does the cited work actually support what is claimed?
- Are there unstated assumptions that the argument depends on?
- Would a skeptical reviewer find the reasoning convincing?
- Are there known counterarguments or alternative interpretations not addressed?
- Does the section overstate or understate what the evidence supports?

Tag each critique with severity (`major` | `moderate` | `minor`) and type (`evidence` | `assumption` | `alternative-explanation` | `citation-accuracy` | `counterargument` | `overstatement`). Include line numbers for each critique when available.

### Step 6: Save output

Save to `reviews/YYYY-MM-DD/critique-{section-name}.md` alongside the manuscript. If a file with that name already exists, version it (`-v2`, `-v3`, etc.).

**Output format:**
```markdown
# Section Critique: [Section Name]

Generated: YYYY-MM-DD
Document: [file path]
Range: [line numbers or section identifier]

## Merits

[One brief paragraph identifying the section's strengths — what is working well and should be preserved. This is not praise for its own sake; it is a guide for revision so the author knows what not to break.]

## Summary of Issues

[One brief paragraph summarizing the key problems found across both levels of critique. Give the author a high-level picture before the detailed list.]

## Internal Critique

### 1. [Short issue title]
- **Severity:** [major | moderate | minor]
- **Type:** [consistency | logic | unsupported-claim | contradiction | clarity | structure | precision]
- **Location:** [line numbers or paragraph reference]
- **Critique:** [What the issue is and why it matters within the text's own framework]

### 2. ...

## External Critique

### 1. [Short issue title]
- **Severity:** [major | moderate | minor]
- **Type:** [evidence | assumption | alternative-explanation | citation-accuracy | counterargument | overstatement]
- **Location:** [line numbers or paragraph reference]
- **Critique:** [What the issue is and why a skeptical reader would flag it]

### 2. ...
```

## Rules

1. **Read the whole document first.** Section-level critiques without document-level context miss cross-references, contradictions with other sections, and argument dependencies.
2. **Separate the levels.** Do not mix internal and external critiques. The separation forces different modes of analysis — evaluating coherence within the text's own frame vs. questioning the frame itself.
3. **Start with merits, then summarize issues.** The merits paragraph identifies what to preserve during revision. The summary paragraph gives the author the big picture before the detailed list.
4. **Be thorough.** The goal is to surface all potential issues. Downstream triage handles prioritization — this skill's job is completeness.
5. **Critique, don't fix.** State what the problem is and why it matters. Do not propose rewrites or solutions.
6. **Tag everything.** Every critique gets severity and type tags. These are essential for downstream triage.
7. **Line numbers when available.** Always reference specific locations in the text.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping the full-document read | Always read the whole document first — context matters |
| Mixing internal and external critiques | Keep levels separate — they require different analytical frames |
| Turning the merits paragraph into generic praise | Be specific about what works and why — this guides what to preserve |
| Treating internal critique as "positivity pass" | Internal critique is rigorous — it finds contradictions, logical gaps, and unclear writing *within* the text's own terms |
| Proposing fixes instead of critiques | State the issue, not the solution — editing happens later |
| Being vague about location | Reference specific lines, paragraphs, or sentences |
| Softening critiques to be "nice" | Thoroughness serves the author — honest critique improves the work |
| Skipping minor issues | Log everything — triage decides what matters, not critique |

## Special Section Types

When the target is a figure, table, or abstract, adjust the critique focus:

### Figures and Tables

- Does the caption adequately explain every part of each panel (axes, labels, symbols, color codes)?
- Is every figure panel referenced in the text?
- Does the text's description of the figure match what the figure actually shows?
- Are statistical annotations (significance markers, error bars) explained?
- Could a reader understand the figure from the caption alone, without reading the main text?

### Abstract

- Does the abstract succinctly summarize the key points of the paper?
- Does it explain the paper's value to a reader — why should they keep reading?
- The abstract is the first point of contact; it should present the paper in the manner most likely to engage the reader.
- Is the language precise? No overselling, no vague claims, no hedged superlatives.
- Do the abstract's claims match the paper's actual findings and conclusions?
