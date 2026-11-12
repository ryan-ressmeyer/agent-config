# Matplotlib implementation and optional helper

## Prefer the project's environment and helpers

Use an existing equivalent helper rather than importing this one redundantly.
The bundled helper requires only Matplotlib (3.10+) and the standard library.
It does not load data, choose encodings, create publisher presets, or infer chart
kind. Import its functions; read its source only when modifying implementation.

Resolve the skill directory to its actual path, then add its `scripts` directory
to the plotting script's import path. For example, with `SKILL_DIR` a `Path`:

```python
import sys
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from figure_style import style_context, style_axes
import matplotlib.pyplot as plt

with style_context(font_family="Liberation Sans"):
    fig, ax = plt.subplots(figsize=(3, 2.5), layout="constrained")
    ax.scatter(x, y, color="black", rasterized=True)  # complete supplied cohort
    ax.set(xlabel="Input (unit)", ylabel="Response (unit)")
    # Set scientific limits and major ticks explicitly as the comparison needs.
    style_axes(ax, mode="scatter")
    for extension in ("pdf", "svg", "png"):
        fig.savefig(output_dir / f"figure.{extension}", dpi=300)
    plt.close(fig)
```

The example assumes `x`, `y`, and `output_dir` already exist; it performs no
analysis or input selection. Keep both creation and export inside the context.
Select the inherited/available typeface explicitly and record substitutions;
Matplotlib's font lookup can fall back if the requested font is missing.

## API and boundaries

`style_context(text_size=8, font_family="Liberation Sans", axis_width=0.8)`
returns a restoring `matplotlib.rc_context`. It sets upright typography, white
backgrounds, outward tick defaults, PDF/PS TrueType output, and SVG text. Font
sizes/widths must be positive finite numbers; font name must be nonempty.
SVG text remains editable but depends on the viewing machine's fonts. Verify
font resolution and actual PDF/SVG appearance, not merely rcParams.
Conventional math typography is not overridden.

`style_axes(ax, mode="scatter", offset=4, linewidth=0.8)` styles only the
explicit axes. Set limits and major ticks BEFORE calling; call again if either
changes. It bounds floated spines to in-view, visible bottom/left major ticks.
The offset uses Matplotlib's display-point spine transform, not a data-coordinate
subtraction. `mode="scatter"` floats both left and bottom spines. `mode="bar"`
keeps the bottom spine at data zero across the current x view and floats only y.
These names select explicit geometry, not artist detection or chart semantics.
The helper does not inspect plotted artists. Choose the geometry using the
comparisons reference's meaningful-zero guidance; a count scatter may need the
zero-baseline geometry. Set scientific limits yourself, including a lower y limit
of zero without negative padding when that is the natural displayed lower bound.

Neither function changes observations, limits, scales, or aspect. Linear/log
Cartesian scales and reversed limits are supported. The bar y scale must be
linear with zero inside the view. Other scales/projections and fewer than two
visible major ticks per axis raise `ValueError` before styling. Offset must be
finite and nonnegative; linewidth must be finite and positive. Do not invoke on
image or colorbar axes unless intentionally changing their borders. It does not
traverse figures looking for axes to restyle. Custom tick styling and per-tick
minor visibility may need reapplying because spine positioning resets ticks;
only major-tick visibility is retained explicitly.

The helper neither creates categorical segments nor chooses marker treatments.
Apply caller-owned categorical segments or other semantic overrides after helper
styling, and reapply them when geometry changes. Do not expect `mode="scatter"`
to infer a zero baseline or `mode="bar"` to set a lower limit of zero.

## Marker stroke and nominal size

In `scatter`, `s` is measured in points squared and `linewidths` in points.
A centered edge stroke extends beyond the marker path, so changing the border
can change the visible footprint even when `s` is unchanged. Set `edgecolors`
and `linewidths` explicitly for the selected treatment; account for marker shape
when controlling nominal outer dimensions. Equal nominal dimensions are not a
perceptual-size guarantee. Follow the comparisons reference's border-first,
joint size/opacity review and reassess any categorical footprint after tuning.
The helper supplies no marker tuning or optimization.

## Layout, physical size, and export

These placement constraints apply to all print figures, not only Matplotlib.
Read the destination's page dimensions, margins, actual column/line width,
caption and spacing budget, and inclusion width/height limits. In LaTeX, inspect
`\linewidth`/`\columnwidth`, `\textheight`, and the `\includegraphics` options at
the placement site. A single-column figure in a two-column document cannot use
the full text-block width. Subtract any same-page caption and spacing from
available height, then apply any tighter inclusion or journal limits. Keep
unknown column widths and caption heights unresolved until you inspect the
template or agree on an explicit budget; do not invent values. The maximum
rectangle is a constraint, not a default canvas.

For an existing figure of width w and height h fitted proportionally into a
W × H rectangle, calculate r = min(W/w, H/h); placed dimensions are rw × rh and
source text, marker lengths, strokes, and offsets scale by r. Verify the
arithmetic with a calculator, code, or LaTeX dimension output, not mental
estimates. Design and inspect at that placed size; prefer matching source
dimensions or explicitly compensate sizes rather than silently shrinking labels
and points. Confirm actual dimensions in the compiled document. An 8 pt source
label is not 8 pt after reduction. Add panel letters explicitly, e.g. with
`ax.text` and the core's letter size/weight, rather than changing all typography.

Choose constrained layout or measured manual layout. Calling `tight_layout()`
disables constrained layout; do not combine them. Avoid blind
`bbox_inches="tight"` for exact-size exports because cropping changes the canvas
footprint. Confirm saved dimensions and inspect PDF/SVG and raster output.
Rasterize dense artists selectively; keep text and axes vector where possible.

Use `set_aspect`/`set_box_aspect` explicitly only when scientific geometry calls
for them. Equal units and a square box also require compatible displayed spans;
do not silently change scientific limits to force both. Spatial images retain
their calibrated geometry. Palettes and whether to use grids remain caller decisions.

When grids are used, default to interior-only lines: omit gridlines coincident
with either axis limit so they do not form a perimeter box. Retain boundary ticks
and labels, intended spines, and meaningful reference/zero baselines. Do not add
grids to ungridded plots or remove image/colorbar borders to apply this rule.
In Matplotlib, set limits, ticks, and spine positions first, then enable the
chosen grid and hide only boundary ticks' `gridline` artists. Handle each enabled
grid level and either axis direction; leave interior visibility/style unchanged.
Reapply after changing limits/ticks and inspect the saved export, not just artist
flags. An explicitly requested enclosing grid overrides this default.

## Synthetic smoke and checks

From the skill directory, run `MPLBACKEND=Agg uv run scripts/figure_style.py`.
The PEP 723 metadata declares its dependency for standalone use; when a project
already supplies Matplotlib, use `uv run python scripts/figure_style.py` instead.
It prints a new temporary directory containing `style.pdf`, `style.svg`, and
`style.png`, made from synthetic scatter/bar values only. Inspect those files;
the smoke is not an application evaluation. No project output is overwritten.

Run the package checks with
`uv run python -m unittest discover -s tests -v` in a Matplotlib environment.
They cover context restoration, display-point offsets, visible bounds, zero
baseline, data/geometry preservation, image/colorbar isolation, invalid input,
and reversed/log views. Structural checks do not establish visual quality.
