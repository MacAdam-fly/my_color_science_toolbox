"""Plot helpers for colour-science visualisation."""

from __future__ import annotations

from .chromaticity import (
    chromaticity_background_image,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_chromaticity_points,
    plot_chromaticity_background,
    plot_locus_wavelength_labels,
)
from .annotations import (
    add_panel_labels,
    panel_label,
)
from .common import finish_figure, get_figure_axes
from .fonts import available_cjk_fonts, use_cjk_font
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
from .style import (
    available_palettes,
    available_styles,
    colour_cycle,
    cm_to_inches,
    despine,
    mm_to_inches,
    palette,
    plot_style,
    set_plot_style,
    style_rcparams,
)
from .swatches import preview_sRGB_from_XYZ, plot_swatch_grid, plot_swatch_strip

__all__: list[str] = []

__all__ += [
    "finish_figure",  # apply final figure layout
    "get_figure_axes",  # create or reuse matplotlib axes
]

__all__ += [
    "chromaticity_background_image",  # compute chromaticity background RGB image
    "plot_chromaticity_background",  # plot a chromaticity background image
    "plot_cie1931_diagram",  # plot CIE 1931 xy chromaticity diagram
    "plot_cie1960_ucs_diagram",  # plot CIE 1960 uv chromaticity diagram
    "plot_cie1976_ucs_diagram",  # plot CIE 1976 u'v' chromaticity diagram
    "plot_chromaticity_points",  # plot labelled chromaticity points
    "plot_locus_wavelength_labels",  # label wavelengths along a spectral locus
]

__all__ += [
    "add_panel_labels",  # add journal-style panel labels to axes
    "panel_label",  # add a journal-style panel label to one axes

    "available_cjk_fonts",  # list installed CJK-capable plotting font candidates
    "use_cjk_font",  # prioritise CJK fonts in the active matplotlib session

    "available_palettes",  # list supported plotting palettes
    "available_styles",  # list supported plotting styles

    "cm_to_inches",  # convert centimetres to inches
    "mm_to_inches",  # convert millimetres to inches

    "colour_cycle",  # return an infinite cycle of plotting colours
    "despine",  # hide selected axes spines
    "palette",  # return a finite plotting colour palette

    "plot_style",  # temporarily apply a plotting style
    "set_plot_style",  # apply a plotting style to global matplotlib rcParams
    "style_rcparams",  # return a copy of rcParams for a plotting style
]

__all__ += [
    "plot_arrows",  # plot one or more two-dimensional arrows
    "plot_bars",  # plot one or more groups of bars
    "plot_image",  # plot a scalar image or RGB(A) image
    "plot_lines",  # plot one or more two-dimensional line series
    "plot_labels",  # add text labels to two-dimensional points
    "plot_points",  # plot one or more two-dimensional point groups
    "plot_polygons",  # plot one or more two-dimensional polygons
    "plot_segments",  # plot one or more two-dimensional line-segment groups
    "set_axis_limits_from_data",  # set axis limits from finite two-dimensional data
    "style_2d_axis",  # apply common two-dimensional axes styling
]

__all__ += [
    "get_3d_figure_axes",  # create or reuse matplotlib 3D axes
    "plot_3d_lines",  # plot one or more three-dimensional line series
    "plot_3d_points",  # plot one or more three-dimensional point groups
    "plot_3d_surface",  # plot a three-dimensional surface grid
    "plot_3d_wireframe",  # plot a three-dimensional wireframe grid
    "set_3d_axis_limits_from_data",  # set axis limits from finite three-dimensional data
    "style_3d_axis",  # apply common three-dimensional axes styling
]

__all__ += [
    "preview_sRGB_from_XYZ",  # clipped sRGB preview values from XYZ
    "plot_swatch_grid",  # plot a labelled sRGB swatch grid
    "plot_swatch_strip",  # plot a horizontal sRGB swatch strip
]
