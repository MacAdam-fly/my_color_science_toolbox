"""Tests for public plotting primitives and chromaticity helpers."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from color.plot import (
    available_palettes,
    available_styles,
    chromaticity_background_image,
    colour_cycle,
    get_figure_axes,
    get_3d_figure_axes,
    plot_chromaticity_background,
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_3d_lines,
    plot_3d_points,
    plot_3d_surface,
    plot_3d_wireframe,
    plot_arrows,
    plot_bars,
    plot_labels,
    plot_image,
    plot_lines,
    plot_locus_wavelength_labels,
    plot_points,
    plot_polygons,
    plot_segments,
    plot_swatch_grid,
    plot_swatch_strip,
    plot_style,
    preview_sRGB_from_XYZ,
    set_3d_axis_limits_from_data,
    set_axis_limits_from_data,
    set_plot_style,
    style_2d_axis,
    style_3d_axis,
    style_rcparams,
)
from color.plot.chromaticity import (
    load_cie1931_locus_upvp1976,
    load_cie1931_locus_uv1960,
    load_cie1931_locus_xy,
    plot_xy_chromaticity_background,
    plot_xy_points,
)
from color.plot.common import as_2d_points, as_rgb_rows


def _close(fig) -> None:
    plt.close(fig)


def test_common_get_figure_axes_creates_axes() -> None:
    fig, ax = get_figure_axes(figsize=(3.0, 2.0))
    assert fig is ax.figure
    _close(fig)


def test_common_get_3d_figure_axes_creates_axes() -> None:
    fig, ax = get_3d_figure_axes(figsize=(3.0, 2.0))
    assert fig is ax.figure
    assert ax.name == "3d"
    _close(fig)

    fig2, ax2 = plt.subplots()
    with pytest.raises(ValueError):
        get_3d_figure_axes(ax2)
    _close(fig2)


def test_common_as_2d_points_and_rgb_rows() -> None:
    points = as_2d_points([0.1, 0.2], size=2, name="xy")
    assert points.shape == (1, 2)

    rgb = as_rgb_rows([[1.2, -0.1, 0.5]])
    assert rgb.shape == (1, 3)
    assert np.all(rgb >= 0.0)
    assert np.all(rgb <= 1.0)


def test_style_2d_axis_applies_common_settings() -> None:
    fig, ax = plt.subplots()
    style_2d_axis(
        ax,
        title="Title",
        xlabel="x",
        ylabel="y",
        grid=True,
        equal_aspect=True,
    )
    assert ax.get_title() == "Title"
    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    assert ax.get_aspect() == 1.0
    _close(fig)


def test_style_3d_axis_applies_common_settings() -> None:
    fig, ax = get_3d_figure_axes()
    style_3d_axis(
        ax,
        title="Title",
        xlabel="a*",
        ylabel="b*",
        zlabel="L*",
        grid=True,
        equal_aspect=True,
        view=(25.0, -45.0),
    )
    assert ax.get_title() == "Title"
    assert ax.get_xlabel() == "a*"
    assert ax.get_ylabel() == "b*"
    assert ax.get_zlabel() == "L*"
    _close(fig)

    fig2, ax2 = plt.subplots()
    with pytest.raises(ValueError):
        style_3d_axis(ax2)
    _close(fig2)


def test_plot_lines_single_and_multiple_series() -> None:
    x = np.array([0.0, 1.0, 2.0])
    fig, ax = plot_lines((x, x**2), xlabel="x", ylabel="y")
    assert fig is ax.figure
    assert len(ax.lines) == 1
    _close(fig)

    fig, ax = plot_lines(
        [(x, x), (x, x**2)],
        labels=("linear", "square"),
        colors=("tab:blue", "tab:red"),
        linestyles=("-", "--"),
    )
    assert len(ax.lines) == 2
    assert ax.get_legend() is not None
    _close(fig)


def test_plot_lines_rejects_mismatched_lengths_and_label_lengths() -> None:
    with pytest.raises(ValueError):
        plot_lines((np.array([0.0, 1.0]), np.array([0.0])))
    with pytest.raises(ValueError):
        plot_lines([(np.array([0.0]), np.array([0.0]))], labels=("a", "b"))


def test_plot_points_single_and_multiple_groups() -> None:
    fig, ax = plot_points([[0.1, 0.2], [0.3, 0.4]], labels=("A", "B"), annotate=True)
    assert fig is ax.figure
    assert len(ax.collections) == 1
    assert len(ax.texts) == 2
    _close(fig)

    groups = (
        [[0.1, 0.2], [0.2, 0.3]],
        [[0.4, 0.5], [0.5, 0.6]],
    )
    fig, ax = plot_points(groups, labels=("group 1", "group 2"), colors=("tab:blue", "tab:red"))
    assert len(ax.collections) == 2
    assert ax.get_legend() is not None
    _close(fig)


def test_plot_points_rejects_invalid_shapes_and_label_lengths() -> None:
    with pytest.raises(ValueError):
        plot_points([[0.1, 0.2, 0.3]])
    with pytest.raises(ValueError):
        plot_points([[[0.1, 0.2]], [[0.3, 0.4]]], labels=("only one",))
    with pytest.raises(ValueError):
        plot_points([[0.1, 0.2], [0.3, 0.4]], labels=("only one",), annotate=True)


def test_plot_3d_points_single_and_multiple_groups() -> None:
    fig, ax = plot_3d_points([[0.1, 0.2, 0.3], [0.3, 0.4, 0.5]], labels=("group",))
    assert fig is ax.figure
    assert ax.name == "3d"
    assert len(ax.collections) == 1
    assert ax.get_legend() is not None
    _close(fig)

    groups = (
        [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]],
        [[0.4, 0.5, 0.6], [0.5, 0.6, 0.7]],
    )
    fig, ax = plot_3d_points(groups, labels=("group 1", "group 2"), colors=("tab:blue", "tab:red"))
    assert len(ax.collections) == 2
    _close(fig)


def test_plot_3d_points_rejects_invalid_shapes() -> None:
    with pytest.raises(ValueError):
        plot_3d_points([[0.1, 0.2]])
    with pytest.raises(ValueError):
        plot_3d_points([[[0.1, 0.2, 0.3]], [[0.4, 0.5, 0.6]]], labels=("only one",))


def test_plot_3d_lines_single_and_multiple_series() -> None:
    t = np.linspace(0.0, 1.0, 5)
    fig, ax = plot_3d_lines((t, t**2, t**3), xlabel="x", ylabel="y", zlabel="z")
    assert fig is ax.figure
    assert len(ax.lines) == 1
    _close(fig)

    fig, ax = plot_3d_lines(
        [(t, t, t), (t, t**2, t**3)],
        labels=("linear", "curve"),
        colors=("tab:blue", "tab:red"),
    )
    assert len(ax.lines) == 2
    assert ax.get_legend() is not None
    _close(fig)


def test_plot_3d_lines_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        plot_3d_lines((np.array([0.0, 1.0]), np.array([0.0]), np.array([0.0, 1.0])))


def test_plot_labels_adds_text_and_rejects_label_mismatch() -> None:
    fig, ax = plot_labels([[0.1, 0.2], [0.3, 0.4]], ("A", "B"))
    assert fig is ax.figure
    assert len(ax.texts) == 2
    _close(fig)

    with pytest.raises(ValueError):
        plot_labels([[0.1, 0.2], [0.3, 0.4]], ("A",))


def test_plot_segments_single_and_multiple_groups() -> None:
    fig, ax = plot_segments(
        [
            [[[0.0, 0.0], [1.0, 1.0]]],
            [[[0.0, 1.0], [1.0, 0.0]]],
        ],
        labels=("diag 1", "diag 2"),
        colors=("tab:blue", "tab:red"),
    )
    assert fig is ax.figure
    assert len(ax.lines) == 2
    assert ax.get_legend() is not None
    _close(fig)


def test_plot_segments_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        plot_segments([[[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]]])


def test_plot_polygons_single_and_multiple_groups() -> None:
    triangle = [[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]]
    square = [[2.0, 0.0], [3.0, 0.0], [3.0, 1.0], [2.0, 1.0]]
    fig, ax = plot_polygons(
        [triangle, square],
        labels=("triangle", "square"),
        edgecolors=("tab:blue", "tab:red"),
        fill=False,
    )
    assert fig is ax.figure
    assert len(ax.patches) == 2
    assert ax.get_legend() is not None
    _close(fig)


def test_plot_polygons_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        plot_polygons([[0.0, 0.0], [1.0, 1.0]])


def test_plot_arrows_and_shape_validation() -> None:
    fig, ax = plot_arrows([[0.0, 0.0], [1.0, 0.0]], [[0.5, 0.5], [1.5, 0.5]])
    assert fig is ax.figure
    assert len(ax.patches) == 2
    _close(fig)

    with pytest.raises(ValueError):
        plot_arrows([[0.0, 0.0], [1.0, 0.0]], [[0.5, 0.5], [1.5, 0.5], [2.0, 0.0]])


def test_plot_image_scalar_and_rgb() -> None:
    fig, ax = plot_image(np.arange(9).reshape(3, 3), colorbar=True)
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(fig.axes) == 2
    _close(fig)

    fig, ax = plot_image(np.ones((2, 3, 3)), show_ticks=False)
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(ax.get_xticks()) == 0
    assert len(ax.get_yticks()) == 0
    _close(fig)

    with pytest.raises(ValueError):
        plot_image(np.ones((2, 2, 2)))


def test_plot_3d_surface_and_wireframe() -> None:
    x = np.linspace(-1.0, 1.0, 6)
    y = np.linspace(-1.0, 1.0, 5)
    X, Y = np.meshgrid(x, y)
    Z = X**2 + Y**2

    fig, ax = plot_3d_surface(X, Y, Z, cmap="viridis", colorbar=True)
    assert fig is ax.figure
    assert ax.name == "3d"
    assert len(ax.collections) >= 1
    assert len(fig.axes) == 2
    _close(fig)

    fig, ax = plot_3d_wireframe(X, Y, Z, color="black")
    assert fig is ax.figure
    assert ax.name == "3d"
    assert len(ax.collections) >= 1
    _close(fig)

    with pytest.raises(ValueError):
        plot_3d_surface(X, Y, Z[:-1])


def test_plot_bars_single_and_grouped() -> None:
    fig, ax = plot_bars([1.0, 2.0, 3.0], labels=("A", "B", "C"), colors="tab:blue")
    assert fig is ax.figure
    assert len(ax.patches) == 3
    _close(fig)

    fig, ax = plot_bars(
        [[1.0, 2.0, 3.0], [1.5, 1.0, 2.5]],
        labels=("A", "B", "C"),
        group_labels=("first", "second"),
        colors=("tab:blue", "tab:orange"),
    )
    assert len(ax.patches) == 6
    assert ax.get_legend() is not None
    _close(fig)

    fig, ax = plot_bars([[1.0, 2.0]], labels=("A", "B"), orientation="horizontal")
    assert len(ax.patches) == 2
    _close(fig)

    with pytest.raises(ValueError):
        plot_bars([[1.0, 2.0]], labels=("A",))
    with pytest.raises(ValueError):
        plot_bars([1.0], orientation="diagonal")


def test_set_axis_limits_from_data() -> None:
    fig, ax = plt.subplots()
    set_axis_limits_from_data(ax, [[0.0, 0.0], [2.0, 4.0]], padding=0.1, equal_aspect=True)
    assert ax.get_xlim()[0] < 0.0
    assert ax.get_xlim()[1] > 2.0
    assert ax.get_ylim()[0] < 0.0
    assert ax.get_ylim()[1] > 4.0
    assert ax.get_aspect() == 1.0
    _close(fig)

    with pytest.raises(ValueError):
        set_axis_limits_from_data(ax, [])


def test_set_3d_axis_limits_from_data() -> None:
    fig, ax = get_3d_figure_axes()
    data = np.array([[0.0, 0.0, 0.0], [2.0, 4.0, 6.0]])
    set_3d_axis_limits_from_data(ax, data, padding=0.1, equal_aspect=True)
    assert ax.get_xlim()[0] < 0.0
    assert ax.get_xlim()[1] > 2.0
    assert ax.get_ylim()[0] < 0.0
    assert ax.get_ylim()[1] > 4.0
    assert ax.get_zlim()[0] < 0.0
    assert ax.get_zlim()[1] > 6.0
    _close(fig)

    with pytest.raises(ValueError):
        set_3d_axis_limits_from_data(ax, [])


def test_plot_style_helpers() -> None:
    first_colour = next(colour_cycle("journal"))
    assert isinstance(first_colour, str)

    journal_params = style_rcparams("journal")
    assert journal_params["axes.titlesize"] == 0.0
    assert journal_params["axes.titlepad"] == 0.0
    assert journal_params["axes.titleweight"] == "normal"
    assert journal_params is not style_rcparams("journal")

    presentation_params = style_rcparams("presentation")
    assert presentation_params["axes.titlesize"] > 0.0

    with plot_style():
        assert plt.rcParams["axes.titlesize"] == 0.0
        assert plt.rcParams["axes.titlepad"] == 0.0
        fig, ax = plot_lines(([0.0, 1.0], [0.0, 1.0]))
        assert fig is ax.figure
        _close(fig)

    with plot_style("journal_double"):
        fig, ax = plot_lines(([0.0, 1.0], [0.0, 1.0]))
        assert fig is ax.figure
        _close(fig)

    with plot_style("presentation"):
        fig, ax = plot_lines(([0.0, 1.0], [0.0, 1.0]))
        assert fig is ax.figure
        _close(fig)

    assert isinstance(next(colour_cycle("monochrome")), str)
    assert isinstance(next(colour_cycle("presentation")), str)
    assert available_styles() == (
        "journal",
        "journal_double",
        "presentation",
        "monochrome",
    )
    assert available_styles(include_aliases=True) == available_styles()
    assert available_palettes() == ("journal", "presentation", "monochrome")

    with plt.rc_context():
        set_plot_style("journal")

    scaled_params = style_rcparams("journal", font_scale=1.2, line_scale=1.3)
    assert scaled_params["font.size"] > journal_params["font.size"]
    assert scaled_params["lines.linewidth"] > journal_params["lines.linewidth"]

    grid_params = style_rcparams("journal", rc={"axes.grid": True})
    assert grid_params["axes.grid"] is True

    with pytest.raises(ValueError):
        next(colour_cycle("unknown"))
    with pytest.raises(ValueError):
        with plot_style("unknown"):
            pass
    for old_style in ("paper", "journal_compact", "journal_single", "bw", "slide"):
        with pytest.raises(ValueError):
            with plot_style(old_style):
                pass
    for old_palette in ("paper", "academic", "muted", "bw", "slide"):
        with pytest.raises(ValueError):
            next(colour_cycle(old_palette))


def test_load_cie1931_locus_xy_shape() -> None:
    xy = load_cie1931_locus_xy()
    assert xy.ndim == 2
    assert xy.shape[1] == 2
    assert xy.shape[0] > 100


def test_load_cie1931_locus_uv_shapes() -> None:
    uv = load_cie1931_locus_uv1960()
    upvp = load_cie1931_locus_upvp1976()
    assert uv.ndim == 2
    assert upvp.ndim == 2
    assert uv.shape[1] == 2
    assert upvp.shape[1] == 2
    assert uv.shape[0] > 100
    assert upvp.shape[0] > 100
    assert np.all(np.isfinite(uv))
    assert np.all(np.isfinite(upvp))


def test_chromaticity_background_image_shape_and_range() -> None:
    image = chromaticity_background_image(samples=32)
    assert image.shape == (32, 32, 3)
    assert np.all(image >= 0.0)
    assert np.all(image <= 1.0)

    uv_image = chromaticity_background_image(method="CIE 1960 UCS", samples=32)
    upvp_image = chromaticity_background_image(method="CIE 1976 UCS", samples=32)
    assert uv_image.shape == (32, 32, 3)
    assert upvp_image.shape == (32, 32, 3)
    assert np.all(uv_image >= 0.0)
    assert np.all(uv_image <= 1.0)
    assert np.all(upvp_image >= 0.0)
    assert np.all(upvp_image <= 1.0)


def test_plot_chromaticity_background_adds_image_and_clip_patch() -> None:
    fig, ax = plot_chromaticity_background(samples=32)
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len([patch for patch in ax.patches if patch.get_gid() == "chromaticity_background_clip"]) == 1
    _close(fig)


def test_plot_xy_chromaticity_background() -> None:
    fig, ax = plot_xy_chromaticity_background(samples=32)
    assert fig is ax.figure
    assert len(ax.images) == 1
    _close(fig)


def test_plot_cie1931_diagram_and_points() -> None:
    fig, ax = plot_cie1931_diagram()
    plot_chromaticity_points([[0.3127, 0.3290], [0.4, 0.3]], ax=ax, labels=("D65", "P"))
    assert fig is ax.figure
    assert len(ax.lines) >= 1
    assert len(ax.collections) >= 2
    assert len(ax.texts) == 2
    _close(fig)


def test_plot_xy_points_compatibility_wrapper() -> None:
    fig, ax = plot_xy_points([[0.3127, 0.3290]], labels=("D65",))
    assert fig is ax.figure
    assert len(ax.collections) == 1
    _close(fig)


def test_plot_cie1931_diagram_with_background() -> None:
    fig, ax = plot_cie1931_diagram(show_background=True, background_samples=32)
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(ax.lines) >= 1
    _close(fig)


def test_plot_cie1931_diagram_with_wavelength_labels() -> None:
    fig, ax = plot_cie1931_diagram(
        show_wavelength_labels=True,
        wavelength_label_interval=100,
        wavelength_label_range=(400.0, 700.0),
    )
    assert fig is ax.figure
    assert len(ax.texts) >= 3
    _close(fig)


def test_plot_locus_wavelength_labels_validation() -> None:
    fig, ax = plt.subplots()
    wavelengths = np.array([400.0, 420.0, 440.0])
    coordinates = np.array([[0.1, 0.2], [0.2, 0.3], [0.3, 0.2]])
    plot_locus_wavelength_labels(wavelengths, coordinates, ax=ax, interval=20)
    assert len(ax.texts) == 3
    _close(fig)

    with pytest.raises(ValueError):
        plot_locus_wavelength_labels(wavelengths, coordinates[:2])
    with pytest.raises(ValueError):
        plot_locus_wavelength_labels(wavelengths, coordinates, interval=0)


def test_plot_cie1960_ucs_diagram() -> None:
    fig, ax = plot_cie1960_ucs_diagram(show_wavelength_labels=True, wavelength_label_interval=100)
    assert fig is ax.figure
    assert len(ax.lines) >= 1
    assert len(ax.collections) >= 2
    assert len(ax.texts) >= 3
    _close(fig)


def test_plot_cie1976_ucs_diagram() -> None:
    fig, ax = plot_cie1976_ucs_diagram()
    assert fig is ax.figure
    assert len(ax.lines) >= 1
    assert len(ax.collections) >= 2
    _close(fig)


def test_plot_uv_locus_with_background_and_without_whitepoint() -> None:
    fig, ax = plot_cie1960_ucs_diagram(
        whitepoint_uv=None,
        show_background=True,
        background_samples=32,
    )
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(ax.lines) >= 1
    assert len(ax.collections) == 1
    _close(fig)

    fig, ax = plot_cie1976_ucs_diagram(
        whitepoint_upvp=None,
        show_background=True,
        background_samples=32,
    )
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(ax.lines) >= 1
    assert len(ax.collections) == 1
    _close(fig)


def test_plot_uv_locus_rejects_invalid_whitepoint_shape() -> None:
    with pytest.raises(ValueError):
        plot_cie1960_ucs_diagram(whitepoint_uv=[0.1, 0.2, 0.3])
    with pytest.raises(ValueError):
        plot_cie1976_ucs_diagram(whitepoint_upvp=[0.1])


def test_preview_srgb_from_XYZ_clips_to_display_range() -> None:
    rgb = preview_sRGB_from_XYZ([[95.047, 100.0, 108.883], [200.0, 100.0, 50.0]])
    assert rgb.shape == (2, 3)
    assert np.all(rgb >= 0.0)
    assert np.all(rgb <= 1.0)


def test_plot_swatch_strip_adds_image() -> None:
    fig, ax = plot_swatch_strip([[1, 0, 0], [0, 1, 0]], labels=("R", "G"))
    assert fig is ax.figure
    assert len(ax.images) == 1
    _close(fig)


def test_plot_swatch_grid_adds_patches() -> None:
    fig, ax = plot_swatch_grid(
        [
            ("row 1", [[1, 0, 0], [0, 1, 0]]),
            ("row 2", [[0, 0, 1], [1, 1, 1]]),
        ]
    )
    assert fig is ax.figure
    assert len(ax.patches) == 4
    _close(fig)
