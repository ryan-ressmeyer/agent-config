---
name: figure-generation
description: Use when creating, revising, reviewing, or exporting scientific figures, multi-panel plots, image galleries, or evidence diagrams for manuscripts, presentations, or reports.
---

# Figure generation

Build around a supported scientific question and reading context. Reuse established
decisions for tiny edits. This workflow does not authorize new analyses or conclusions.

## 1. Establish question, evidence, and destination

Read the request, manuscript context, supplied results, and existing figure code.
Identify the direct comparison, corresponding items/conditions/covariate ranges,
and intended audience, medium, placed size, and constraints. Infer an established
purpose; if several messages are plausible, propose a supported message and
panel rationale for confirmation before implementation. Ask only what context
cannot answer.

For print, the upper limit is the document's usable figure rectangle, after
margins, column width, caption/spacing, and inclusion limits—not the physical page.
Before choosing a canvas, read [placement constraints](references/matplotlib.md#layout-physical-size-and-export),
even when not using Matplotlib. Establish unknown dimensions and verify scaling
rather than assuming marginless letter paper. Screen-only output has more flexibility.

**Complete when:** the question, evidence, destination, usable figure rectangle,
and final placement scale are established, with consequential uncertainty resolved.

## 2. Design comparisons and inclusion

Let direct comparisons determine alignment, grouping, ordering, and space before
packing. Whitespace serves hierarchy and comparison, not a quota or page-filling
rule. Compact references and sparse display groups without changing analysis.
Reduce visual search and mental matching. Every element, including axes and text,
must identify, compare, orient, or qualify evidence. SHOW, DON'T TELL: use grouping,
local scales, and concise labels; fix layout rather than explaining it.
No overall title for manuscript figures; user-facing screen galleries may have one.
Panel labels/titles must earn their place without repeating axis labels.
Use concise established measurement names, not technical definitions as axis names.
Keep explanatory manuscript footers, processing/normalization sentences, definitions,
and generic caveats in caption/Methods/notes by default. Immediate decoding uses
concise labels, scales, keys, or graphical cues. Retain required units, uncertainty
definitions, condition identity, and scientific qualifications in the deliverable.
Include opaque IDs or metadata only for needed identification, cross-reference,
or comparison; retain the full mapping in source/notes.
For genuinely borderline, consequential inclusion choices, ask BEFORE
implementing; do not render speculative alternatives first.

Declare the cohort and representation. If plotting individual points, show ALL
observations in that cohort, without sampling or thinning for appearance or
performance. Rasterized artists can preserve every point. A justified density
or aggregate display must retain the declared data and disclose its meaning;
it must not imply that all individual observations are visible.

For plot choice, pairing, semantic axes, marker treatment, overlap, or uncertainty,
read [comparisons](references/comparisons.md). For legends, panel layout, scalar
heatmaps, RGB/channel images, or diagrams, read [layout and images](references/layout-images.md).

**Complete when:** panels have purposes and comparison-driven layout, inclusion
and representation are explicit, and consequential optional elements are resolved.

## 3. Implement from supplied results

Reuse project plotting helpers where equivalent. Preserve identities, pairing,
units, normalization, and supplied analysis results. Straightforward descriptive
calculations for an agreed display are allowed; obtain separate approval for
new fits, tests, exclusions, or interpretation-changing transformations.

At FINAL PLACED SIZE, start with 8 pt upright text and 10 pt bold panel letters;
retain conventional mathematical/scientific italics. These sizes are adjustable,
not targets to shrink below whenever a layout is crowded. Inherit the manuscript
sans-serif font; for new work choose an available Arial-like font and record any
relevant substitution. Use a white background. Default single-series marks to black
unless color conveys a meaningful established distinction. Inherit semantic palettes,
add colors sparingly, and use accessible non-color distinctions as needed.

Ordinary Cartesian axes start with 0.8 pt lines, outward ticks, and no top/right
spines unless meaningful. Continuous left/bottom spines default to floating outward
4 pt, adjustable, ending at outermost visible major ticks without changing limits.
Select meaningful-zero baselines and categorical segments by semantics, not plotting
function (see comparisons). Preserve meaningful image borders and colorbars.
Give each unit image in scientific galleries its own calibrated scale bar.
For same-unit x/y value comparisons, prefer a square plotting region and equal
data scaling; otherwise choose aspect for the question, not a blanket square rule.

For grids and Matplotlib, read [implementation](references/matplotlib.md).
The optional [helper](scripts/figure_style.py) provides scoped defaults and explicit
axis styling; import it only when useful, not as a replacement plotting framework.

**Complete when:** reproducible source encodes the agreed display, accounts for
the supplied data, and applies relevant defaults or records justified deviations.

## 4. Render, inspect, and revise

Inspect actual post-draw exports at final placed size. Check local labels/scale
bars against nearby images, data, adjacent panels, and row transitions; reserve
room for labels. Distinguish intentional annotation from accidental overlap.
Check legibility, hierarchy, alignment, clipping, cohort accounting, truthful
scales/normalization, and accessible distinctions. Verify annotations and comparisons
against supplied evidence. Canvas containment or bounding-box tests alone do not
prove clarity. Remove redundancy, rearrange, or split rather than shrink.
Revise and inspect within budget; report unresolved fidelity/readability defects.

**Complete when:** the delivered render has been visually inspected and fidelity
checks pass, or specific unresolved defects are explicitly reported.

## 5. Deliver

Export PDF, SVG, and PNG from one reproducible render unless the task specifies
otherwise. Supply source and short notes identifying inputs, display calculations,
normalization, cohort/aggregation meaning, and relevant limitations or deviations.
Exact statistical reporting normally belongs in captions; useful uncertainty or
comparison annotations belong in plots, without automatic significance stars.
Draft a caption only when requested.

**Complete when:** source, requested exports, and meaning/provenance notes are
present, the actual files were checked, and unresolved issues are disclosed.
