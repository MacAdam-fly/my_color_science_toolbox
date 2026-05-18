# colorimetry

`color.colorimetry` converts spectral object wrappers into colorimetric
responses. It is the computation layer above:

```text
color.datasets     static reference data
color.generators   formula-generated data
color.spectra      spectral object wrappers
color.colorimetry  spectral integration to XYZ / LMS
```

## Public Entrypoints

```python
from color.colorimetry import (
    emission_to_xyz,
    reflectance_to_xyz,
    emission_to_lms,
    reflectance_to_lms,
    XYZ_to_xyY,
    xyY_to_XYZ,
)
```

Use `emission_to_*` for self-luminous spectral data. Use `reflectance_to_*`
for object reflectance data under an illuminant.

XYZ and LMS use the same numerical integration core. The difference is the
three-channel response function passed in:

```text
XYZ -> CIE XYZ colour matching functions
LMS -> cone fundamentals
```

Chromaticity helpers keep the luminance component explicit:

```python
xyY = XYZ_to_xyY(XYZ)
XYZ = xyY_to_XYZ(xyY)
xy = XYZ_to_xy(XYZ)
```

`XYZ_to_xy(...)` intentionally returns only the chromaticity
coordinates and is not a reversible conversion by itself.

Some CVRL LMS cone fundamental tables contain blank long-wavelength S-cone
entries. `datasets` preserves those as `NaN`; when they are intended as zero
response for integration, fill them explicitly at the spectral-wrapper stage:

```python
fundamentals = from_dataset(
    "standard_observers.cone_fundamentals",
    "cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

## Examples

See `examples/colorimetry/` for end-to-end scripts covering:

- generated emission spectra to XYZ/LMS
- color-card reflectance to XYZ/LMS under D65
- generated vs static CIE Illuminant A XYZ comparison
- smoke checks across datasets, generators, spectra and colorimetry
