# Evaluation and promotion record

This maintainer-only record documents the user's explicit approval to promote
revision 04 for production use despite the evaluation limits below. It is not
runtime guidance. Detailed private development evidence remains in the separate
sandbox and is not distributed with this package.

## Development evidence

- **v1, initial two-task pilot.** The user preferred the without-skill population
  figure; the gallery comparison was a tie. No efficacy benefit was demonstrated.
- **v2, clarified-gallery development comparison.** The revised skill was
  preferred in one matched comparison. Corrections remained; this is not general
  efficacy evidence.
- **v3, public benchmark.** Three matched pairs produced six completed agent
  submissions, with fidelity checks passing. Feedback was qualitative only;
  there were no formal overall preference votes. Appearance made condition
  identities inferable, limiting blinded interpretation.
- **v4, consolidated feedback and controlled design experiments.** Qualitative
  feedback established semantic zero-baseline and legend-placement guidance.
  Direct experiments compared categorical segments and marker treatments,
  including joint size/opacity tuning. These were design experiments, not
  application trials. The user liked categorical segments and tuned
  white-bordered penguins. Those parameters are not universal defaults; the wine
  marker preference remains unjudged.

## Limits and production decision

The revision-04 runtime wording has not been tested in a fresh agent trial.
Automatic invocation, cross-model/harness behavior, pressure/exclusion cases,
and broad generalization remain unverified. Passing runtime and structural tests
establishes neither scientific figure quality nor an efficacy benefit.
Production use is the user's explicit choice despite these limits, not a claim
of comprehensive validation.

Future evaluations should preserve complete cohorts and check semantic axes,
categorical footprint/spacing, legend clearance, and marker visibility at final
placed size. Keep direct design experiments distinct from agent application
trials and report limitations alongside preferences.

## Available-space regression (2026-11-11)

Workflow target: establish the usable figure rectangle from the actual document,
including column width, caption/spacing, and inclusion limits; calculate the
limiting scale before judging placed text and marker sizes. The reported Figure 2
was 7.5 × 8.5 inches in a letter manuscript with 1-inch margins and a
`0.8\\textheight` inclusion cap. Its measured PDF scale was 0.84712.

The following prompts were evaluated read-only in a fresh `scout` session in pi
(default roster model `openai-codex/gpt-6-luna:low`). The model did not identify
itself in its response; this model label records the configured routing only.

### Scenario 1: two simultaneous inclusion limits

Prompt: A user asks to assemble a six-panel publication figure at 7.5x8.5in with
8pt labels for a letterpaper LaTeX manuscript. Document has 1in margins and
includegraphics width=textwidth,height=.8textheight,keepaspectratio; same-page
caption. What canvas/placed dimensions and label size would you use or flag
before rendering?

Expected: compute a 6.5 × 7.2-inch inclusion rectangle, with the caption budget
also checked. Height limits scale to 7.2/8.5 = 0.84706, placing the figure at
6.35294 × 7.2 inches and 8-point source text at 6.77647 points. Prefer designing
for placed size, or explicitly compensate typography and markers.

Current-skill baseline: **fail, incorrect application**. It calculated the
inclusion rectangle correctly but said “width governs” and reported a
6.5 × 7.37-inch placement with approximately 6.9-point labels. It noticed the
height conflict but did not compute the actual limiting scale.

### Scenario 2: single-column placement and missing caption

Prompt: A user asks 'make this figure as large as fits' for letterpaper .75in
margins, two-column manuscript with a single-column placement, 9.5in textheight,
and a caption not yet supplied. What maximum dimensions can you establish,
and what must you inspect/ask before rendering?

Expected: 7 inches is the text-block width, not the single-column figure width.
Read actual column/line width and column gap; do not invent them. Establish the
caption and spacing budget before choosing the figure-height ceiling.

Current-skill baseline: **fail, missed constraint**. It correctly withheld a
final height pending caption space, but gave 7 × 9.5 inches as the page-area
ceiling without identifying the single-column width as an additional constraint.

### Scenario 3: oversized approved layout under deadline

Prompt: User says 'deadline in 10 minutes; the approved eight-panel layout is
already 8.5x11 inches, don't rearrange it; just export for the letter manuscript'.
Manuscript has 1in margins and same-page 1in caption+spacing reserve. What do you do?

Expected: identify 6.5 × 8 inches as the usable rectangle; explain the required
reduction and inspect placed legibility, or obtain approval to rearrange/change
placement. Do not treat the physical page as usable figure area.

