"""Tests for public plotting helpers."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from color.generators.leds import multi_led_spd
from color.plot import (
    as_2d_points,
    as_rgb_rows,
    chromaticity_background_image,
    get_figure_axes,
    load_cie1931_locus_upvp1976,
    load_cie1931_locus_uv1960,
    load_cie1931_locus_xy,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_conversion_graph,
    plot_conversion_path,
    plot_chromaticity_background,
    plot_multi_spectral_distribution,
    plot_rgb_gamuts,
    plot_spectral_distribution,
    plot_swatch_grid,
    plot_swatch_strip,
    plot_xy_chromaticity_background,
    plot_xy_points,
    preview_sRGB_from_XYZ,
)
from color.spectra import from_D65_illuminant, from_cie1931_xyz_cmfs, from_columns


def _close(fig) -> None:
    plt.close(fig)


def test_common_get_figure_axes_creates_axes() -> None:
    fig, ax = get_figure_axes(figsize=(3.0, 2.0))
    assert fig is ax.figure
    _close(fig)


def test_common_as_2d_points_and_rgb_rows() -> None:
    points = as_2d_points([0.1, 0.2], size=2, name="xy")
    assert points.shape == (1, 2)

    rgb = as_rgb_rows([[1.2, -0.1, 0.5]])
    assert rgb.shape == (1, 3)
    assert np.all(rgb >= 0.0)
    assert np.all(rgb <= 1.0)


def test_plot_spectral_distribution_returns_fig_ax() -> None:
    sd = from_D65_illuminant()
    fig, ax = plot_spectral_distribution(sd)
    assert fig is ax.figure
    assert len(ax.lines) == 1
    _close(fig)


def test_plot_multi_spectral_distribution_returns_fig_ax() -> None:
    cmfs = from_cie1931_xyz_cmfs()
    fig, ax = plot_multi_spectral_distribution(cmfs, labels=("X", "Y"))
    assert fig is ax.figure
    assert len(ax.lines) == 2
    _close(fig)


def test_plot_multi_spectral_distribution_rejects_missing_label() -> None:
    cmfs = from_cie1931_xyz_cmfs()
    with pytest.raises(ValueError):
        plot_multi_spectral_distribution(cmfs, labels=("missing",))


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
    plot_xy_points([[0.3127, 0.3290], [0.4, 0.3]], ax=ax, labels=("D65", "P"))
    assert fig is ax.figure
    assert len(ax.lines) >= 1
    assert len(ax.collections) >= 2
    _close(fig)


def test_plot_cie1931_diagram_with_background() -> None:
    fig, ax = plot_cie1931_diagram(show_background=True, background_samples=32)
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(ax.lines) >= 1
    _close(fig)


def test_plot_cie1960_ucs_diagram() -> None:
    fig, ax = plot_cie1960_ucs_diagram()
    assert fig is ax.figure
    assert len(ax.lines) >= 1
    assert len(ax.collections) >= 2
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


def test_plot_rgb_gamuts_resolves_common_colourspaces() -> None:
    fig, ax = plot_rgb_gamuts(("sRGB", "Display P3", "Rec.2020", "DCI-P3"))
    assert fig is ax.figure
    assert len(ax.lines) == 4
    _close(fig)


def test_conversion_plotting_is_reexported() -> None:
    fig, ax = plot_conversion_path("sRGB", "Lab")
    assert fig is ax.figure
    assert len([patch for patch in ax.patches if patch.get_gid() == "conversion_path_node"]) >= 1
    _close(fig)

    fig, ax = plot_conversion_graph()
    assert fig is ax.figure
    assert len([patch for patch in ax.patches if patch.get_gid() == "conversion_graph_node"]) >= 1
    _close(fig)


def test_plot_helpers_accept_generated_spectrum() -> None:
    raw = multi_led_spd()
    sd = from_columns(raw, y="spd", name="LED")
    fig, ax = plot_spectral_distribution(sd)
    assert fig is ax.figure
    assert ax.get_xlabel() == "Wavelength (nm)"
    _close(fig)
