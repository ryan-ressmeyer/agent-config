# Research System — Design Document

## Goal

Support the full arc of scientific research: from reading papers, through planning analyses and manuscripts, to writing publication-ready prose.

Build a **paper database** incrementally through interactive conversations. Use that database — alongside the project's codebase and experimental data — to plan high-impact manuscripts through collaborative dialogue. Then write the prose with proper citations.

The system is **not** an automation tool — it is a guided process. The agent speeds up and organizes the work, but the user drives the pace, reads every paper, verifies every interpretation, and makes every strategic decision.

## Three Phases

```
Phase 1: Literature Review          Phase 2: Manuscript Planning         Phase 3: Writing
─────────────────────────           ────────────────────────────         ──────────────────
Build the paper database            Plan the paper from data +           Write prose with
one paper at a time                 literature, run analyses,            citations from
                                    iterate on framing                   the database

literature-review (orchestrator)    manuscript-planning                  literature-writer
├── citation-fetch                  ├── database-search                  ├── database-search
├── pdf-retrieve                    ├── literature-review*               └── (reads database
├── paper-summarize                 ├── theme-synthesize                     directly)
├── database-check                  └── [code tools]
├── database-search
└── theme-synthesize                * hands back when gaps found
```

Phases are not strictly sequential — users move between them as needed. A manuscript plan may reveal literature gaps that send you back to Phase 1. Writing may surface a missing analysis that sends you back to Phase 2.

---

## Database Structure

The database lives at `references/` by default (overridable via `CLAUDE.md` or user input). It can be a standalone directory or a subfolder within a larger project.

```
references/
├── index.yaml                          # top-level metadata for all papers
├── references.bib                      # BibTeX entries for all papers
├── themes/
│   ├── temporal-coding.md              # cross-paper thematic synthesis
│   ├── receptive-field-models.md
│   └── ...
├── smith-jones-2019/
│   ├── smith-jones-2019.pdf            # paper PDF
│   ├── smith-jones-2019-summary.md     # QLMRI summary
│   ├── smith-jones-2019-figures/       # extracted key figures (optional)
│   │   ├── fig2-tuning-curves.png
│   │   └── fig4-model-comparison.png
│   ├── cited-by.yaml                   # papers that cite this one
│   ├── references.yaml                 # papers this one cites
│   └── related.yaml                    # semantically related papers (via search)
├── lee-park-2021/
│   ├── lee-park-2021.pdf
│   └── lee-park-2021-summary.md
└── ...
```

### Naming Convention

Folder and file names: `firstauthor-seniorauthor-year` (all lowercase, hyphens). If only one author, use `author-year`. If year collides, append a letter: `smith-jones-2019b`.

### `index.yaml`

Top-level metadata file. Each entry:

```yaml
papers:
  - id: smith-jones-2019
    title: "Temporal dynamics of V1 orientation selectivity"
    authors: ["Smith, A.B.", "Doe, C.D.", "Jones, E.F."]
    year: 2019
    journal: "Journal of Neuroscience"
    doi: "10.1523/JNEUROSCI.1234-19.2019"
    pmid: "31234567"
    subject:
      - "macaque"
    summary: "Measured V1 orientation tuning dynamics using chronically implanted arrays; found sharpening over 50-150ms consistent with recurrent models."
    key_figures:
      - file: "fig2-tuning-curves.png"
        caption: "Orientation tuning curves sharpen between 50-150ms post-stimulus"
      - file: "fig4-model-comparison.png"
        caption: "Recurrent model (R²=0.94) fits temporal dynamics better than feedforward (R²=0.61)"
    status: "summarized"  # to-read | read | summarized | key-paper
    has_pdf: true
    has_summary: true
    date_added: 2026-03-05
```

