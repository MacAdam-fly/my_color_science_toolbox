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
    emission_to_XYZ,
    reflectance_to_XYZ,
    emission_to_LMS,
    reflectance_to_LMS,
    Y_to_Lstar,
    Lstar_to_Y,
    photopic_luminous_efficiency_function,
    scotopic_luminous_efficiency_function,
    photopic_luminous_flux,
    scotopic_luminous_flux,
    photopic_luminous_efficiency,
    scotopic_luminous_efficiency,
    photopic_luminous_efficacy,
    scotopic_luminous_efficacy,
    luminous_flux,
    luminous_efficiency,
    luminous_efficacy,
    XYZ_to_xyY,
    xyY_to_XYZ,
)
```

Use `emission_to_*` for self-luminous spectral data. Use `reflectance_to_*` for
object reflectance data under an illuminant:

```python
XYZ = emission_to_XYZ(spd)
XYZ = reflectance_to_XYZ(reflectance)
LMS = emission_to_LMS(spd)
LMS = reflectance_to_LMS(reflectance)
```

The default calculation conditions are intentionally visible in the function
signatures:

```python
emission_to_XYZ(emission, *, cmfs="cie1931_xyz_1nm")
reflectance_to_XYZ(reflectance, *, illuminant="D65", cmfs="cie1931_xyz_1nm")
emission_to_LMS(
    emission,
    *,
    fundamentals="cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
reflectance_to_LMS(
    reflectance,
    *,
    illuminant="D65",
    fundamentals="cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

`cmfs` is loaded from `standard_observers.cmfs`, `fundamentals` is loaded from
`standard_observers.cone_fundamentals`, and `illuminant` is loaded from
`illuminants`. Pass preloaded spectral objects when you need a custom observer,
illuminant, shape or NaN policy.

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

Lightness helpers are available for CIE 1976 `Y <-> L*`:

```python
Lstar = Y_to_Lstar(Y, Y_n=100.0)
Y = Lstar_to_Y(Lstar, Y_n=100.0)
```

These functions operate on the relative luminance component `Y`, not on an
absolute luminance unit model such as `cd/m^2`.

Photometric helpers are also available:

```python
V = photopic_luminous_efficiency_function()
V_prime = scotopic_luminous_efficiency_function()
flux = photopic_luminous_flux(spd)
efficiency = photopic_luminous_efficiency(spd)
efficacy = photopic_luminous_efficacy(spd)
```

The default photopic function is `vl1924_1nm`, matching the conventional
`K_m = 683 lm/W` constant. The default scotopic function is `scotopic_v_1nm`,
paired with `K'_m = 1700 lm/W`.

Use the `photopic_*` and `scotopic_*` wrappers for the common safe path, so the
luminous efficiency function and `K_m` stay matched automatically. The generic
`luminous_flux`, `luminous_efficiency` and `luminous_efficacy` functions remain
available when you explicitly want to pass a custom LEF and constant.

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
- photopic and scotopic LEFs with luminous efficacy comparison
- smoke checks across datasets, generators, spectra and colorimetry
