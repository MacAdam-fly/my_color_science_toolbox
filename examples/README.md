# Examples

Minimal examples for the color package.

## Color Space Conversions

- `lab_luv_basic.py` — Lab/Luv round-trip via XYZ.
- `cam02_basic.py` — XYZ ↔ CAM02 (QMh) using a context.

## Database Examples (`database/`)

Usage examples for the `color.datasets` data loading module.

- `example_illuminants.py` — Load CIE illuminants, compute blackbody radiation at arbitrary temperatures, generate CIE D-series daylight at arbitrary CCTs, plot SPDs.
- `example_color_cards.py` — Load Macbeth ColorChecker and BCRA calibration tiles, print reflectance at specific wavelengths, plot spectral reflectance curves.
- `example_standard_observers.py` — Load CIE XYZ CMFs, CIE 2006 LMS cone fundamentals, CIE 2008 V(λ), prereceptoral filters, chromaticity coordinates, photopigments. Demonstrates category aliases (`"lms"`, `"vl"`, `"filter"`, `"xy"`, `"pigment"`).
- `example_gamut_data.py` — Load Pointer's real surface colour gamut, inspect chromaticity data.
- `example_color_systems.py` — Load Munsell renotation data, inspect CIELAB distributions.

Run any example:

```bash
python examples/database/example_illuminants.py
```

Each plotting example saves a PNG to `examples/database/`.