**`subject` field:** The species or model organism studied. This is NOT for topic keywords — themes are tracked in `themes/*.md` synthesis documents, not on individual paper entries. It is a list because some papers study multiple species. Controlled vocabulary:
- Species: `macaque`, `mouse`, `human`, `cat`, `ferret`, `marmoset`, `rat`, `zebrafish`
- Non-animal: `computational-model` (pure modeling with no animal data), `theoretical` (analytical/mathematical only)
- Examples: `["macaque"]` for a macaque electrophysiology paper, `["macaque", "computational-model"]` for a paper with both physiology and modeling, `["computational-model"]` for a pure simulation study

### `references.bib`

Maintained alongside `index.yaml`. Every paper in the database gets a BibTeX entry with citation key matching the paper `id`:

```bibtex
@article{smith-jones-2019,
  author  = {Smith, A.B. and Doe, C.D. and Jones, E.F.},
  title   = {Temporal dynamics of {V1} orientation selectivity},
  journal = {Journal of Neuroscience},
  year    = {2019},
  volume  = {39},
  number  = {12},
  pages   = {2345--2358},
  doi     = {10.1523/JNEUROSCI.1234-19.2019}
}
```

### QLMRI Summary (`*-summary.md`)

```markdown
# Smith & Jones (2019) — Temporal dynamics of V1 orientation selectivity

## Citation
Smith, A.B., Doe, C.D., & Jones, E.F. (2019). Temporal dynamics of V1
orientation selectivity. *Journal of Neuroscience*, 39(12), 2345-2358.
DOI: 10.1523/JNEUROSCI.1234-19.2019

## Subject / Preparation
Macaque (Macaca mulatta), chronically implanted Utah arrays in V1

## Questions
- How does orientation selectivity in V1 evolve over time within a single trial?
- Is the temporal sharpening of tuning consistent with feedforward or recurrent models?

## Logic
- If tuning sharpens beyond what a feedforward model predicts, recurrent
  amplification must contribute.
- Compared observed tuning dynamics to feedforward (Hubel-Wiesel) and
  recurrent (ring model) predictions.

## Methods
- 96-channel Utah arrays in V1 of 2 macaques
- Drifting gratings, 12 orientations, 200ms presentation
- Population decoding (SVM) at 10ms time bins
- Compared to feedforward and recurrent computational models

## Results
- Orientation selectivity emerged at 40ms, peaked at 80ms
- Tuning bandwidth narrowed 30% between 50-150ms (p < 0.001)
- Temporal profile matched recurrent model predictions (R² = 0.94)
  better than feedforward (R² = 0.61)
- Effect consistent across both animals

## Inferences
- Recurrent processing sharpens V1 orientation tuning over time
- Feedforward models alone cannot account for observed dynamics
- Temporal window of 50-150ms is the critical period for recurrent refinement

## Key Figures
![Orientation tuning curves sharpen between 50-150ms](smith-jones-2019-figures/fig2-tuning-curves.png)

![Recurrent model fits temporal dynamics better than feedforward](smith-jones-2019-figures/fig4-model-comparison.png)
```

### Related Papers Files (`cited-by.yaml`, `references.yaml`, `related.yaml`)

Each paper folder contains files tracking its citation neighborhood and semantically related work:

```yaml
# references.yaml — papers this paper cites (that we care about)
references:
  - id: hubel-wiesel-1962          # in our database
    doi: "10.1113/jphysiol.1962.sp006837"
    in_database: true
  - id: ringach-shapley-1997
    doi: "10.1038/387281a0"
    in_database: true
  - title: "Some paper we haven't added yet"
    doi: "10.1234/not-yet-added"
    in_database: false              # candidate for addition

# cited-by.yaml — papers that cite this paper
cited_by:
  - id: chen-williams-2022
    doi: "10.1016/j.neuron.2022.01.015"
    in_database: true
  - title: "Another citing paper"
    doi: "10.1234/citing-paper"
    in_database: false

# related.yaml — semantically related papers found via search
# Discovered by searching Semantic Scholar / Google Scholar using
# the paper's key terms and checking abstracts for relevance.
# These are NOT in the citation graph — they address similar questions
# or use similar methods but may not cite each other.
related:
  - title: "Population coding of orientation in mouse V1"
    doi: "10.1234/related-paper"
    source: "semantic-scholar-recommended"  # or "scholar-search", "pubmed-search"
    relevance: "Similar methods (population decoding of orientation) but in mouse instead of macaque"
    in_database: false
  - title: "Recurrent circuits in primate visual cortex"
    doi: "10.1234/another-related"
    source: "scholar-search"
    relevance: "Reviews recurrent models relevant to this paper's theoretical framework"
    in_database: false
```

