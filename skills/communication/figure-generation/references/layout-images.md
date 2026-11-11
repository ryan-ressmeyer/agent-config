# Layout, images, and diagrams

## Panel hierarchy and reading order

Translate the core's direct comparisons into spatial relationships. Align related
items or conditions at comparable covariate values/ranges so readers need not
search across the page or mentally match distant examples. Independently sorting
each condition is insufficient when the comparison needs correspondence across
groups. Let those relationships determine grouping, ordering, and area before
optimizing packing. Row/column traversal is an implementation consequence, not
a universal reading rule or something a long legend should have to explain.

Display alignment does not establish statistical pairing or exact covariate
matching. Preserve actual values and disclose relevant mismatch in notes; do not
relabel approximate correspondence as a matched design. Share scales only when
quantities and units justify comparison. Small multiples can expose repeated
structure without requiring equal-sized boxes, a fixed grid, or a golden ratio.

## Whitespace and compactness

Whitespace separates meaningful groups and comparisons; neither a fixed fraction
nor a filled page is a target. A small reference group normally occupies one
compact, consistent comparison lane unless the relationship warrants otherwise.
Lane orientation follows the comparison. Do not squeeze primary evidence to
reserve mostly empty reference slots or duplicate reference lanes to fill a grid.

Sparse terminal DISPLAY groups may be merged into neighboring display groups or
repacked when scientifically appropriate. This changes arrangement, not analytical
bins, cohorts, pairings, exclusions, or selected examples. Preserve all records and
actual values without stretching images or changing physical scales. Ask before
repacking would sacrifice meaningful correspondence.

Use a layout engine or measured positions rather than stacking manual nudges.
Label the comparison variables, not every available field. For example, latency
belongs on the canvas when temporal differences matter, not merely because
selection metadata contains a lag. Keep panel letters consistently placed in
reading order. Restructure or split illegible galleries under the core's footprint
rules rather than explaining their layout in prose.

## Needed keys and legend placement

Decide required legend/key content before rendering, under the core's inclusion
and approval rules. Whitespace permits placement, not extra content. Keep keys
needed to decode the evidence; ask before implementing consequential optional
additions rather than using available space to justify them.

Inspect the data and layout, then place needed keys in genuinely usable in-panel
whitespace when they remain legible without concealing marks or uncertainty.
For this manuscript style, use below-panel placement as the fallback when panel
space cannot safely hold the key; do not automatically reserve a top strip.
A shared key must have clear referents across every panel it serves. Placement
inside an axes rectangle is not inherently occlusion, and an apparently empty
region is not proof of safe placement.

Re-render after repositioning and check all relevant marks and panels in actual
exports at final placed size, including nearby labels, summaries, and other keys.
Revise layout if the key hides evidence or makes cross-panel decoding ambiguous.

## Local spacing and post-draw review

Keep each image, local scale/label, and associated plot visibly one unit. Use
sensible internal spacing and clear separation from the next unit; deliberately
reserve room for labels, including at row transitions. Full-canvas containment
does not establish that these local relationships are readable.

Inspect post-draw labels and scale bars against nearby images, data marks,
adjacent panels, and row transitions in actual exports. Distinguish an intentional
annotation from accidental interference. Bounding-box intersection flags a region
to inspect; it alone does not establish occlusion of visible data marks. Conversely,
a passed metadata-bounds test is not proof of clarity. Review the actual marks
and decoding cues before accepting the arrangement.

## Scalar heatmaps

A scalar image encodes one numerical quantity per location. Document quantity,
units, origin, orientation, extent, interpolation, and color normalization in
accompanying definitions. Keep immediately needed decoding cues on the canvas;
use a labeled color scale where numerical decoding matters. Comparable panels
need common color limits when color is intended to support magnitude comparison.
If different limits are scientifically warranted, make that difference explicit;
do not let shared-looking keys imply a shared mapping.

## True RGB and channel images

True RGB images contain color information rather than one scalar value. Preserve
the scientific meaning of RGB or experimental channel assignments; do not apply
a scalar colormap wholesale. Identify channels and composite rules. If channel
colors are selectable, distinguish them accessibly and consider separate channel
views when a composite hides evidence. Do not imply an RGB colorbar is a scalar
measurement key.

## Spatial scaling and contrast

Keep pixel aspect, spatial calibration, orientation, and displayed extents truthful.
For the core's per-unit gallery scale bars, derive bar length from each image's
calibration and displayed extent. Use readable local labels with physical units;
do not hard-code a length or unit. A detached shared bar or a sentence describing
image extent cannot substitute for those local bars. Outside per-unit galleries,
a shared bar is valid only when displayed spatial scale is shared, not merely
when arrays have equal shapes. An image border can carry orientation or grouping.
Label inset locations and magnification; do not stretch an image to fill a slot.

Use common contrast mapping for intensity comparisons. Per-image contrast may
support morphology inspection, but disclose the mapping and loss of absolute
intensity comparability. Never silently normalize each image to its own extrema.
Report clipping/saturation and supplied preprocessing that affect interpretation;
changing scientific normalization remains subject to the core's approval gate.

## Evidence diagrams

Simplify to the relationships the reader needs. Distinguish measured, established,
and hypothetical connections. Schematic placement, arrows, and shapes must not
imply unsupported anatomy, directionality, causation, or scale. Redundant labels,
shapes, or line styles can support accessibility; remove repetition only when
meaning and decoding remain intact.
