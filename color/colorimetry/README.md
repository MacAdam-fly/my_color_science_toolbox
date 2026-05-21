# colorimetry

`color.colorimetry` converts spectral object wrappers into colorimetric
responses. It is the computation layer above:

中文详细说明见 [`README_DETAILS.md`](README_DETAILS.md)。

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
    LMS_to_XYZ,
    XYZ_to_LMS,
    ChromaticityAnalysis,
    analyze_chromaticity,
    is_inside_chromaticity_locus,
    dominant_wavelength,
    complementary_wavelength,
    excitation_purity,
    colorimetric_purity,
    xy_from_dominant_wavelength_pe,
    xy_from_dominant_wavelength_pc,
    CCT_to_mired,
    mired_to_CCT,
    xy_to_CCT_McCamy1992,
    CCT_to_xy_CIE_D,
    xy_to_CCT,
    CCT_to_xy,
    xy_to_uv1960,
    XYZ_to_uv1960,
    uv1960_to_xy,
    uv_to_CCT_Robertson1968,
    CCT_to_uv_Robertson1968,
    TemperatureAnalysis,
    analyze_temperature,
    uv_to_CCT_Ohno2013,
    CCT_to_uv_Ohno2013,
    planckian_table_Ohno2013,
    uv_to_CCT,
    CCT_to_uv,
    xy_to_CCT_Duv,
    CCT_Duv_to_xy,
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

Direct CIE 2006 LMS and XYZ matrix transformations are available after values
have already been computed:

```python
XYZ = LMS_to_XYZ(LMS, observer=2)
LMS = XYZ_to_LMS(XYZ, observer=2)
```

Use `observer=2` or `observer=10` to select the matching CIE 2006 observer
matrix.

The CIE 2006 LMS/XYZ matrix constants live in
`color.constants.standard_observer_matrices`.

Chromaticity helpers keep the luminance component explicit:

```python
xyY = XYZ_to_xyY(XYZ)
XYZ = xyY_to_XYZ(xyY)
xy = XYZ_to_xy(XYZ)
```

`XYZ_to_xy(...)` intentionally returns only the chromaticity
coordinates and is not a reversible conversion by itself.

Dominant wavelength and purity helpers operate on CIE xy chromaticity
coordinates:

```python
wavelength, dominant_xy = dominant_wavelength(xy)
complementary_wavelength_nm, complementary_xy = complementary_wavelength(xy)
purity_e = excitation_purity(xy)
purity_c = colorimetric_purity(xy)

result = analyze_chromaticity(xy)
inside = is_inside_chromaticity_locus(xy)
xy_from_pe = xy_from_dominant_wavelength_pe(result.wavelength, result.excitation_purity)
xy_from_pc = xy_from_dominant_wavelength_pc(result.wavelength, result.colorimetric_purity)
```

By default, these functions use D65 white `xy_n=(0.3127, 0.3290)` and the
`standard_observers.chromaticity_coordinates/cie1931_chro_1nm` spectral locus.
`dominant_wavelength(...)` and `complementary_wavelength(...)` return only their
own wavelength and intersection coordinate. Use `analyze_chromaticity(...)`
when you need the paired dominant/complementary result, `dominant_region`,
`complementary_region`, excitation purity and colorimetric purity together.
Region values are `"spectral"`, `"purple"` or `"undefined"`.
`analyze_chromaticity(...)` returns a `ChromaticityAnalysis` object.
`is_inside_chromaticity_locus(...)` checks whether xy coordinates are inside the
closed spectral locus plus purple-line boundary, with boundary points counted as
inside.
The reverse constructors use the same signed-wavelength convention: positive
wavelengths point to the spectral locus, while negative wavelengths reconstruct
non-spectral purple colours from their complementary spectral wavelength.

Correlated colour temperature helpers cover the basic xy/CCT path:

```python
mired = CCT_to_mired(6500)
CCT = mired_to_CCT(mired)
xy_d65 = CCT_to_xy_CIE_D(6504.38938305)
CCT_estimate = xy_to_CCT_McCamy1992(xy_d65)
xy = CCT_to_xy(6504.38938305, method="cie_d")
CCT = xy_to_CCT(xy, method="mccamy1992")
uv = xy_to_uv1960(xy)
CCT_Duv = uv_to_CCT(uv, method="robertson1968")
xy_again = uv1960_to_xy(CCT_to_uv(CCT_Duv, method="robertson1968"))
CCT_Duv_ohno = uv_to_CCT(uv, method="ohno2013")
xy_from_CCT_Duv = CCT_Duv_to_xy(CCT_Duv_ohno, method="ohno2013")
analysis = analyze_temperature(xy, method="ohno2013")
```

There are two different loci in this module:

- `CCT_to_xy_CIE_D(...)` / `CCT_to_xy(..., method="cie_d")` use the CIE D-series
  daylight locus. This gives daylight chromaticity coordinates such as D65
  near `xy=(0.3127, 0.3290)`. It is not the Planckian blackbody locus.
- `uv_to_CCT_*`, `CCT_to_uv_*`, `xy_to_CCT_Duv(...)` and `CCT_Duv_to_xy(...)`
  operate relative to the Planckian locus in CIE 1960 UCS. `Duv=0` means the
  point lies on the Planckian locus.

`CCT_to_xy_CIE_D(...)` uses the same daylight locus formula as
`color.generators.illuminants.daylight_spd(...)`, while the generator builds the
full spectral power distribution. `xy_to_CCT_McCamy1992(...)` is a simple
one-way CCT approximation from xy and does not return `Duv`. For CCT plus `Duv`,
use the CIE 1960 UCS helpers. Robertson 1968 is the default fast path; Ohno
2013 is also available when you want a denser Planckian-table calculation:

```python
CCT_Duv = uv_to_CCT_Ohno2013(uv)
uv = CCT_to_uv_Ohno2013(CCT_Duv)
table = planckian_table_Ohno2013()
```

`uv_to_CCT(..., method="ohno2013")`, `CCT_to_uv(..., method="ohno2013")` and
`xy_to_CCT_Duv(..., method="ohno2013")` route through the same Ohno helpers.
`CCT_Duv_to_xy(...)` is the convenience inverse of `xy_to_CCT_Duv(...)`.
Use `analyze_temperature(...)` when you want named fields instead of a raw
`[CCT, Duv]` array; it returns a `TemperatureAnalysis` object containing `CCT`,
`Duv`, `xy`, `uv`, `method` and `locus`.
`Duv > 0` and `Duv < 0` indicate opposite sides of the Planckian locus in CIE
1960 UCS.

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
- direct CIE 2006 LMS/XYZ matrix transformations
- dominant wavelength, complementary wavelength and purity
- basic CCT, mired, CIE D daylight chromaticity and CCT+Duv calculations
- photopic and scotopic LEFs with luminous efficacy comparison
- smoke checks across datasets, generators, spectra and colorimetry