These files serve as a **discovery engine**. Three sources of related work:
1. **References** — backward citations (what this paper builds on)
2. **Cited-by** — forward citations (what built on this paper)
3. **Related** — semantically similar papers found via search + abstract screening (may not cite each other at all, but address overlapping questions or methods)

Papers marked `in_database: false` are candidates the agent should surface to the user after reviewing a paper.

### Theme Documents (`themes/*.md`)

Cross-paper syntheses that trace how ideas evolved:

```markdown
# Orientation Selectivity — Temporal Dynamics

## Overview
How does orientation selectivity emerge and evolve within a trial?
This thread traces the shift from static feedforward models toward
dynamic recurrent accounts.

## Historical Arc
1. **Hubel & Wiesel (1962)** established feedforward model...
2. **Ringach et al. (1997)** first showed dynamic tuning changes...
3. **Smith & Jones (2019)** provided strongest recurrent evidence...

## Key Findings Across Papers
- ...

## Key Figures

Smith & Jones (2019), Fig. 2 — best illustration of temporal sharpening:
![Tuning curve dynamics](../smith-jones-2019/smith-jones-2019-figures/fig2-tuning-curves.png)

## Open Questions
- ...

## Papers in This Theme
- hubel-wiesel-1962
- ringach-shapley-1997
- smith-jones-2019
```

---

## Phase 1 Sub-Skills: Literature Review

### 1. `citation-fetch`

**Purpose:** Given a paper identifier (DOI, PMID, title, or search query), retrieve full citation metadata and citation graph.

**Inputs:** DOI, PMID, arXiv ID, title string, or search query
**Outputs:** Structured metadata (authors, title, journal, year, DOI, PMID, abstract), BibTeX entry, lists of citing/cited papers

**Behavior:**
- Query CrossRef, PubMed, Semantic Scholar APIs
- Return structured metadata
- Generate the `index.yaml` entry fields
- Generate the BibTeX entry for `references.bib`
- Generate the citation block for the summary document
- Retrieve the citation graph and related work:
  - Papers this paper cites (via Semantic Scholar references endpoint) → `references.yaml`
  - Papers that cite this paper (via Semantic Scholar citations endpoint) → `cited-by.yaml`
  - Semantically related papers (via Semantic Scholar recommendations, Google Scholar / PubMed searches using key terms from title/abstract, with quick abstract checks for relevance) → `related.yaml`
  - Cross-reference all three lists against existing database entries (mark `in_database: true/false`)
- If multiple results found from a search query, present options to the user

**Relation to existing:** Replaces/refocuses the existing `citation-management` skill. Strips out the BibTeX-heavy workflow and focuses on metadata retrieval + citation graph for the database.

---

### 2. `pdf-retrieve`

**Purpose:** Obtain the PDF for a paper and place it in the database.

**Inputs:** DOI, PMID, or URL; target path in database
**Outputs:** PDF saved to `references/<id>/<id>.pdf`

**Behavior:**
1. Try open-access sources first:
   - Unpaywall API (free, legal open-access lookup by DOI)
   - PubMed Central (free full text)
   - arXiv / bioRxiv / medRxiv (preprint servers)
   - Semantic Scholar open-access PDF links
2. If no open-access PDF found:
   - **Ask the user** to retrieve the paper manually
   - Provide the DOI link and any known URLs
   - Tell the user the expected file path: `references/<id>/<id>.pdf`
   - Wait for user to confirm the PDF is placed
   - Verify the file exists and is readable
