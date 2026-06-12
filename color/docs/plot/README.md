# color.plot

`color.plot` provides low-level Matplotlib building blocks for colour-science
visualisation. It draws existing data; it does not perform spectral integration,
colour-space routing, chromatic adaptation, gamut mapping, appearance modelling,
or file export.

- For the Chinese API guide, see [API_GUIDE.md](API_GUIDE.md).
- For Chinese design notes, see [README_DETAILS.md](README_DETAILS.md).
- For figure export, use `color.io.save_figure(...)`.

## Public API

```python
from color.plot import (
    finish_figure,
    get_figure_axes,
    chromaticity_background_image,
    plot_chromaticity_background,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_chromaticity_points,
    plot_locus_wavelength_labels,
    add_panel_labels,
    panel_label,
    available_cjk_fonts,
    use_cjk_font,
    available_palettes,
    available_styles,
    cm_to_inches,
    mm_to_inches,
    colour_cycle,
    despine,
    palette,
    plot_style,
    set_plot_style,
    style_rcparams,
    plot_arrows,
    plot_bars,
    plot_image,
    plot_lines,
    plot_labels,
    plot_points,
    plot_polygons,
    plot_segments,
    set_axis_limits_from_data,
    style_2d_axis,
    get_3d_figure_axes,
    plot_3d_lines,
    plot_3d_points,
    plot_3d_surface,
    plot_3d_wireframe,
    set_3d_axis_limits_from_data,
    style_3d_axis,
    preview_sRGB_from_XYZ,
    plot_swatch_grid,
    plot_swatch_strip,
)
```

## Quick Start

```python
import numpy as np
from color.plot import plot_cie1931_diagram, plot_lines, plot_style

x = np.linspace(380, 780, 200)
y = np.exp(-0.5 * ((x - 560) / 35) ** 2)

with plot_style("journal"):
    fig, ax = plot_lines((x, y), xlabel="Wavelength (nm)", ylabel="Value")
```

```python
from color.plot import plot_chromaticity_points, plot_cie1931_diagram

fig, ax = plot_cie1931_diagram(show_background=True)
plot_chromaticity_points([[0.3127, 0.3290]], ax=ax, labels=("D65",))
```

```python
import numpy as np
from color.plot import plot_3d_surface, plot_3d_wireframe

L = np.linspace(0, 100, 32)
h = np.linspace(0, 2 * np.pi, 64)
H, LL = np.meshgrid(h, L)
C = 60 * np.sin(np.pi * LL / 100)

fig, ax = plot_3d_surface(C * np.cos(H), C * np.sin(H), LL, alpha=0.35)
plot_3d_wireframe(C * np.cos(H), C * np.sin(H), LL, ax=ax, color="0.25")
```

All plotting functions accept `ax=None` and return `(fig, ax)` unless documented
otherwise.

## Design Boundary

`color.plot` exposes primitives:

- 2D lines, points, segments, labels, polygons, arrows, images and bars.
- 3D points, lines, surfaces and wireframes.
- CIE 1931 xy, CIE 1960 uv and CIE 1976 u'v' chromaticity diagrams.
- Journal-oriented plotting styles, palettes, CJK font helpers and panel labels.
- Approximate sRGB preview swatches.

Domain-specific figures should be composed from these primitives. For example,
spectral curves are line plots, temperature loci are chromaticity diagrams plus
lines and points, and RGB gamuts are chromaticity diagrams plus polygons.

Journal presets suppress Matplotlib axes titles by default. Use panel labels and
captions for publication figures; explicitly override title rcParams only when a
title is intentional.

The chromaticity background is a visual aid. RGB values are normalised and
clipped for display, so the background is not a strict colour-management result.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest color\plot\tests -q --basetemp .pytest_tmp
```
