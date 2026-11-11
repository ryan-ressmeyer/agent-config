# Comparisons, overlap, and uncertainty

## Match the encoding to the question

Use aligned positions when readers need to compare values precisely. Heer and
Bostock's proportional-judgment experiments support this for their tested tasks,
not a universal ranking independent of purpose. A trend can warrant lines;
measurements with pairing warrant a representation that preserves those links.
A line should not imply continuity or ordering that the measurement lacks.

For small-sample continuous measurements, show distributions and supplied
pairing rather than hiding them inside mean bars. Weissgerber et al.'s critique
does not prohibit categorical count bars or legitimate time-series lines.
For larger cohorts, choose the representation for the comparison and display
resolution, following the core's complete-cohort rule. When overlay hides related
populations' distributions or differences, facet them on consistent scales to
support direct comparison. Faceting is conditional; choose panel count from the
question rather than requiring every population to be split.

## Meaningful zero and categorical axes

Choose axis geometry from scientific meaning, not the plotting function. When
zero is the natural displayed lower bound, as for ordinary nonnegative counts,
place the bottom axis at y=0 without negative padding; the vertical axis may
float. This applies to count points or lines as well as bars. Positive values
alone do not require a zero-based scatter view. Preserve truthful scales and
the intended comparison rather than forcing zero into every numerical axis.

For nominal or ordered categorical axes, use separate segments centered on the
category ticks rather than a continuous spine suggesting an intervening continuum.
Integer-valued measurements and time axes are not categorical merely because
their ticks are integers. Segment span should match or slightly exceed the
intended displayed category footprint along the categorical direction, including
subgroup offsets, jitter envelope, and marker edges. For vertical categorical
axes, span means height.

Use equal lengths within an axis, based on the widest intended category display
footprint. Prefer a declared display envelope to random realized extrema so
segment lengths do not become an encoding of sample size or variability. Keep
visible inter-category gaps; if footprint coverage conflicts with separation,
revisit layout instead of joining the segments or truncating the display. No
fixed percentage of category spacing is a general rule. Reassess the footprint
after marker tuning. Categorical segments and semantic overrides require caller
work; the optional helper does not implement them.

## Marker treatment and overlap

Preserve established color, shape, and fill encodings when choosing candidates:

- With little overlap and adequate contrast, try simple filled markers.
- For pale fills against the background, try a thin dark edge for contrast.
- For partially overlapping colored points where individual boundaries matter,
  try a thin white edge.
- For one-group overlapping boundaries, consider open circles. Krzywinski & Wong's
  *Plotting symbols* offers expert guidance for that case and for strong category
  boundaries, not a universal white-, dark-, or open-marker prescription.

Judge overlap and contrast at final placed size, not by point count alone.
Display-space overlap and contrast can diagnose problems; these candidates have
no validated numerical thresholds or mandatory optimization routine. Do not
replace a semantic hollow/filled distinction merely to apply a candidate style.

Choose border treatment first, then jointly tune marker size and opacity at final
placed size. Equal nominal outer dimensions do not imply equal perceived size
or weight; a white border can make a filled triangle appear smaller or lighter.
Check isolated points, crowded regions, and subgroup visibility in the actual
export. Size/opacity settings from one approved example are not global defaults.
For Matplotlib's stroke/size interaction, use the implementation reference.

Transparency, smaller markers, layering, or separate panels can expose overlap
without dropping records. Severe overlap calls for size/layout changes, faceting,
or a justified complete-cohort aggregate, never thinning. Borders cannot reveal
exactly coincident observations; saturated regions still conceal multiplicity.
Do not claim that a visible cloud lets readers count every observation.
Rasterization reduces vector-export cost while retaining all plotted records.
Density, binning, or summaries answer a different question from individually
visible observations. State the binning/kernel, denominator, and normalization;
account for out-of-range, missing, or invalid values instead of silently losing them.
Jitter can clarify coincident values only when displacement is disclosed and
does not suggest precision or variation absent from the measurements.

## Define uncertainty before drawing it

Distinguish variation among observations (e.g. SD, quantiles) from uncertainty in
an estimate (e.g. SE, confidence or credible intervals). Name the interval type
in a concise key; retain coverage, estimated quantity, and independent unit in
accompanying definitions unless needed immediately for safe decoding. Reuse supplied
estimates; request analysis approval if the required interval has not been computed.

Paired, repeated, nested, and clustered measurements require their dependence
to be preserved. Independent-sample error-bar examples are not shortcuts for
inference in those designs. Overlapping or non-overlapping bars alone do not
establish the result of a hypothesis test. Show approved comparison annotations
only when their referents are unambiguous and they help the scientific question.

## Semantic color

For scalar values, match sequential color to ordered magnitude, diverging color
to a meaningful center, and cyclic color to periodic quantities. Avoid rainbow
maps that create unintended perceptual boundaries. Verify lightness structure
and color-vision accessibility; do not choose a map solely because it looks
pleasant. Crameri et al.'s scalar-map guidance does not prescribe recoloring
true RGB images or experimental channels. Categorical identity needs distinct
categories, not an implied scalar order. Reuse the manuscript's semantics.