3. Validate the PDF is readable (not corrupted, not a login/paywall HTML page)

**Key principle:** The agent should never hit a paywall and silently fail. Always escalate to the user with clear instructions.

---

### 3. `paper-summarize`

**Purpose:** Read a paper PDF with the user and produce a QLMRI summary, then update `index.yaml` and `references.bib`.

**Inputs:** Path to PDF in database
**Outputs:** `<id>-summary.md` written; `index.yaml` entry updated; `references.bib` entry added/updated

**Behavior:**
1. Read the PDF using Claude's native PDF reading (paginated for long papers)
2. Extract structured information using QLMRI framework:
   - **Q**uestions — What questions does the paper address?
   - **L**ogic — What is the reasoning/hypothesis structure?
   - **M**ethods — What methods were used? (including subject/preparation)
   - **R**esults — What were the key findings?
   - **I**nferences — What conclusions do the authors draw?
3. Identify key figures and extract them if possible (see Key Figures section)
4. Write the summary document following the template above
5. Add/update the entry in `index.yaml` with:
   - Citation metadata (if not already present)
   - 1-3 sentence summary
   - Subject/preparation
   - Key figure references
   - Theme tags (suggest to user for confirmation)
   - Set status to `summarized`
6. Add/update the BibTeX entry in `references.bib`
7. Present summary to user for review/correction
8. **After review:** Surface candidates for next papers from all three sources:
   - "This paper cites N papers not yet in your database. Most relevant:"
   - "This paper is cited by M papers not yet in your database. Most relevant:"
   - "I also found K semantically related papers (similar questions/methods). Most relevant:"
   - Let the user choose which (if any) to add next

**Rigor requirements:**
- Distinguish between what authors claim and what the data supports
- Note sample sizes, statistical tests, and effect sizes
- Flag any methodological concerns
- Capture the specific subject and preparation details

**Key Figures:**
- Identify the 2-4 most important figures in the paper
- If figure extraction is possible (via PDF image extraction tools), save them to `<id>-figures/`
- If extraction is not possible, note the figure numbers and captions in the summary
- Embed extracted figures in the summary markdown with captions
- Record key figures in `index.yaml` entry
- Key figures can be referenced in theme documents to illustrate cross-paper points

**One paper at a time:** This skill always processes a single paper interactively. The user should be learning and engaging with each paper, not batch-processing.

---

### 4. `database-check`

**Purpose:** Verify database integrity — all expected files exist, naming is correct, index is consistent.

**Inputs:** Database path (default: `references/`)
**Outputs:** Report of issues found; optionally fix minor issues

**Checks:**
- Every folder matches `firstauthor-seniorauthor-year` pattern
- Every folder contains `<id>.pdf` and/or `<id>-summary.md`
- Every folder with files has a corresponding `index.yaml` entry
- Every `index.yaml` entry has a corresponding folder
- `has_pdf` and `has_summary` flags match actual file presence
- Papers referenced in theme documents exist in the database
- `references.bib` entries match `index.yaml` entries
- Related papers files (`cited-by.yaml`, `references.yaml`, `related.yaml`) have valid cross-references
- No orphaned files or folders
- Summary files follow the QLMRI template structure
- No duplicate entries (same DOI or same id)

**Behavior:**
- Report all issues with severity (error vs warning)
- Offer to fix auto-fixable issues (e.g., updating `has_pdf` flags, syncing `references.bib`)
- Never delete files without user confirmation

---

### 5. `database-search`

**Purpose:** Search the local paper database by metadata, content, or theme.

**Inputs:** Query string, optional filters (year range, subject, theme, author)
**Outputs:** Matching papers with their index entries and summary snippets

**Search targets:**
- `index.yaml` fields (title, authors, journal, subject, summary)
- Summary document full text
- Theme document full text
- Related papers files (find papers connected via citations or semantic similarity)

