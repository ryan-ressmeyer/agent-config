---
name: paper-summarize
description: Use when a paper PDF needs to be read and summarized using the QLMRI framework (Questions, Logic, Methods, Results, Inferences), or when adding a new paper's summary to the literature database
---

# Paper Summarize

## Overview

Read a paper PDF and produce a structured QLMRI summary, then update the literature database (`index.yaml`, `references.bib`). This is always an interactive, one-paper-at-a-time process — the user should be learning alongside the agent.

## When to Use

- User has a PDF in the database that needs summarizing
- User has just added a paper via `pdf-retrieve` and wants to process it
- User wants to re-summarize or update an existing summary
- A paper folder exists with a PDF but no summary file

## Database Context

**Database location:** `references/` by default, overridable via CLAUDE.md or user input.

**Paper folder structure:**
```
references/<id>/
├── <id>.pdf
├── <id>-summary.md          # ← this skill creates/updates this
├── <id>-figures/             # ← extracted key figures (optional)
│   ├── fig2-description.png
│   └── fig4-description.png
├── references.yaml
├── cited-by.yaml
└── related.yaml
```

## Workflow

### Step 1: Read the PDF

Use Claude's native PDF reading. For papers >10 pages, read in page ranges:
```
Read pages 1-10, then 11-20, etc.
```

Focus on: Abstract, Introduction, Methods, Results, Discussion, Figures.

### Step 2: Write QLMRI Summary

Create `<id>-summary.md` following this template exactly:

```markdown
# LastName & SeniorAuthor (Year) — Short Title

## Citation
Full citation in APA-ish format with DOI.

## Subject / Preparation
Species (genus species if known), preparation details.
For computational work: "Computational model" or "Simulation" with framework details.
If multiple subjects: list all.

## Questions
- What specific questions does this paper address?
- Frame as the authors frame them

## Logic
- What is the reasoning structure / hypothesis?
- What predictions follow from the hypothesis?
- What would falsify it?

## Methods
- Key experimental/computational methods
- Sample sizes, statistical approaches
- Stimulus parameters, recording methods, model architecture — whatever is central

## Results
- Key findings with effect sizes and statistics where reported
- Distinguish primary findings from secondary/exploratory
- Note figure numbers for key results

## Inferences
- What do the authors conclude?
- Are the conclusions supported by the data?
- Note any overclaims or caveats the authors acknowledge

## Key Figures
Embed extracted figures if available, or reference by number:
![Caption](relative-path-to-figure.png)
```

### Step 3: Extract Key Figures (if possible)

Identify the 2-4 most important figures. If figure extraction is feasible:
- Save to `<id>-figures/` directory
- Name descriptively: `fig2-tuning-curves.png`
- Embed in the summary with captions

If extraction is not feasible, note figure numbers and captions in the summary text.

### Step 4: Update index.yaml

Add or update the paper's entry. Use `uv run ~/.claude/skills/paper-summarize/scripts/update_index.py` to safely merge the new entry:

```bash
uv run ~/.claude/skills/paper-summarize/scripts/update_index.py \
  --database references/ \
  --id smith-jones-2019 \
  --title "Paper title" \
  --authors '["Smith, A.B.", "Jones, E.F."]' \
  --year 2019 \
  --journal "Journal Name" \
  --doi "10.xxx/yyy" \
  --subject '["macaque"]' \
  --summary "1-3 sentence summary" \
  --status summarized \
  --has-pdf true \
  --has-summary true
```

### Step 5: Update references.bib

Add/update the BibTeX entry. Use `uv run ~/.claude/skills/paper-summarize/scripts/update_bibtex.py`:

```bash
uv run ~/.claude/skills/paper-summarize/scripts/update_bibtex.py \
  --database references/ \
  --id smith-jones-2019 \
  --entry '@article{smith-jones-2019, author = {...}, ...}'
```

### Step 6: Present and Discuss

Present the summary to the user. Ask:
- "Does this accurately capture the paper? Anything to correct or add?"
- Suggest theme tags for confirmation
- Suggest `status` level (default: `summarized`, offer `key-paper` if warranted)

### Step 7: Surface Next Papers

After the summary is reviewed, check the paper's citation graph files:
- `references.yaml` — papers it cites not yet in database
- `cited-by.yaml` — papers citing it not yet in database
- `related.yaml` — semantically related papers not yet in database

Present the most relevant candidates:
> "This paper cites N papers not yet in your database. Most relevant:
> - [Title] (Year) — [brief reason]
>
> It's cited by M papers. Most relevant:
> - [Title] (Year) — [brief reason]
>
> I also found K related papers. Most relevant:
> - [Title] (Year) — [relevance note]
>
> Would you like to add any of these next?"

## Rigor Requirements

- **Distinguish claims from evidence.** "Authors claim X" vs "Data show Y" when they diverge.
- **Note sample sizes.** N animals, n neurons/trials/subjects.
- **Report statistics.** p-values, effect sizes, confidence intervals when available.
- **Flag concerns.** Small N, missing controls, overclaims, circular analyses.
- **Capture subject details.** Species, strain, age, sex, preparation — whatever is relevant.
- **For computational papers:** Note model assumptions, parameter choices, validation approach.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Summarizing abstract instead of reading full paper | Read all sections — results often differ from abstract framing |
| Missing subject/preparation details | Always check Methods for species, strain, preparation |
| Accepting author conclusions uncritically | Compare Results to Inferences — note any gaps |
| Skipping statistics | Include p-values, N, effect sizes where reported |
| Adding theme tags to index entries | Themes are tracked in `themes/*.md` documents, not on paper entries |
| Forgetting to surface next papers | Always check citation graph after summary review |
