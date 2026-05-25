# color.plot

`color.plot` contains small matplotlib helpers for colour-science
visualisation. It is intentionally a plotting layer only: it does not perform
colour-science calculations beyond lightweight preview conversion for swatches.

For Chinese design notes, see [README_DETAILS.md](README_DETAILS.md).

## Public API

```python
from color.plot import (
    get_figure_axes,
    chromaticity_background_image,
    plot_spectral_distribution,
    plot_multi_spectral_distribution,
    style_spectral_axis,
    load_cie1931_locus_xy,
    load_cie1931_locus_uv1960,
    load_cie1931_locus_upvp1976,
    plot_xy_chromaticity_background,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_xy_points,
    preview_sRGB_from_XYZ,
    plot_swatch_strip,
    plot_swatch_grid,
    plot_rgb_gamuts,
    plot_conversion_path,
    plot_conversion_graph,
)
```

## Quick Start

```python
from color.plot import plot_spectral_distribution, plot_cie1931_diagram, plot_cie1960_ucs_diagram
from color.spectra import from_D65_illuminant

d65 = from_D65_illuminant()

fig, ax = plot_spectral_distribution(d65, ylabel="Relative SPD")
fig.savefig("d65.png", dpi=150)

fig, ax = plot_cie1931_diagram()
fig.savefig("cie1931_xy.png", dpi=150)

fig, ax = plot_cie1931_diagram(show_background=True)
fig.savefig("cie1931_xy_background.png", dpi=150)

fig, ax = plot_cie1960_ucs_diagram(show_background=True)
fig.savefig("cie1960_uv_background.png", dpi=150)
```

All plotting functions accept `ax=None` and return `(fig, ax)`.

`color.plot.common` also provides small plotting utilities such as
`get_figure_axes(...)`, `finish_figure(...)`, `as_2d_points(...)` and
`as_rgb_rows(...)`. These are plotting-layer helpers, not general scientific
array utilities.

## Preview Swatches

## Chromaticity Background

`plot_cie1931_diagram(show_background=True)` draws an approximate sRGB background
inside the CIE 1931 spectral locus. The background is a visual aid: RGB values
are normalised and clipped for display, so it is not a strict colour-management
result.

`plot_cie1960_ucs_diagram(...)` and `plot_cie1976_ucs_diagram(...)` draw the same CIE 1931
spectral locus in CIE 1960 UCS `uv` and CIE 1976 UCS `u'v'` coordinates. The
`uv1960` view is the natural plotting space for CCT and Duv visualisations;
`u'v'1976` is useful for Luv-related chromaticity diagrams.

Legacy names `plot_xy_locus(...)`, `plot_uv1960_locus(...)` and
`plot_upvp1976_locus(...)` remain available as compatibility aliases.

`preview_sRGB_from_XYZ(...)`, `plot_swatch_strip(...)` and
`plot_swatch_grid(...)` are visualisation helpers. They clip RGB values to
`[0, 1]` for display and should not be used as gamut-mapping or appearance
models.

## Conversion Plots

`plot_conversion_path(...)` and `plot_conversion_graph(...)` are re-exported
from `color.spaces.plotting`. The old `color.spaces.plotting` import path
remains valid.

## Examples

```powershell
.\.venv\Scripts\python.exe examples\plot\example_01_plot_overview.py
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest color\plot\tests -q --basetemp .pytest_tmp
```
