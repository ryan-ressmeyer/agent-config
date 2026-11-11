"""Behavior checks for the optional helper; no trial inputs or figures."""

import importlib.util
from pathlib import Path
import shutil
import unittest

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "figure_style.py"


def helper():
    assert SCRIPT.is_file(), "optional figure_style helper not implemented"
    spec = importlib.util.spec_from_file_location("figure_style", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StyleContextTests(unittest.TestCase):
    def test_scoped_defaults_and_restoration_even_on_error(self):
        style = helper()
        before = mpl.rcParams.copy()
        with self.assertRaisesRegex(RuntimeError, "sentinel"):
            with style.style_context():
                self.assertEqual(mpl.rcParams["font.size"], 8)
                self.assertEqual(mpl.rcParams["font.style"], "normal")
                self.assertEqual(mpl.rcParams["font.sans-serif"], ["Liberation Sans"])
                self.assertEqual(mpl.rcParams["axes.linewidth"], 0.8)
                self.assertEqual(mpl.rcParams["xtick.direction"], "out")
                self.assertEqual(mpl.rcParams["ytick.direction"], "out")
                self.assertEqual(mpl.rcParams["figure.facecolor"], "white")
                self.assertEqual(mpl.rcParams["axes.facecolor"], "white")
                self.assertEqual(mpl.rcParams["savefig.facecolor"], "white")
                self.assertEqual(mpl.rcParams["pdf.fonttype"], 42)
                self.assertEqual(mpl.rcParams["svg.fonttype"], "none")
                raise RuntimeError("sentinel")
        for key in before:
            self.assertEqual(mpl.rcParams[key], before[key], key)
        with style.style_context(text_size=9, font_family="Liberation Sans", axis_width=1):
            self.assertEqual(mpl.rcParams["font.size"], 9)
            self.assertIn("Liberation Sans", mpl.rcParams["font.sans-serif"])
            self.assertEqual(mpl.rcParams["axes.linewidth"], 1)
        self.assertEqual(mpl.rcParams["font.size"], before["font.size"])


    def test_smoke_exports_synthetic_example_in_temporary_directory(self):
        style = helper()
        self.assertTrue(hasattr(style, "smoke_demo"), "synthetic smoke not implemented")
        directory = style.smoke_demo()
        try:
            self.assertEqual(directory.parent, Path("/tmp"))
            self.assertEqual({p.suffix for p in directory.iterdir()}, {".pdf", ".svg", ".png"})
            self.assertTrue((directory / "style.pdf").read_bytes().startswith(b"%PDF"))
            self.assertTrue((directory / "style.png").read_bytes().startswith(b"\x89PNG"))
            self.assertIn("<svg", (directory / "style.svg").read_text())
        finally:
            shutil.rmtree(directory)


class AxisStyleTests(unittest.TestCase):
    def setUp(self):
        self.style = helper()
        self.assertTrue(
            hasattr(self.style, "style_axes"), "explicit axis styling not implemented"
        )
        self.fig, self.ax = plt.subplots(dpi=144)
        self.ax.scatter([1, 2, 3], [2, 3, 4])
        self.ax.set(xlim=(0.5, 5.5), ylim=(0.5, 5.5))
        self.ax.set_xticks(range(7))
        self.ax.set_yticks(range(7))
        self.ax.set(xlim=(0.5, 5.5), ylim=(0.5, 5.5))

    def tearDown(self):
        plt.close("all")

    def assert_outward(self, ax, offset=4):
        for side, point, transform, dimension in (
            ("bottom", (2, 0), ax.get_xaxis_transform(), 1),
            ("left", (0, 2), ax.get_yaxis_transform(), 0),
        ):
            actual = ax.spines[side].get_transform().transform(point)
            reference = transform.transform(point)
            self.assertAlmostEqual(
                actual[dimension] - reference[dimension],
                -offset * self.fig.dpi / 72,
                places=7,
            )

    def test_scatter_uses_display_points_and_only_visible_major_ticks(self):
        # Hidden in-range endpoints must not extend the spine either.
        ticks = self.ax.xaxis.get_major_ticks()
        ticks[1].tick1line.set_visible(False)
        ticks[5].tick1line.set_visible(False)
        self.style.style_axes(self.ax, mode="scatter")
        self.fig.canvas.draw()
        self.assertEqual(self.ax.spines["bottom"].get_bounds(), (2, 4))
        self.assertEqual(self.ax.spines["left"].get_bounds(), (1, 5))
        self.assertFalse(self.ax.spines["top"].get_visible())
        self.assertFalse(self.ax.spines["right"].get_visible())
        self.assertEqual(self.ax.spines["left"].get_linewidth(), 0.8)
        self.assertEqual(self.ax.xaxis.get_major_ticks()[2].get_tickdir(), "out")
        self.assert_outward(self.ax)
        self.style.style_axes(self.ax, offset=6, linewidth=1.2)
        self.assert_outward(self.ax, offset=6)
        self.assertEqual(self.ax.spines["left"].get_linewidth(), 1.2)

    def test_nonnegative_bar_retains_zero_baseline(self):
        self.ax.clear()
        self.ax.bar([1, 2], [3, 5])
        self.ax.set(xlim=(0, 3), ylim=(0, 6))
        self.ax.set_xticks([1, 2])
        self.ax.set_yticks([0, 2, 4, 6, 8])
        self.ax.set_ylim(0, 6)
        self.style.style_axes(self.ax, mode="bar")
        self.fig.canvas.draw()
        self.assertEqual(self.ax.spines["bottom"].get_position(), ("data", 0))
        self.assertTrue(self.ax.spines["bottom"].get_visible())
        self.assertEqual(self.ax.spines["bottom"].get_bounds(), (0, 3))
        self.assertEqual(self.ax.spines["left"].get_bounds(), (0, 6))
        actual = self.ax.spines["bottom"].get_transform().transform((1, 0))
        self.assertAlmostEqual(actual[1], self.ax.transData.transform((1, 0))[1])
        self.assertEqual(self.ax.spines["left"].get_position(), ("outward", 4))

    def test_preserves_data_limits_scales_and_aspect(self):
        self.ax.set_aspect(1.25)
        line, = self.ax.plot([1, 2, 3], [3, 2, 1])
        offsets = self.ax.collections[0].get_offsets().copy()
        state = (self.ax.get_xlim(), self.ax.get_ylim(), self.ax.get_xscale(),
                 self.ax.get_yscale(), self.ax.get_aspect())
        self.style.style_axes(self.ax)
        self.fig.canvas.draw()
        self.assertEqual(state, (self.ax.get_xlim(), self.ax.get_ylim(),
                                self.ax.get_xscale(), self.ax.get_yscale(),
                                self.ax.get_aspect()))
        self.assertTrue((self.ax.collections[0].get_offsets() == offsets).all())
        self.assertEqual(list(line.get_xdata()), [1, 2, 3])
        self.assertEqual(list(line.get_ydata()), [3, 2, 1])

    def test_reversed_log_axes_keep_scale_limits_and_tick_bounds(self):
        self.ax.set(xscale="log", yscale="log", xlim=(100, 1), ylim=(1000, 1))
        self.ax.set_xticks([0.1, 1, 10, 100, 1000])
        self.ax.set_yticks([0.1, 1, 10, 100, 1000, 10000])
        # set_ticks can expand limits; restore the intended view before styling.
        self.ax.set(xlim=(100, 1), ylim=(1000, 1))
        self.style.style_axes(self.ax)
        self.fig.canvas.draw()
        self.assertEqual(self.ax.get_xlim(), (100, 1))
        self.assertEqual(self.ax.get_ylim(), (1000, 1))
        self.assertEqual(self.ax.get_xscale(), "log")
        self.assertEqual(self.ax.get_yscale(), "log")
        self.assertEqual(self.ax.spines["bottom"].get_bounds(), (1, 100))
        self.assertEqual(self.ax.spines["left"].get_bounds(), (1, 1000))
        self.assert_outward(self.ax)

    def test_image_and_colorbar_borders_untouched_without_explicit_call(self):
        image_ax = self.fig.add_axes((0.65, 0.65, 0.2, 0.2))
        image = image_ax.imshow([[1, 2], [3, 4]], extent=(0, 4, 0, 4))
        colorbar = self.fig.colorbar(image, ax=image_ax)
        borders = [*image_ax.spines.values(), *colorbar.ax.spines.values()]
        def border_state():
            return [(s.get_visible(), s.get_transform().get_matrix().tolist(),
                     s.get_path().vertices.tolist(), s.get_bounds(), s.get_linewidth())
                    for s in borders]

        before = border_state()
        with self.style.style_context():
            self.style.style_axes(self.ax)
        self.assertEqual(before, border_state())
        image_ax.set_xticks([0, 2, 4])
        image_ax.set_yticks([0, 2, 4])
        self.style.style_axes(image_ax)
        self.assertFalse(image_ax.spines["top"].get_visible())

    def test_invalid_parameters_and_unsupported_views_fail_before_mutation(self):
        before = [(s.get_visible(), s.get_position(), s.get_bounds())
                  for s in self.ax.spines.values()]
        for kwargs in ({"mode": "auto"}, {"offset": -1}, {"offset": float("nan")},
                       {"offset": True}, {"linewidth": 0}, {"linewidth": "thin"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.style.style_axes(self.ax, **kwargs)
        for kwargs in ({"text_size": 0}, {"text_size": float("inf")},
                       {"text_size": True}, {"font_family": " "}, {"axis_width": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.style.style_context(**kwargs)
        self.ax.set_xticks([])
        with self.assertRaisesRegex(ValueError, "major ticks"):
            self.style.style_axes(self.ax)
        self.assertEqual(before, [(s.get_visible(), s.get_position(), s.get_bounds())
                                  for s in self.ax.spines.values()])
        self.ax.set_xticks([1, 2, 3])
        self.ax.set(yscale="log", ylim=(1, 10))
        with self.assertRaisesRegex(ValueError, "zero baseline"):
            self.style.style_axes(self.ax, mode="bar")
        self.ax.set(yscale="linear", ylim=(1, 10))
        with self.assertRaisesRegex(ValueError, "zero baseline"):
            self.style.style_axes(self.ax, mode="bar")
        self.ax.set(xscale="symlog")
        with self.assertRaisesRegex(ValueError, "linear or log"):
            self.style.style_axes(self.ax)
        polar = self.fig.add_subplot(111, projection="polar")
        with self.assertRaisesRegex(ValueError, "Cartesian"):
            self.style.style_axes(polar)


if __name__ == "__main__":
    unittest.main()
