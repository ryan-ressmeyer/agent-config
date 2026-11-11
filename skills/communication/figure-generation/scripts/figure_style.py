# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.10"]
# ///
"""Optional scoped defaults and explicit styling for ordinary Cartesian axes."""

from math import isfinite
from numbers import Real

import matplotlib as mpl


def _number(value, name, *, zero=False):
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not isfinite(value)
        or (value < 0 if zero else value <= 0)
    ):
        raise ValueError(f"{name} must be finite and {'nonnegative' if zero else 'positive'}")


def style_context(*, text_size=8, font_family="Liberation Sans", axis_width=0.8):
    """Return an rc_context; create and export figures inside its with block."""
    _number(text_size, "text_size")
    _number(axis_width, "axis_width")
    if not isinstance(font_family, str) or not font_family.strip():
        raise ValueError("font_family must be a nonempty font name")
    return mpl.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font_family],
            "font.size": text_size,
            "font.style": "normal",
            "font.weight": "normal",
            "axes.labelsize": text_size,
            "axes.titlesize": text_size,
            "axes.labelweight": "normal",
            "axes.titleweight": "normal",
            "xtick.labelsize": text_size,
            "ytick.labelsize": text_size,
            "legend.fontsize": text_size,
            "legend.title_fontsize": text_size,
            "figure.titlesize": text_size,
            "figure.titleweight": "normal",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.linewidth": axis_width,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": axis_width,
            "ytick.major.width": axis_width,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def _visible_bounds(axis):
    low, high = sorted(axis.get_view_interval())
    ticks = [
        location
        for location, tick in zip(axis.get_majorticklocs(), axis.get_major_ticks())
        if isfinite(location)
        and low <= location <= high
        and axis.get_visible()
        and tick.get_visible()
        and tick.tick1line.get_visible()
    ]
    if len(set(ticks)) < 2:
        raise ValueError("set at least two visible bottom/left major ticks per axis")
    return min(ticks), max(ticks)


def style_axes(ax, *, mode="scatter", offset=4, linewidth=0.8):
    """Style one explicit Cartesian axes after setting limits and major ticks.

    mode='scatter' floats both spines; mode='bar' declares nonnegative bars
    and retains a horizontal zero baseline. Call again after changing the view.
    Linear/log scales and reversed limits work; bar y must be linear and show 0.
    Images/colorbars are never discovered or styled implicitly.
    """
    _number(offset, "offset", zero=True)
    _number(linewidth, "linewidth")
    if mode not in ("scatter", "bar"):
        raise ValueError("mode must be 'scatter' or 'bar'")
    if getattr(ax, "name", None) != "rectilinear":
        raise ValueError("style_axes requires ordinary Cartesian axes")
    if ax.get_xscale() not in ("linear", "log") or ax.get_yscale() not in (
        "linear", "log"
    ):
        raise ValueError("style_axes supports only linear or log scales")
    if mode == "bar" and (
        ax.get_yscale() != "linear" or not min(ax.get_ylim()) <= 0 <= max(ax.get_ylim())
    ):
        raise ValueError("bar zero baseline requires linear y limits containing zero")
    xbounds, ybounds = _visible_bounds(ax.xaxis), _visible_bounds(ax.yaxis)
    # Spine.set_position resets ticks; preserve explicitly hidden major marks/labels.
    # ponytail: retain major visibility only; reapply custom/minor styling afterward.
    visibility = []
    for axis in (ax.xaxis, ax.yaxis):
        visibility.append([
            (tick.get_visible(), *[artist.get_visible() for artist in
             (tick.tick1line, tick.tick2line, tick.label1, tick.label2)])
            for tick in axis.get_major_ticks()
        ])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_visible(True)
    ax.spines[["left", "bottom"]].set_linewidth(linewidth)
    ax.spines["left"].set_position(("outward", offset))
    ax.spines["left"].set_bounds(*ybounds)
    ax.spines["bottom"].set_position(("outward", offset) if mode == "scatter" else ("data", 0))
    ax.spines["bottom"].set_bounds(*(xbounds if mode == "scatter" else sorted(ax.get_xlim())))
    ax.tick_params(which="both", direction="out", width=linewidth,
                   top=False, right=False, labeltop=False, labelright=False)
    for axis, states in zip((ax.xaxis, ax.yaxis), visibility):
        for tick, (visible, *artists) in zip(axis.get_major_ticks(), states):
            tick.set_visible(visible)
            for artist, show in zip(
                (tick.tick1line, tick.tick2line, tick.label1, tick.label2), artists
            ):
                artist.set_visible(show)


def smoke_demo():
    """Render synthetic scatter/bar examples to a new temporary directory."""
    from pathlib import Path
    from tempfile import mkdtemp

    import matplotlib.pyplot as plt

    output = Path(mkdtemp(prefix="figure-style-smoke-"))
    with style_context():
        fig, (scatter, bar) = plt.subplots(1, 2, figsize=(5, 2.5), layout="constrained")
        try:
            scatter.scatter([1, 2, 3], [1, 3, 2], color="0.25")
            scatter.set(xlim=(0, 4), ylim=(0, 4), xlabel="Input (a.u.)", ylabel="Output (a.u.)")
            scatter.set_xticks([0, 2, 4])
            scatter.set_yticks([0, 2, 4])
            bar.bar([1, 2], [2, 3], color="0.6")
            bar.set(xlim=(0, 3), ylim=(0, 4), xlabel="Category", ylabel="Count")
            bar.set_xticks([1, 2])
            bar.set_yticks([0, 2, 4])
            style_axes(scatter)
            style_axes(bar, mode="bar")
            for ax, letter in zip((scatter, bar), "AB"):
                ax.text(0, 1.05, letter, transform=ax.transAxes, fontsize=10, fontweight="bold")
            for extension in ("pdf", "svg", "png"):
                fig.savefig(output / f"style.{extension}", dpi=160)
        finally:
            plt.close(fig)
    return output


if __name__ == "__main__":
    print(smoke_demo())
