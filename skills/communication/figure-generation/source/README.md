# Source index

These are provenance notes, not additional workflow requirements. The parent
reviewed the external sources during development; the draft uses original
summaries of selected guidance. Ryan's confirmed preferences have local authority;
expert advice, empirical studies, implementation documentation, and other agent
skills have different evidentiary roles.

## Local authority

- **Ryan's confirmed interview preferences.** Primary user requirements, confirmed
  before drafting. Adopted the workflow's typography, selective axis treatment,
  print-only footprint ceiling, complete-cohort rule, approval boundaries, and
  reproducible delivery preferences. These are local defaults, not empirical
  claims of universal superiority. The private interview is not distributed.
- **Ryan's confirmed post-review feedback (revision 02).** Primary user preferences
  from the development review. Adopted comparison-first correspondence and layout,
  conditional faceting, no overall manuscript title, a higher threshold for canvas
  prose and metadata, concise measurement labels, local calibrated gallery scale
  bars, and black single-series marks unless semantic color is justified. Retain
  definitions and caveats outside the canvas unless immediately needed to decode
  it safely. These corrections are not external-source findings or demonstrated
  efficacy gains; private reviews and task-specific solutions are not distributed.
- **Ryan's follow-up review (revision 03).** Confirmed functional whitespace,
  compact reference/display grouping, and a stricter manuscript-prose boundary.
  Local post-draw review criteria also address parent-reported annotation crowding.
  These are user preferences and review safeguards, not external empirical findings
  or evidence that the revised wording improves outcomes.
- **Ryan's reviewed figure feedback (revision 04).** Confirmed semantic zero
  baselines, needed-key placement in usable panel space with below-panel fallback,
  footprint-based uniform categorical segments, and conditional marker candidates
  followed by size/opacity tuning. These are local preferences and design
  judgments, not validated thresholds, universal marker winners, or demonstrated
  improvements from the revised wording. Example-specific parameters are not
  runtime defaults; helper capabilities remain unchanged.
- **Parent-reviewed manuscript/development corpus.** Supporting examples of local
  practice, not a representative evaluation corpus or universal prescriptions.
  Used to motivate context-sensitive comparison and layout decisions. No original
  plotting code, fixture identities, reference figures, or task-specific layout
  recipes are included or linked here.

## Communication and visual comparison

