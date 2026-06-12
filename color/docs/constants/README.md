# color.constants

`color.constants` is the authoritative home for important standard constants
shared across the project: whitepoint XYZ values, RGB display standard
matrices, LMS/XYZ observer matrices, and chromatic adaptation transforms.

Chinese API usage examples are available in [`API_GUIDE.md`](API_GUIDE.md).
Chinese design notes are available in [`README_DETAILS.md`](README_DETAILS.md).

## Scope

`constants` stores standard data. It does not execute conversions.

Use upper-level modules for behavior:

- `color.spaces` for colour-space conversion.
- `color.adaptation` for chromatic adaptation.
- `color.colorimetry` for spectral integration and chromaticity.
- `color.appearance` for colour appearance models.
- `color.gamut` for gamut computation.

## Public API

Whitepoint / illuminant XYZ constants:

- `A_XYZ`
- `C_XYZ`
- `D50_XYZ`
- `D55_XYZ`
- `D65_XYZ`
- `E_XYZ`

RGB display standard matrices:

- `SRGB_TO_XYZ`, `XYZ_TO_SRGB`
- `REC709_TO_XYZ`, `XYZ_TO_REC709`
- `REC2020_TO_XYZ`, `XYZ_TO_REC2020`
- `ADOBE_RGB_TO_XYZ`, `XYZ_TO_ADOBE_RGB`
- `DISPLAY_P3_TO_XYZ`, `XYZ_TO_DISPLAY_P3`
- `DCIP3_TO_XYZ`, `XYZ_TO_DCIP3`
- `NTSC_1953_TO_XYZ`, `XYZ_TO_NTSC_1953`

RGB standard definition tables:

- `RGB_COLOURSPACE_DEFINITIONS`
- `RGB_GAMUT_METADATA`
- `COMMON_GAMUTS`

CIE 2006 LMS/XYZ observer matrices:

- `LMS_2_DEGREE_TO_XYZ_2_DEGREE`
- `XYZ_2_DEGREE_TO_LMS_2_DEGREE`
- `LMS_10_DEGREE_TO_XYZ_10_DEGREE`
- `XYZ_10_DEGREE_TO_LMS_10_DEGREE`

Chromatic adaptation transform matrices:

- `CAT_VON_KRIES`
- `CAT_BRADFORD`
- `CAT_CAT02`
- `CAT_CAT16`
- `CHROMATIC_ADAPTATION_TRANSFORMS`

## Quick Start

```python
from color.constants import D50_XYZ, D65_XYZ, SRGB_TO_XYZ

print(D65_XYZ)

linear_rgb = [1.0, 1.0, 1.0]
XYZ = SRGB_TO_XYZ @ linear_rgb
```

Use constants as inputs to higher-level modules:

```python
from color.adaptation import chromatic_adaptation_XYZ
from color.constants import D50_XYZ, D65_XYZ

XYZ_D65 = chromatic_adaptation_XYZ(
    [50.0, 40.0, 30.0],
    source_white_XYZ=D50_XYZ,
    target_white_XYZ=D65_XYZ,
)
```

## Scale Convention

Whitepoints and RGB matrices use the project-wide `Y=100` XYZ scale.

```python
from color.constants import D65_XYZ, SRGB_TO_XYZ

white = SRGB_TO_XYZ @ [1.0, 1.0, 1.0]
# close to D65_XYZ
```

The RGB matrices are for **linear** RGB. Encoded RGB transfer functions are
handled by `color.spaces.rgb`, not by these constants.

## Files

| File | Responsibility |
| --- | --- |
| `illuminants_XYZ.py` | whitepoint / illuminant XYZ constants |
| `display_standards.py` | RGB display and imaging standard matrices |
| `standard_observer_matrices.py` | CIE 2006 LMS/XYZ observer matrices |
| `adaptation_matrices.py` | chromatic adaptation transform matrices |