**Behavior:**
- Fuzzy matching on text fields
- Exact matching on structured fields (year, subject)
- Return results ranked by relevance
- Show brief context for each match
- Support combining filters (e.g., "macaque studies on orientation selectivity after 2015")
- Support citation graph queries (e.g., "papers that cite smith-jones-2019", "papers cited by lee-park-2021")

---

### 6. `theme-synthesize`

**Purpose:** Create or update a thematic synthesis document that traces ideas across multiple papers.

**Inputs:** Theme name, list of paper IDs
**Outputs:** `themes/<theme-name>.md` created/updated

**Behavior:**
1. Gather all papers tagged with the theme (or specified by user)
2. Read their summaries
3. Synthesize a narrative that:
   - Traces the historical arc of the idea
   - Identifies points of agreement and disagreement
   - Highlights methodological evolution
   - Notes open questions and gaps
   - References key figures from individual papers to illustrate points
4. Present draft to user for review
5. Update theme tags in `index.yaml` for any newly associated papers

**Key principle:** This is a synthesis, not a list of summaries. It should read as a coherent narrative about how understanding of a topic evolved.

---

## Phase 2: Manuscript Planning

### `manuscript-planning`

**Purpose:** Collaborative dialogue to develop a high-impact manuscript plan from data + literature.

**Inputs:** Literature database, project codebase, experiment descriptions, user's research questions
**Outputs:** Manuscript plan (user-specified format/location) + lab journal (append-only)

**Two artifacts:**

1. **Manuscript plan** — Living outline of the paper. Bullet points and short sentences, not prose. Format and location are user-specified (markdown, LaTeX, etc.). Default: `manuscript-plan.md` in project root.

2. **Lab journal** — Append-only record of everything tried: hypotheses, analyses, results, ad hoc thoughts, dead ends. Freeform entries, kept small. Links to scripts. Default: `lab-journal.md` in project root.

**Core loop:**
```
User describes data / experiments / question
  → Agent explores codebase and literature as needed
  → Agent and user collaborate on direction and analysis design
  → Agent writes and runs analysis scripts (via code tools + uv)
  → Agent presents results and proposed interpretation TO USER
  → User confirms, corrects, or redirects
  → Agent logs work in lab journal
  → Agent updates manuscript plan if warranted
  → Repeat
```

**Modes:** Discovery, analysis collaboration, outline structuring, gap identification, future experiments, resume.

**Key principles:**
- Agent always returns to user for interpretation verification
- Agent and user co-design analyses before the agent writes code
- Impact is negotiated — agent asks about target journal/audience, doesn't assume
- One question at a time during exploratory dialogue

**Interfaces with code tools:** `python-environment`, `systematic-debugging`, `test-driven-development`

**See:** `manuscript-planning/SKILL.md` for full specification.

---

## Phase 3: Writing

### `literature-writer`

**Purpose:** Use the paper database to assist writing scientific papers.

**Inputs:** Section being written (intro, discussion, etc.), topic/claim being made
**Outputs:** Drafted text with inline citations, suggested references

**Behavior:**
1. Search database for papers relevant to the section/claim
2. Load relevant summaries and theme documents
3. Draft text with proper citations drawn from the database (using BibTeX keys from `references.bib`)
4. For introductions: build narrative arc from theme documents
5. For discussions: connect findings to existing literature
6. For any section: suggest where citations should be inserted
7. Reference key figures from the database where they support the narrative
8. Flag claims that lack supporting papers in the database

**Key principle:** Only cite papers that are in the database. If a citation is needed but not in the database, tell the user and offer to add it via the literature-review workflow.

---

## Orchestrator Skills

### `literature-review` (Phase 1 Orchestrator)

**Purpose:** Interactive session for building the paper database. One paper at a time, with the user learning alongside the agent.

**Core loop:**
```
User provides topic/paper/question
  → Agent searches (citation-fetch) or processes (paper-summarize)
  → Agent updates database
  → Agent presents findings and summary for review
  → Agent surfaces candidate next papers from citation graph
  → User asks follow-up, corrects summary, or provides next paper
  → Repeat
```

