# colorimetry

`color.colorimetry` is the computation layer for CIE colorimetry. It consumes
spectral objects or numeric colour values and computes:

- spectral emission / reflectance to XYZ and LMS responses
- XYZ, xy, xyY, uv1960 and u'v'1976 conversions
- direct CIE 2006 LMS <-> XYZ matrix transformations
- photopic / scotopic photometry
- CIE 1976 lightness `Y <-> L*`
- dominant wavelength, complementary wavelength and purity
- CCT, mired, Duv, CIE D daylight locus and Planckian-locus analysis

It sits above datasets, generators and spectra:

```text
color.datasets     static reference data
color.generators   formula-generated spectral data
color.spectra      spectral object wrappers
color.colorimetry  colorimetric computations
```

For the Chinese API guide, see [`API_GUIDE.md`](API_GUIDE.md).
For Chinese design notes, see [`README_DETAILS.md`](README_DETAILS.md).

## Recommended Spectral Workflow

Prepare the spectral objects explicitly when clarity matters. This makes the
observer, illuminant and NaN policy visible in the code.

### Self-Luminous Spectrum

```python
from color.generators.leds import multi_led_spd
from color.spectra import from_cie1931_xyz_cmfs, from_cie2006_lms_2degree_fundamentals
from color.spectra import from_columns
from color.colorimetry import emission_to_XYZ, emission_to_LMS

raw = multi_led_spd(
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)
led = from_columns(raw, y="spd", name="three-peak LED")

cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
lms2 = from_cie2006_lms_2degree_fundamentals(interval_nm=1)

XYZ = emission_to_XYZ(led, cmfs=cmfs)
LMS = emission_to_LMS(led, fundamentals=lms2)
```

Emission conversions do not normalise by default. If `k` is omitted, `k=1`, so
the result scale follows the spectral values, response functions and wavelength
interval.

### Reflectance Spectrum Under D65

```python
from color.datasets.color_cards import get_color_card
from color.spectra import (
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_columns,
)
from color.colorimetry import reflectance_to_XYZ, reflectance_to_LMS

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")

d65 = from_D65_illuminant()
cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
lms2 = from_cie2006_lms_2degree_fundamentals(interval_nm=1)

XYZ = reflectance_to_XYZ(patch, illuminant=d65, cmfs=cmfs)
LMS = reflectance_to_LMS(
    patch,
    illuminant=d65,
    fundamentals=lms2,
    normalisation_channel="m",
)
```

Reflectance conversions normalise by default. For XYZ, a perfect reflecting
diffuser under the chosen illuminant gives `Y=100`. The reflectance spectrum
itself is not modified.

The high-level functions also accept dataset names:

```python
XYZ = reflectance_to_XYZ(patch, illuminant="D65", cmfs="cie1931_xyz_1nm")
```

That shortcut is convenient, but explicit spectral objects are preferred in
examples, tests and scientific workflows where the calculation conditions
should be visible.

## Public API Overview

### Spectral To Responses

```python
emission_to_XYZ(emission, *, cmfs="cie1931_xyz_1nm", shape=None, k=None)
reflectance_to_XYZ(reflectance, *, illuminant="D65", cmfs="cie1931_xyz_1nm", shape=None, k=None)

emission_to_LMS(
    emission,
    *,
    fundamentals="cie2006_lms2_linE_1nm",
    shape=None,
    k=None,
    fill_nan=0.0,
)
reflectance_to_LMS(
    reflectance,
    *,
    illuminant="D65",
    fundamentals="cie2006_lms2_linE_1nm",
    shape=None,
    k=None,
    fill_nan=0.0,
    normalisation_channel=None,
)
```

`cmfs` and `fundamentals` can be either strings naming registered standard
observer datasets or preloaded `MultiSpectralDistribution` objects.
`illuminant` can be a string dataset name or a `SpectralDistribution`.

### Chromaticity

```python
XYZ_to_xyY(XYZ)
xyY_to_XYZ(xyY)
XYZ_to_xy(XYZ)

xy_to_uv1960(xy)
XYZ_to_uv1960(XYZ)
uv1960_to_xy(uv)

xy_to_upvp1976(xy)
XYZ_to_upvp1976(XYZ)
upvp1976_to_xy(upvp)
```

