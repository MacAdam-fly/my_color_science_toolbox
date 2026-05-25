# Plot Examples

Examples for `color.plot`.

## Run

```powershell
.\.venv\Scripts\python.exe examples\plot\example_01_plot_overview.py
.\.venv\Scripts\python.exe examples\plot\example_02_temperature_visualization.py
```

## Outputs

The overview example focuses on chromaticity diagrams and writes images to
`examples/plot/output/`:

| File | Demonstrates |
| --- | --- |
| `01_cie1931_xy_locus.png` | CIE 1931 xy spectral locus without background |
| `01_cie1931_xy_locus_background.png` | CIE 1931 xy spectral locus with approximate sRGB background |
| `01_cie1960_uv_locus.png` | CIE 1960 UCS uv spectral locus without background |
| `01_cie1960_uv_locus_background.png` | CIE 1960 UCS uv spectral locus with approximate sRGB background |
| `01_cie1976_upvp_locus.png` | CIE 1976 UCS u'v' spectral locus without background |
| `01_cie1976_upvp_locus_background.png` | CIE 1976 UCS u'v' spectral locus with approximate sRGB background |
| `02_temperature_loci_uv1960.png` | Planckian and CIE D daylight loci in CIE 1960 uv |
| `02_duv_offsets_uv1960.png` | Duv offsets around the Planckian locus |
| `02_mired_curve.png` | CCT and mired relationship |