**Modes of operation:**
1. **Discovery mode** — User gives a topic; agent searches for relevant papers, presents candidates, user selects which to add
2. **Processing mode** — User provides a paper (PDF, DOI, or title); agent fetches citation, retrieves PDF, writes summary, surfaces citation graph candidates
3. **Synthesis mode** — User asks about themes; agent runs theme-synthesize on relevant papers
4. **Question mode** — User asks a question; agent searches database and answers with citations
5. **Maintenance mode** — Run database-check, fill gaps, update themes

**After processing each paper, the agent should:**
- Present the QLMRI summary for review
- Ask if the user wants to correct or add anything
- Show the most relevant papers from the citation graph not yet in the database
- Ask: "Would you like to add any of these papers next, explore a theme, or move on to something else?"

**The agent should also:**
- Maintain awareness of what's already in the database
- Propose theme connections as the database grows
- Track what the user is interested in to guide discovery

---

## Full Skill Dependency Graph

```
literature-review (orchestrator)
├── citation-fetch
├── pdf-retrieve
├── paper-summarize
│   └── (surfaces citation graph → feeds back into discovery)
├── database-check
├── database-search
└── theme-synthesize

manuscript-planning
├── database-search
├── literature-review          (hand off when literature gaps found)
├── theme-synthesize
├── python-environment         (all script execution)
├── systematic-debugging       (when analyses fail)
└── test-driven-development    (when building analysis pipelines)

literature-writer
├── database-search
└── (reads database directly: index.yaml, references.bib, summaries, themes)
```

---

## Configuration

### Default Locations
- Literature database: `references/` in the current working directory
- Manuscript plan: `manuscript-plan.md` in project root
- Lab journal: `lab-journal.md` in project root

### Override via CLAUDE.md
```markdown
## Research System
Database path: /path/to/my/references
Manuscript plan: /path/to/manuscript-plan.md
Lab journal: /path/to/lab-journal.md
```

### Override via User Input
User can specify at the start of a session. The database can live as a subfolder within a larger project — the skills only care about the internal structure of the database directory itself.

---

## What Changes from Existing Skills

| Existing Skill | What Happens |
|---|---|
| `citation-management` | Replaced by `citation-fetch`. BibTeX workflow simplified; `references.bib` maintained automatically as part of database. |
| `literature-review` | Completely rewritten as the orchestrator skill. Current PRISMA/systematic-review focus replaced with interactive, one-paper-at-a-time database-building workflow. |

---

## Design Decisions

1. **`references.bib` maintained alongside `index.yaml`** — Every paper gets a BibTeX entry automatically. Useful for LaTeX writing via `literature-writer`.

2. **Native PDF reading** — `paper-summarize` uses Claude's built-in PDF reading capability (paginated for papers >10 pages). No preprocessing or text extraction step.

3. **Citation graph per paper** — Each paper folder contains `references.yaml` and `cited-by.yaml` tracking its citation neighborhood. Papers not yet in the database are marked as candidates for addition.

4. **One paper at a time** — No batch processing. The system is designed to support the user's learning process, not automate intake. The agent surfaces candidates; the user chooses the pace.

5. **`subject` as a list** — Papers often span multiple subjects (e.g., macaque electrophysiology + computational modeling). The field accepts multiple values including both animal species and computational approaches.

6. **Key figure extraction** — When possible, extract important figures from PDFs and embed them in summary and theme documents. This makes the database a visual resource, not just text.

7. **Database location is flexible** — Defaults to `references/` but can be anywhere. Supports being a subfolder in a larger project repo.

8. **Manuscript planning bridges literature and code** — `manuscript-planning` reads the literature database and interfaces with the codebase via existing code tools. It produces a living plan and an append-only lab journal that preserves institutional memory across sessions.

9. **Three-phase flow with feedback loops** — Literature review → manuscript planning → writing, but users move between phases freely. A manuscript plan may reveal literature gaps; writing may surface missing analyses.