- [Rougier et al., 2014](https://doi.org/10.1371/journal.pcbi.1003833).
  Expert workflow guidance (CC0). Adopted audience/message/medium and contextual
  small multiples; qualified beauty as subordinate to scientific communication.
- Nature Methods *Points of View*: [layout](https://doi.org/10.1038/nmeth.1711),
  [salience](https://doi.org/10.1038/nmeth.1762),
  [axes](https://doi.org/10.1038/nmeth.2337),
  [labels](https://doi.org/10.1038/nmeth.2405), and
  [neural diagrams](https://doi.org/10.1038/nmeth.3777).
  Expert design guidance, not empirical proof of every recommendation. Adopted
  hierarchy, useful labels, and selective axes. Rejected fixed grid opacity,
  golden-ratio prescriptions, and categorical anti-redundancy rules. Qualified
  diagram simplification to preserve evidence and anatomical uncertainty.
- [Krzywinski & Wong, 2013, *Plotting symbols*](https://www.nature.com/articles/nmeth.2490)
  (DOI 10.1038/nmeth.2490). Parent-verified expert guidance supporting open circles
  for one-category overlap and strong boundaries between categories. It does not
  establish universal white/dark borders or validate the draft's conditional
  overlap/contrast heuristics. No source text or figures are reproduced.
- [Heer and Bostock, 2010](https://doi.org/10.1145/1753326.1753357).
  Empirical graphical-perception study. Adopted task-bounded support for aligned
  position comparisons; rejected a task-independent ranking of all chart types.
- Wilke, *Fundamentals of Data Visualization* author manuscript:
  [multi-panel figures](https://clauswilke.com/dataviz/multi-panel-figures.html),
  [overlapping points](https://clauswilke.com/dataviz/overlapping-points.html),
  [uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html).
  Expository synthesis (CC BY-NC-ND). Adopted conditional layout/overlap choices
  and spread-versus-estimation distinctions. No modified book content is copied;
  the complete-cohort prohibition on thinning comes from Ryan, not this book.

## Statistical and image meaning

- [Weissgerber et al., 2015](https://doi.org/10.1371/journal.pbio.1002128).
  Empirical survey and methodological critique. Adopted distribution and pairing
  visibility for small-sample continuous data; rejected a ban on count bars or
  valid lines. Does not authorize recomputing analyses.
- [Krzywinski and Altman, error bars](https://doi.org/10.1038/nmeth.2659).
  Expert statistical explanation. Adopted explicit error-bar definitions;
  qualified independent-sample examples as unsuitable inference shortcuts for
  paired, repeated, or clustered measurements.
- [Crameri et al., 2020](https://doi.org/10.1038/s41467-020-19160-7).
  Scientific color-map review (CC BY). Adopted scalar semantics, perception, and
  accessibility guidance; rejected replacing scientific RGB/channel meaning
  with a universal scalar palette.
- [Jambor et al., 2021](https://doi.org/10.1371/journal.pbio.3001161).
  Image-reporting research and practical guidance (CC BY). Adopted objective-to-
  panel planning, truthful spatial scaling, annotations, and inset identification;
  qualified contrast choices by whether intensity comparison remains possible.

## Implementation and destination constraints

- Official Matplotlib documentation:
  [constrained layout](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html),
  [spine positioning](https://matplotlib.org/stable/api/spines_api.html),
  [scatter](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html),
  [rc_context](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.rc_context.html),
  [savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html),
  [fonts](https://matplotlib.org/stable/users/explain/text/fonts.html), and
  [colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html).
  Implementation authority, not aesthetic evidence. Adopted scoped rc settings,
  display-point offsets, stroke/marker-size interaction, selective rasterization,
  and format-aware export. Qualified tight cropping for exact-size output and
  incompatible layout engines.
- [Nature figure specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/).
  Publisher/phase-specific authority. Adopted checking the actual destination;
  rejected hard-coded universal journal rules or publisher presets.

## Other agent workflows

These supplied workflow patterns, not independently validated performance claims.
No whole skills, branding systems, templates, or executable implementations were
copied.

- Anthropic [graphing](https://github.com/anthropics/claude-tag-plugins/blob/main/claude-tag-data-viz/skills/graphing/SKILL.md)
  and [data visualization](https://github.com/anthropics/knowledge-work-plugins/blob/main/data/skills/data-visualization/SKILL.md).
  Adopted context awareness and render/inspect/revise; rejected compulsory
  titles, chartkit, branding, and universal stylistic defaults.
- OpenAI [visualize-data](https://github.com/openai/plugins/blob/main/plugins/data-analytics/skills/visualize-data/SKILL.md)
  and its companion build-web-data-visualization strategy.
  Adopted a compact decision brief and final-context QA; rejected runtime routing,
  compulsory titles, point-count floors, chart variety, mobile mandates, and
  brand palettes. Scientific print output is not a web dashboard by default.
- K-Dense [scientific visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md).
  Checklist/workflow reference only. Adopted reproducible export and review;
  rejected an installed framework and unsupported performance claims.

## Licensing and archiving

Links identify sources; they do not grant permission to redistribute their text
or figures. License labels above reflect the parent source review, not a new
legal audit. For sources without a stated license here, assume no redistribution
permission. The draft contains original summaries and original helper/test code,
not proprietary excerpts, copied manuscript code, or adapted ND-licensed text.
No source snapshots are bundled. Maintainers should record versions, access dates,
and licenses before later archiving or redistribution; links may change.
