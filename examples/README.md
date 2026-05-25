# Examples

Minimal examples for the color package.

## Color Space Conversions

- `lab_luv_basic.py` — Lab/Luv round-trip via XYZ.
- `cam02_basic.py` — XYZ ↔ CAM02 (QMh) using a context.

## Database Examples (`database/`)

Usage examples for the `color.datasets` data loading module.

- `example_illuminants.py` — Load static CIE illuminants, generate blackbody and CIE D-series daylight SPDs, plot SPDs.
- `example_color_cards.py` — Load Macbeth ColorChecker and BCRA calibration tiles, print reflectance at specific wavelengths, plot spectral reflectance curves.
- `example_standard_observers.py` — Load CIE XYZ CMFs, CIE 2006 LMS cone fundamentals, CIE 2008 V(λ), prereceptoral filters, chromaticity coordinates, photopigments. Demonstrates category aliases (`"lms"`, `"vl"`, `"filter"`, `"xy"`, `"pigment"`).
- `example_gamut_data.py` — Load Pointer's real surface colour gamut, inspect chromaticity data.
- `example_color_systems.py` — Load Munsell renotation data, inspect CIELAB distributions.

Run any example:

```bash
python examples/database/example_illuminants.py
```

Each plotting example saves a PNG to `examples/database/`.

## Integration Examples (`integration/`)

- `example_01_long_colour_pipeline.py` — Generated LED spectrum and sRGB signal
  through XYZ/LMS, Luv, CAM02-UCS with D50 viewing white, explicit chromatic
  adaptation for Oklab, final Lab, and CIEDE2000.