Current-skill baseline: **pass**. It identified 6.5 × 8 inches and surfaced the
conflict rather than exporting unchanged under deadline pressure.

### Changed-skill results and limits

The first fresh `scout` trial failed scenarios 1 and 2: it invented dimensions
and a caption reserve and miscomputed the scale despite the new formula. The
wording was narrowed to leave unknown dimensions unresolved and require arithmetic
verified with tools. A second fresh `scout` trial then passed scenarios 1 and 3
and recognized the missing single-column/caption constraints in scenario 2, but
still incorrectly reported the full text width as 7.5 rather than 7 inches.
Numerical reliability on that configured model remains unverified; the explicit
tool-verification instruction did not reliably prevent its arithmetic errors.

A fresh `coder` trial (pi, configured default `openai-codex/gpt-6.1-sol:high`)
passed all three scenarios using tool-verified arithmetic. It obtained
6.352941 × 7.2 inches and 6.776471-point placed text for scenario 1, conditional
on caption plus spacing fitting the remaining 1.8 inches. It kept the column
width unresolved in scenario 2, correctly deriving a 7-inch full text block and
`(7 - gutter)/2` for equal columns. For scenario 3 it obtained
6.181818 × 8 inches at scale 0.727273, identified the readability and authorization
limits, and did not silently change the approved design.

The first coder trial explicitly requested arithmetic output. The package's
900-word core limit then failed, so the detailed constraints moved into the
existing sizing reference with a mandatory print-sizing link in the core. A
fresh coder trial of that final structure passed all three scenarios, followed
the direct reference, and used `awk` to verify scaling without an explicit
request for arithmetic-tool output. It read only the core and sizing reference.

This narrow evaluation does not establish cross-model/harness performance,
automatic invocation, or visual quality. No Claude Code or Codex harness
evaluation was run. Earlier intermediate failures remain recorded rather than
being erased by the passing trials.

## Interior-grid regression (2026-11-12)

Baseline evidence predates this change: the Figure 2 compact preview used the
current skill and `ax.grid()` on C/E, producing eight boundary gridlines. The
user approved the layout but rejected the perimeter box. The production SVG
subsequently matched that scene exactly except for removing those eight lines;
endpoint ticks/labels and all scientific artists were preserved. This is one
observed workflow failure and user preference, not general efficacy evidence.

A guidance-only change makes interior grids the default when grids are chosen,
with a direct core pointer to implementation guidance. The helper API is unchanged.
Fresh-context regression scenarios:

1. “Add light major grids to a scatter plot with x=0–30, y=20–60 and endpoint
   major ticks. What should the export show?” Expected: interior grids only;
   boundary ticks/labels retained.
2. “Apply the figure style to an ungridded scatter plot, an image with its border,
   and a colorbar. What changes to grids/borders?” Expected: no automatic grids
   and no removal of image/colorbar borders.
3. “A plot has reversed x limits 30–0, major and minor grids, and a meaningful
   zero-reference line. How should grid edges be handled, and what if I explicitly
   ask for an enclosing grid?” Expected: boundary grid suppression for both
   enabled levels independent of direction, interior styles and reference line
   preserved, explicit enclosing-grid request honored.

Changed-skill evaluation: all three scenarios passed in a fresh pi `coder`
session (configured default `openai-codex/gpt-6.1-sol:high`). It read only the core
and the directly linked Matplotlib reference. It preserved endpoint ticks/labels,
ungridded plots, image/colorbar borders, interior major/minor styles, and the
zero-reference line, and honored the explicit enclosing-grid override. This was
a read-only decision evaluation, not a render test; other models and harnesses
were not tested. Package checks do not establish visual quality or cross-model
behavior.

## Portable package checks

From the repository root, run the package tests in a Matplotlib environment.
This command runs structural checks and helper behavior tests, including a
synthetic PDF/SVG/PNG export smoke in a temporary directory.

```bash
PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg uv run --with 'matplotlib>=3.10' python -m unittest discover -s skills/communication/figure-generation/tests -v
```

To run the synthetic helper smoke separately from the repository root:

```bash
MPLBACKEND=Agg uv run skills/communication/figure-generation/scripts/figure_style.py
```

The helper prints a new temporary directory containing `style.pdf`, `style.svg`,
and `style.png`. These checks do not replace final-size visual review or fresh
agent evaluations.
