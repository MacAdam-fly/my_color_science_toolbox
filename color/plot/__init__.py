"""Plot helpers for colour-science visualisation."""

from __future__ import annotations

from .chromaticity import (
    D65_UPVP1976,
    D65_UV1960,
    D65_XY,
    chromaticity_background_image,
    load_cie1931_locus_upvp1976,
    load_cie1931_locus_uv1960,
    load_cie1931_locus_xy,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_chromaticity_background,
    plot_xy_chromaticity_background,
    plot_xy_points,
)
from .common import as_2d_points, as_rgb_rows, finish_figure, get_figure_axes
from .conversion import plot_conversion_graph, plot_conversion_path
from .rgb import plot_rgb_gamuts
from .spectra import (
    plot_multi_spectral_distribution,
    plot_spectral_distribution,
    style_spectral_axis,
)
from .swatches import preview_sRGB_from_XYZ, plot_swatch_grid, plot_swatch_strip
from .temperature import (
    daylight_locus_uv1960,
    duv_offset_grid_uv1960,
    planckian_locus_uv1960,
    plot_duv_offsets_uv1960,
    plot_mired_curve,
    plot_temperature_loci_uv1960,
)

__all__ = [
    "D65_UPVP1976",  # rounded D65 u'v'1976 whitepoint used for plotting
    "D65_UV1960",  # rounded D65 uv1960 whitepoint used for plotting
    "D65_XY",  # rounded D65 xy whitepoint used for plotting
    "as_2d_points",  # validate row-wise plotting points
    "as_rgb_rows",  # validate RGB rows for plotting
    "chromaticity_background_image",  # compute chromaticity background RGB image
    "daylight_locus_uv1960",  # compute CIE D daylight locus in CIE 1960 uv
    "duv_offset_grid_uv1960",  # compute CCT and Duv offset grid in CIE 1960 uv
    "finish_figure",  # apply final figure layout
    "get_figure_axes",  # create or reuse matplotlib axes
    "load_cie1931_locus_upvp1976",  # load CIE 1931 spectral locus u'v' coordinates
    "load_cie1931_locus_uv1960",  # load CIE 1931 spectral locus uv coordinates
    "load_cie1931_locus_xy",  # load CIE 1931 spectral locus xy coordinates
    "plot_chromaticity_background",  # plot a chromaticity background image
    "plot_cie1931_diagram",  # plot CIE 1931 xy chromaticity diagram
    "plot_cie1960_ucs_diagram",  # plot CIE 1960 uv chromaticity diagram
    "plot_cie1976_ucs_diagram",  # plot CIE 1976 u'v' chromaticity diagram
    "plot_xy_chromaticity_background",  # plot the CIE 1931 xy background
    "plot_xy_points",  # plot labelled xy chromaticity points
    "plot_conversion_graph",  # plot the registered colour-space conversion graph
    "plot_conversion_path",  # plot one conversion path
    "planckian_locus_uv1960",  # compute Planckian locus in CIE 1960 uv
    "plot_duv_offsets_uv1960",  # plot Duv offsets in CIE 1960 uv
    "plot_mired_curve",  # plot CCT to mired relationship
    "plot_rgb_gamuts",  # plot RGB colourspace primary triangles
    "plot_temperature_loci_uv1960",  # plot Planckian and daylight loci in uv
    "plot_multi_spectral_distribution",  # plot multi-channel spectral data
    "plot_spectral_distribution",  # plot single-channel spectral data
    "style_spectral_axis",  # apply common spectral axis styling
    "preview_sRGB_from_XYZ",  # clipped sRGB preview values from XYZ
    "plot_swatch_grid",  # plot a labelled sRGB swatch grid
    "plot_swatch_strip",  # plot a horizontal sRGB swatch strip
]
