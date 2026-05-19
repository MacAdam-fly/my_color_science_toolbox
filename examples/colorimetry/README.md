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
```

Plots are written to `examples/colorimetry/output/`.

`example_end_to_end_smoke.py` uses the high-level `emission_to_XYZ`,
`reflectance_to_XYZ`, `emission_to_LMS` and `reflectance_to_LMS` helpers. The other
examples keep some explicit response loading so they can compare intermediate
data and make the calculation path visible.

`example_photometry.py` plots the default photopic and scotopic luminous
efficiency functions and compares luminous efficacy for a few example spectra.

The LMS examples use `from_dataset(..., fill_nan=0.0)` because some CVRL cone
fundamental files contain blank long-wavelength S-cone entries that are treated
as zero response for numerical integration.
