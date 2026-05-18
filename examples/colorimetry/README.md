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
```

Plots are written to `examples/colorimetry/output/`.

The LMS examples use `from_dataset(..., fill_nan=0.0)` because some CVRL cone
fundamental files contain blank long-wavelength S-cone entries that are treated
as zero response for numerical integration.
