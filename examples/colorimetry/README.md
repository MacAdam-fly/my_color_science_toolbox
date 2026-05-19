# colorimetry examples

These examples exercise the end-to-end path:

```text
datasets / generators -> spectra -> colorimetry
```

Run them from the project root:

```powershell
.\.venv\Scripts\python.exe examples\colorimetry\example_reflectance_color_card_xyz_lms.py
.\.venv\Scripts\python.exe examples\colorimetry\example_emission_generators_xyz_lms.py
.\.venv\Scripts\python.exe examples\colorimetry\example_illuminant_a_xyz_comparison.py
.\.venv\Scripts\python.exe examples\colorimetry\example_chromaticity_array.py
.\.venv\Scripts\python.exe examples\colorimetry\example_end_to_end_smoke.py
.\.venv\Scripts\python.exe examples\colorimetry\example_photometry.py
.\.venv\Scripts\python.exe examples\colorimetry\example_lightness.py
.\.venv\Scripts\python.exe examples\colorimetry\example_lms_xyz_transformations.py
.\.venv\Scripts\python.exe examples\colorimetry\example_dominant_wavelength.py
```

Plots are written to `examples/colorimetry/output/`.

`example_end_to_end_smoke.py` uses the high-level `emission_to_XYZ`,
`reflectance_to_XYZ`, `emission_to_LMS` and `reflectance_to_LMS` helpers. The other
examples keep some explicit response loading so they can compare intermediate
data and make the calculation path visible.

`example_photometry.py` plots the default photopic and scotopic luminous
efficiency functions and compares luminous efficacy for a few example spectra.

`example_lightness.py` shows the CIE 1976 `Y -> L* -> Y` round-trip on a few
relative luminance samples.

`example_lms_xyz_transformations.py` shows direct CIE 2006 LMS and XYZ matrix
round-trips after values have already been computed.

`example_dominant_wavelength.py` computes and plots dominant wavelength,
complementary wavelength, excitation purity and colorimetric purity for a few
CIE xy samples, including the full `analyze_chromaticity(...)` result
used for plotting both intersections and a reverse reconstruction from
dominant wavelength plus colorimetric purity.

The LMS examples use `from_dataset(..., fill_nan=0.0)` because some CVRL cone
fundamental files contain blank long-wavelength S-cone entries that are treated
as zero response for numerical integration.