`xy` is a chromaticity projection and is not reversible by itself. Use `xyY`
when luminance must be preserved.

### Direct LMS / XYZ Transformations

```python
LMS_to_XYZ(LMS, observer=2)
XYZ_to_LMS(XYZ, observer=2)
```

These are CIE 2006 matrix transformations after LMS or XYZ values have already
been computed. They are not spectral integration functions.

### Dominant Wavelength And Purity

```python
dominant_wavelength(xy)
complementary_wavelength(xy)
excitation_purity(xy)
colorimetric_purity(xy)
is_inside_chromaticity_locus(xy)

analysis = analyze_chromaticity(xy)
xy_from_dominant_wavelength_pe(analysis.wavelength, analysis.excitation_purity)
xy_from_dominant_wavelength_pc(analysis.wavelength, analysis.colorimetric_purity)
```

Use `analyze_chromaticity(...)` when you need dominant and complementary
information, region labels, and both purity values together.

### Temperature

```python
CCT_to_mired(CCT)
mired_to_CCT(mired)
CCT_to_xy_CIE_D(CCT)
uv_to_CCT(uv, method="robertson1968")
CCT_to_uv([CCT, Duv], method="robertson1968")
xy_to_CCT_Duv(xy, method="robertson1968")
CCT_Duv_to_xy([CCT, Duv], method="robertson1968")
analyze_temperature(xy, method="robertson1968")
```

There are two distinct loci:

- `CCT_to_xy_CIE_D(...)` uses the CIE D-series daylight locus.
- `uv_to_CCT(...)`, `CCT_to_uv(...)`, `xy_to_CCT_Duv(...)` and
  `CCT_Duv_to_xy(...)` work relative to the Planckian locus in CIE 1960 UCS.

`Duv=0` means the point lies on the Planckian locus, not on the CIE D daylight
locus.

Direct algorithm implementations such as Robertson 1968, Ohno 2013 and
McCamy 1992 live in `color.colorimetry.temperature`; the `color.colorimetry`
top level exposes the named dispatchers.

### Photometry And Lightness

```python
photopic_luminous_efficiency_function()
scotopic_luminous_efficiency_function()

photopic_luminous_flux(spd)
scotopic_luminous_flux(spd)
photopic_luminous_efficiency(spd)
scotopic_luminous_efficiency(spd)
photopic_luminous_efficacy(spd)
scotopic_luminous_efficacy(spd)

Y_to_Lstar(Y, Y_n=100.0)
Lstar_to_Y(Lstar, Y_n=100.0)
```

Use the `photopic_*` and `scotopic_*` wrappers for common workflows so the LEF
and `K_m` constants stay matched. Generic `luminous_*` helpers remain available
for custom LEFs. Photometry helpers also accept `shape=None`.

## Spectral Integration Rule

Spectral response integrations use one default rule across XYZ, LMS,
photometry, device responses and reflectance recovery:

- If `shape` is supplied, it is the only integration grid.
- If `shape` is omitted, the response-function grid is clipped to the
  wavelength overlap of all input spectra.
- Aligned values outside their source range are filled with zero.
- Sampled products are integrated with trapezoid quadrature.

SSI is an exception: it follows the Academy SSI method and its fixed
`375-675 nm` / `10 nm` calculation flow rather than this generic spectral
response rule.

## Important Notes

- `colorimetry` expects spectral objects or numeric arrays, not raw dataset
  dictionaries.
- Emission and reflectance integrations use different scaling rules.
- LMS cone fundamental shortcuts use `fill_nan=0.0` by default because some
  CVRL S-cone columns contain blank long-wavelength entries.
- `XYZ_to_xy(...)` loses luminance; `XYZ_to_xyY(...)` keeps it.
- CIE D daylight CCT and Planckian CCT+Duv are related concepts but not the
  same locus.

## Examples

See `examples/colorimetry/` for scripts covering spectral conversion,
reflectance colour cards, generated emission spectra, photometry, lightness,
dominant wavelength and temperature visualisations.
