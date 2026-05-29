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
    plot_chromaticity_points,
    plot_chromaticity_background,
    plot_locus_wavelength_labels,
    plot_xy_chromaticity_background,
    plot_xy_points,
)
from .common import as_2d_points, as_rgb_rows, finish_figure, get_figure_axes
from .primitives import (
    plot_arrows,
    plot_bars,
    plot_image,
    plot_labels,
    plot_lines,
    plot_points,
    plot_polygons,
    plot_segments,
    set_axis_limits_from_data,
    style_2d_axis,
)
from .primitives3d import (
    get_3d_figure_axes,
    plot_3d_lines,
    plot_3d_points,
    plot_3d_surface,
    plot_3d_wireframe,
    set_3d_axis_limits_from_data,
    style_3d_axis,
)
from .style import PLOT_STYLE_PRESETS, colour_cycle, plot_style, set_plot_style
from .swatches import preview_sRGB_from_XYZ, plot_swatch_grid, plot_swatch_strip

__all__ = [
    "D65_UPVP1976",  # rounded D65 u'v'1976 whitepoint used for plotting
    "D65_UV1960",  # rounded D65 uv1960 whitepoint used for plotting
    "D65_XY",  # rounded D65 xy whitepoint used for plotting
    "as_2d_points",  # validate row-wise plotting points
    "as_rgb_rows",  # validate RGB rows for plotting
    "chromaticity_background_image",  # compute chromaticity background RGB image
    "finish_figure",  # apply final figure layout
    "get_3d_figure_axes",  # create or reuse matplotlib 3D axes
    "get_figure_axes",  # create or reuse matplotlib axes
    "load_cie1931_locus_upvp1976",  # load CIE 1931 spectral locus u'v' coordinates
    "load_cie1931_locus_uv1960",  # load CIE 1931 spectral locus uv coordinates
    "load_cie1931_locus_xy",  # load CIE 1931 spectral locus xy coordinates
    "PLOT_STYLE_PRESETS",  # named matplotlib style presets for plotting
    "colour_cycle",  # return an infinite cycle of plotting colours
    "plot_chromaticity_background",  # plot a chromaticity background image
    "plot_cie1931_diagram",  # plot CIE 1931 xy chromaticity diagram
    "plot_cie1960_ucs_diagram",  # plot CIE 1960 uv chromaticity diagram
    "plot_cie1976_ucs_diagram",  # plot CIE 1976 u'v' chromaticity diagram
    "plot_chromaticity_points",  # plot labelled chromaticity points
    "plot_locus_wavelength_labels",  # label wavelengths along a spectral locus
    "plot_xy_chromaticity_background",  # plot the CIE 1931 xy background
    "plot_xy_points",  # compatibility wrapper for xy chromaticity points
    "plot_3d_lines",  # plot one or more three-dimensional line series
    "plot_3d_points",  # plot one or more three-dimensional point groups
    "plot_3d_surface",  # plot a three-dimensional surface grid
    "plot_3d_wireframe",  # plot a three-dimensional wireframe grid
    "plot_arrows",  # plot one or more two-dimensional arrows
    "plot_bars",  # plot one or more groups of bars
    "plot_image",  # plot a scalar image or RGB(A) image
    "plot_lines",  # plot one or more two-dimensional line series
    "plot_labels",  # add text labels to two-dimensional points
    "plot_points",  # plot one or more two-dimensional point groups
    "plot_polygons",  # plot one or more two-dimensional polygons
    "plot_segments",  # plot one or more two-dimensional line-segment groups
    "plot_style",  # temporarily apply a plotting style
    "set_3d_axis_limits_from_data",  # set axis limits from finite three-dimensional data
    "set_axis_limits_from_data",  # set axis limits from finite two-dimensional data
    "set_plot_style",  # apply a plotting style to global matplotlib rcParams
    "style_2d_axis",  # apply common two-dimensional axes styling
    "style_3d_axis",  # apply common three-dimensional axes styling
    "preview_sRGB_from_XYZ",  # clipped sRGB preview values from XYZ
    "plot_swatch_grid",  # plot a labelled sRGB swatch grid
    "plot_swatch_strip",  # plot a horizontal sRGB swatch strip
]
