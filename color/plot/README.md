# color.plot

`color.plot` contains low-level matplotlib building blocks for colour-science
visualisation. It draws existing data; it does not perform spectral integration,
colour-space routing, chromatic adaptation, gamut mapping, or appearance
modelling.

For Chinese design notes, see [README_DETAILS.md](README_DETAILS.md).

## Public API

```python
from color.plot import (
    get_figure_axes,
    finish_figure,
    plot_lines,
    plot_points,
    plot_segments,
    plot_labels,
    plot_polygons,
    plot_arrows,
    plot_image,
    plot_bars,
    set_axis_limits_from_data,
    style_2d_axis,
    plot_3d_points,
    plot_3d_lines,
    plot_3d_surface,
    plot_3d_wireframe,
    set_3d_axis_limits_from_data,
    style_3d_axis,
    colour_cycle,
    palette,
    available_styles,
    available_palettes,
    style_rcparams,
    plot_style,
    set_plot_style,
    panel_label,
    add_panel_labels,
    available_cjk_fonts,
    use_cjk_font,
    chromaticity_background_image,
    plot_chromaticity_background,
    plot_locus_wavelength_labels,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_chromaticity_points,
    preview_sRGB_from_XYZ,
    plot_swatch_strip,
    plot_swatch_grid,
)
```

## Quick Start

```python
import numpy as np
from color.plot import plot_cie1931_diagram, plot_lines, plot_points

x = np.linspace(0, 1, 100)
fig, ax = plot_lines((x, x ** 2), xlabel="x", ylabel="y")

fig, ax = plot_points([[0.2, 0.3], [0.4, 0.5]], labels=["A", "B"], annotate=True)

fig, ax = plot_cie1931_diagram(show_background=True)
fig, ax = plot_cie1931_diagram(show_wavelength_labels=True)
fig, ax = plot_cie1931_diagram()

L = np.linspace(0, 100, 32)
h = np.linspace(0, 2 * np.pi, 64)
H, LL = np.meshgrid(h, L)
C = 60 * np.sin(np.pi * LL / 100)
fig, ax = plot_3d_surface(C * np.cos(H), C * np.sin(H), LL, xlabel="a*", ylabel="b*", zlabel="L*")
```

All plotting functions accept `ax=None` and return `(fig, ax)`.

## Design Boundary

`color.plot` exposes primitives:

- 2D lines and points.
- 2D segments, labels, polygons, arrows and data-driven axis limits.
- 3D points, lines, surfaces, wireframes and data-driven 3D axis limits.
- Scalar/RGB images and grouped bars.
- Local or global plotting style helpers for publication-oriented figures. The built-in presets cover compact journal figures, wide multi-panel layouts, poster/presentation output, notebooks, and dark-background plots.
- CIE 1931 xy, CIE 1960 uv, and CIE 1976 u'v' chromaticity diagrams.
- Optional wavelength labels along the CIE spectral locus, using diagram-specific default labels inspired by `colour.plotting`.
- Approximate sRGB preview swatches.
- Small axes and input helpers.

Domain-specific figures should be composed from these primitives:

- Spectral curves are line plots.
- Colour solids are 3D surfaces or wireframes.
- Temperature loci are chromaticity diagrams plus lines and points.
- RGB gamuts are chromaticity diagrams plus polygons and primary points.
- Conversion path and graph plotting lives in `color.spaces.plotting`.

The chromaticity background is a visual aid. RGB values are normalised and
clipped for display, so the background is not a strict colour-management result.
Chromaticity diagrams do not set a title by default. For journal figures, use
panel labels and captions instead of axes titles. The `journal` presets suppress
Matplotlib axes titles by default, so `ax.set_title(...)` will not visibly affect
the final figure unless you explicitly override the title rcParams.

Use `plot_style("journal")` as a context manager when you want a compact
journal-friendly figure without permanently changing matplotlib settings.
`journal` is the default and maps to the single-column preset. Use
`plot_style("journal_double")` for wide or multi-panel figures, and use
`set_plot_style("journal")` only when you intentionally want to update global
`rcParams`.

Use `style_rcparams("journal")` when you need a copy of the style dictionary for
inspection or integration with external plotting code. The raw
`PLOT_STYLE_PRESETS` mapping remains available from `color.plot.style` for
compatibility, but it is not part of the top-level `color.plot` API.

The journal presets are not official journal templates. They follow common
publisher guidance such as Nature's single/double-column figure sizing and final
text-size recommendations, and IEEE's 3.5 inch / 7.16 inch column widths and
300 dpi minimum guidance for colour or greyscale raster graphics.

## Examples

```powershell
.\.venv\Scripts\python.exe examples\plot\example_01_plot_overview.py
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest color\plot\tests -q --basetemp .pytest_tmp
```
