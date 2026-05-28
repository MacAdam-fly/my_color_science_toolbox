# Plot Examples

Examples for the low-level `color.plot` building blocks.

## Run

```powershell
.\.venv\Scripts\python.exe examples\plot\example_01_plot_overview.py
.\.venv\Scripts\python.exe examples\plot\example_02_cct_loci.py
.\.venv\Scripts\python.exe examples\plot\example_03_dominant_wavelength.py
.\.venv\Scripts\python.exe examples\plot\example_04_rgb_gamut_comparison.py
.\.venv\Scripts\python.exe examples\plot\example_05_component_gallery.py
.\.venv\Scripts\python.exe examples\plot\example_06_image_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\plot\example_07_plot_style_comparison.py
```

## Outputs

The overview example writes images to `examples/plot/output/`:

| File | Demonstrates |
| --- | --- |
| `01_lines.png` | Generic multi-line primitive |
| `01_points.png` | Generic multi-group point primitive |
| `01_cie1931_xy_comparison.png` | CIE 1931 xy diagram: no background, background, background with wavelength labels |
| `01_cie1960_uv_comparison.png` | CIE 1960 UCS uv diagram: no background, background, background with wavelength labels |
| `01_cie1976_upvp_comparison.png` | CIE 1976 UCS u'v' diagram: no background, background, background with wavelength labels |
| `01_chromaticity_points.png` | Chromaticity diagram with labelled points |
| `01_swatch_strip.png` | sRGB preview swatches |
| `02_cct_loci_composed.png` | CCT loci composed from a CIE 1960 diagram, lines and points |
| `03_dominant_wavelength_composed.png` | Dominant wavelength analysis composed from a CIE 1931 diagram, segments and labelled points |
| `04_rgb_gamut_comparison_composed.png` | RGB gamut triangles composed from a CIE 1931 diagram and polygon primitives |
| `05_swatch_grid_from_xyz.png` | `preview_sRGB_from_XYZ` and `plot_swatch_grid` |
| `05_image_component.png` | `plot_image` with an RGB image array |
| `05_bars_journal_style.png` | `plot_bars`, `colour_cycle` and `plot_style("journal")` |
| `05_axis_limits_and_annotations.png` | `set_axis_limits_from_data`, arrows, segments and labels |
| `06_srgb_to_rec2020_image_comparison.png` | sRGB image and Rec.2020 encoded RGB preview drawn with `plot_image` |
| `06_rec2020_encoded_preview.jpg` | Clipped encoded Rec.2020 values saved as an 8-bit preview |
| `07_plot_style_comparison.png` | Current matplotlib defaults compared with `journal_single`, `journal_double` and `presentation` style presets |

Examples 02-05 intentionally rebuild domain-specific figures from lower-level
pieces instead of relying on high-level `color.plot` helpers. Conversion graphs
remain in `color.spaces.plotting`, because they are driven by the colour-space
registry rather than generic plotting geometry.

The Rec.2020 image example compares encoded channel values for inspection. It
does not embed an ICC profile or perform colour-managed Rec.2020 display
rendering.
