# Integration Examples

Examples in this folder exercise multiple package layers together instead of
focusing on one module at a time.

## Scripts

| Script | Purpose |
| --- | --- |
| `example_01_long_colour_pipeline.py` | Runs a long chain from generated LED spectra, sRGB and a colour-card reflectance patch through XYZ/LMS, Luv, CAM02-UCS, chromatic adaptation, Oklab, Lab, CIEDE2000, dominant wavelength and CCT+Duv analysis. |

## Long Colour Pipeline

`example_01_long_colour_pipeline.py` is a compact end-to-end check for the
current project architecture. The important idea is that each layer keeps its
own responsibility:

```text
generators -> spectra -> colorimetry -> spaces -> adaptation -> difference
```

The example starts with three different inputs:

```text
1. A generated three-peak LED emission spectrum.
2. An encoded sRGB signal: [0.4, 0.5, 0.6].
3. A Macbeth ColorChecker "Blue Sky" reflectance patch under D65.
```

All are converted to CIE 1931 XYZ and CIE 2006 2-degree LMS. Their XYZ values
then pass through a reversible colour-space chain:

```text
XYZ(D65)
-> Luv(D65)
-> XYZ(D65)
-> adapt to D50
-> CAM02-UCS(D50 viewing white)
-> XYZ(D50)
-> adapt to D65
-> Oklab
-> XYZ(D65)
-> Lab(D65)
-> CIEDE2000
-> dominant wavelength / purity analysis and inverse xy reconstruction
-> CCT + Duv analysis and inverse xy reconstruction
```

The core logic, with the key intent comments preserved, is:

```python
import numpy as np

from color.adaptation import adapt_from_D65, adapt_to_D65
from color.colorimetry import (
    CCT_Duv_to_xy,
    XYZ_to_LMS,
    XYZ_to_xy,
    analyze_chromaticity,
    analyze_temperature,
    emission_to_LMS,
    emission_to_XYZ,
    reflectance_to_LMS,
    reflectance_to_XYZ,
    xy_from_dominant_wavelength_pc,
    xy_from_dominant_wavelength_pe,
)
from color.constants import D50_XYZ, D65_XYZ
from color.datasets.color_cards import get_color_card
from color.difference import delta_E_CIE2000
from color.generators.leds import multi_led_spd
from color.spaces import SpaceSpec, convert_color
from color.spectra import (
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_columns,
)

# 1. Generate and wrap a three-peak LED emission spectrum.
led = from_columns(
    multi_led_spd(
        wavelength_nm=np.arange(390, 831, 1.0),
        peak_wavelengths=(460, 530, 620),
        peak_power_ratios=(0.4, 0.7, 0.9),
    ),
    y="spd",
)

# 2. Integrate the LED against standard observer responses.
cmfs = from_cie1931_xyz_cmfs()
lms2 = from_cie2006_lms_2degree_fundamentals()
XYZ_led = emission_to_XYZ(led, cmfs=cmfs)
LMS_led = emission_to_LMS(led, fundamentals=lms2)

# 3. Convert an sRGB signal to XYZ, then to CIE 2006 2-degree LMS.
RGB = np.array([0.4, 0.5, 0.6])
XYZ_rgb = convert_color(RGB, "sRGB", SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ))
LMS_rgb = XYZ_to_LMS(XYZ_rgb, observer=2)

# 4. Read one colour-card patch as a reflectance spectrum and integrate it
#    under D65. This exercises the dataset -> spectra -> colorimetry path.
raw_card = get_color_card("macbeth")
reflectance = from_columns(raw_card, y="Blue Sky", name="Macbeth Blue Sky")
d65 = from_D65_illuminant()
XYZ_reflectance = reflectance_to_XYZ(reflectance, illuminant=d65, cmfs=cmfs)
LMS_reflectance = reflectance_to_LMS(
    reflectance,
    illuminant=d65,
    fundamentals=lms2,
    normalisation_channel="m",
)

# 5. Stack all samples so the rest of the chain tests batch conversion.
XYZ_D65 = np.vstack([XYZ_led, XYZ_rgb, XYZ_reflectance])

# 6. Move through Luv under a D65 reference white.
Luv = convert_color(
    XYZ_D65,
    SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
    SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
)
XYZ_D65_back = convert_color(
    Luv,
    SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
    SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
)

# 7. CAM02-UCS is evaluated with a D50 viewing white, so adapt explicitly.
XYZ_D50 = adapt_from_D65(XYZ_D65_back, target_white_XYZ=D50_XYZ)
cam02_spec = SpaceSpec(
    "CAM02-UCS",
    XYZ_w=D50_XYZ,
    L_A=318.31,
    Y_b=20,
    surround="Average",
)
CAM02UCS = convert_color(
    XYZ_D50,
    SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ),
    cam02_spec,
)
XYZ_D50_back = convert_color(
    CAM02UCS,
    cam02_spec,
    SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ),
)

# 8. Oklab requires D65-referred XYZ, so adapt back before entering Oklab.
XYZ_for_Oklab = adapt_to_D65(XYZ_D50_back, source_white_XYZ=D50_XYZ)
Oklab = convert_color(
    XYZ_for_Oklab,
    SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
    "Oklab",
)
XYZ_roundtrip = convert_color(
    Oklab,
    "Oklab",
    SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
)

# 9. Finish in D65 Lab and compute a standard Lab colour difference.
Lab = convert_color(
    XYZ_roundtrip,
    SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
    SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ),
)
de00 = delta_E_CIE2000(Lab[0], Lab[1])

# 10. Closure error should stay close to numerical precision.
closure_error = np.linalg.norm(XYZ_roundtrip - XYZ_D65, axis=1)

# 11. Analyse chromaticity, then reconstruct xy from dominant wavelength
#     plus excitation purity and colourimetric purity.
xy = XYZ_to_xy(XYZ_roundtrip)
chromaticity = analyze_chromaticity(xy)
xy_from_pe = xy_from_dominant_wavelength_pe(
    chromaticity.wavelength,
    chromaticity.excitation_purity,
)
xy_from_pc = xy_from_dominant_wavelength_pc(
    chromaticity.wavelength,
    chromaticity.colorimetric_purity,
)
dominant_pe_error = np.linalg.norm(xy_from_pe - xy, axis=1)
dominant_pc_error = np.linalg.norm(xy_from_pc - xy, axis=1)

# 12. Analyse correlated colour temperature and Duv, then reconstruct xy.
temperature = analyze_temperature(xy, method="ohno2013")
cct_duv = np.stack((temperature.CCT, temperature.Duv), axis=-1)
xy_from_cct = CCT_Duv_to_xy(cct_duv, method="ohno2013")
temperature_error = np.linalg.norm(xy_from_cct - xy, axis=1)
```

The example deliberately uses explicit `SpaceSpec(...)` and explicit chromatic
adaptation calls. This keeps the whitepoint semantics visible: `convert_color`
routes colour spaces, while `adapt_from_D65(...)` and `adapt_to_D65(...)`
perform the whitepoint adaptation steps.
