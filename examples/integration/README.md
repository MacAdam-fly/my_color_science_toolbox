# Integration Examples

Examples in this folder connect multiple package layers together instead of
focusing on one module at a time.

## Scripts

| Script | Purpose |
| --- | --- |
| `example_01_long_colour_pipeline.py` | Full runnable pipeline covering data sources, spectral objects, colorimetry, spaces, adaptation, appearance, difference, gamut analysis, recovery, plotting and figure export. |

## Long Colour Pipeline

`example_01_long_colour_pipeline.py` is the runnable companion to the root
`readme.md` long-chain section.

It uses three inputs:

1. A generated three-peak LED emission spectrum.
2. An encoded sRGB signal: `[0.4, 0.5, 0.6]`.
3. A Macbeth ColorChecker `"Blue Sky"` reflectance patch under D65.

The example then runs:

```text
datasets / generators
-> spectra
-> colorimetry: XYZ, LMS, xy, relative Y, CCT+Duv, dominant wavelength
-> spaces: Lab, Luv, Oklab, CAM16-UCS
-> adaptation: D65 -> D50 for CAM16 viewing
-> appearance: CIECAM16 correlates
-> difference: CIEDE2000 against a second Macbeth patch
-> gamut: coarse sRGB gamut analysis
-> recovery: Blue Sky XYZ back to reflectance
-> plot/io: save original-vs-recovered reflectance figure
```

Run it directly:

```powershell
.\.venv\Scripts\python.exe examples\integration\example_01_long_colour_pipeline.py
```

The script writes:

```text
examples/integration/output/01_long_colour_pipeline_reflectance_recovery.png
```

Generated files under `examples/**/output/` are intentionally ignored by git.
