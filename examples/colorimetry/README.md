# colorimetry examples

These examples demonstrate the current `color.colorimetry` layer as an
end-to-end bridge:

```text
datasets / generators -> spectra -> colorimetry -> xyY / LMS / photometry / CCT
```

The examples are numbered so they can be read as a short guide. Plots are
written to `examples/colorimetry/output/`.

## Run

Run individual examples from the project root:

```powershell
.\.venv\Scripts\python.exe examples\colorimetry\example_01_spectral_conversion_overview.py
.\.venv\Scripts\python.exe examples\colorimetry\example_02_reflectance_color_cards.py
.\.venv\Scripts\python.exe examples\colorimetry\example_03_emission_spectra.py
.\.venv\Scripts\python.exe examples\colorimetry\example_04_illuminant_a_comparison.py
.\.venv\Scripts\python.exe examples\colorimetry\example_05_chromaticity_arrays.py
.\.venv\Scripts\python.exe examples\colorimetry\example_06_photometry.py
.\.venv\Scripts\python.exe examples\colorimetry\example_07_lightness.py
.\.venv\Scripts\python.exe examples\colorimetry\example_08_lms_xyz_transformations.py
.\.venv\Scripts\python.exe examples\colorimetry\example_09_dominant_wavelength.py
.\.venv\Scripts\python.exe examples\colorimetry\example_10_temperature.py
```

Run the example integration check:

```powershell
.\.venv\Scripts\python.exe -m pytest color\colorimetry\tests\test_examples.py -q --basetemp .pytest_tmp
```

## Guide

`example_01_spectral_conversion_overview.py` gives a compact overview of the
main conversion path. It converts a perfect reflector and a generated emission
spectrum to XYZ, then shows the same results as xyY coordinates, xy positions
and approximate sRGB preview swatches.

`example_02_reflectance_color_cards.py` converts selected PMC colour-card
reflectance patches under D65. It focuses on reflectance curves, CIE 1931 xy
positions, relative luminance `Y` and approximate sRGB previews instead of raw
XYZ bar charts.

`example_03_emission_spectra.py` converts generated self-luminous spectra,
including a blackbody, CIE D daylight, a Gaussian source and an RGB LED mixture.
It compares their xy positions and LMS cone responses.

`example_04_illuminant_a_comparison.py` compares the static Illuminant A dataset
with the formula-generated Illuminant A SPD. The plot highlights SPD overlap,
xy agreement and the small `Delta x`, `Delta y`, `Delta Y` residuals.

`example_05_chromaticity_arrays.py` demonstrates batch conversion for
image-like arrays. It converts an `n*m*3` XYZ array to `n*m*3` xyY and `n*m*2`
xy while preserving the leading dimensions.

`example_06_photometry.py` plots photopic and scotopic luminous efficiency
functions and compares luminous efficacy for several example spectra.

`example_07_lightness.py` shows the CIE 1976 `Y -> L* -> Y` round-trip on
relative luminance samples.

`example_08_lms_xyz_transformations.py` shows direct CIE 2006 LMS and XYZ matrix
round-trips after tristimulus or cone-response values have already been
computed.

`example_09_dominant_wavelength.py` computes and plots dominant wavelength,
complementary wavelength, excitation purity and colorimetric purity for several
CIE xy samples.

`example_10_temperature.py` computes CCT/mired relationships, compares Robertson
and Ohno CCT+Duv values, and plots CIE D daylight and Planckian loci.

Approximate sRGB swatches are only visual aids. The examples keep the computed
XYZ and xyY values unchanged; clipping is applied only inside the plotting
preview.

The LMS examples use `from_dataset(..., fill_nan=0.0)` because some CVRL cone
fundamental files contain blank long-wavelength S-cone entries that are treated
as zero response for numerical integration.
