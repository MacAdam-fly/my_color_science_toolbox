# Recovery Examples

Examples for `color.recovery`. Generated figures are written to
`examples/recovery/output/` and ignored by Git.

## Basic Workflows

- `example_01_reflectance_recovery.py`
  - Recover reflectance from `XYZ` and `xyY`.
  - Compare bounded least-squares and Burns 2019 on a colour-card patch.

- `example_02_spectrum_recovery.py`
  - Recover effective spectra from `XYZ` and `LMS`.
  - Verify closure with `emission_to_XYZ(...)` and `emission_to_LMS(...)`.

- `example_03_reflectance_library.py`
  - Load default, mixed, and `all_uef` reflectance libraries.
  - Show sample counts, labels, and representative reflectance curves.

## Database-Prior Reflectance Recovery

- `example_04_pca_reflectance_recovery.py`
  - Compare bounded least-squares and PCA reflectance recovery.
  - Uses an explicitly loaded `ReflectanceLibrary`.

- `example_05_pca_parameter_sweep.py`
  - Sweep PCA component count and coefficient regularisation.
  - Shows how PCA prior strength affects closure and curve shape.

- `example_06_dictionary_reflectance_recovery.py`
  - Compare bounded least-squares, PCA, and convex dictionary recovery.
  - Demonstrates dictionary `top_k` candidate selection.

## Parametric Spectrum Recovery

- `example_07_gaussian_spectrum_recovery.py`
  - Recover a single-peak effective spectrum with `GaussianRecoveryOptions`.
  - Inspect dominant-wavelength metadata.

- `example_08_multi_gaussian_spectrum_recovery.py`
  - Compare single and multi-Gaussian recovery for a two-peak spectrum.

- `example_09_auto_gaussian_spectrum_recovery.py`
  - Show `AutoGaussianRecoveryOptions` selecting single or multi-Gaussian
    models from chromaticity analysis.

## Method Comparison

- `example_10_reflectance_method_comparison.py`
  - Compare bounded least-squares, Burns 2019, Meng 2015, PCA, and dictionary
    on Blue Sky, Foliage, and Moderate Red Macbeth patches.
  - Prints closure error, reflectance range, roughness, and library metadata.

## Run

```powershell
.\.venv\Scripts\python.exe examples\recovery\example_10_reflectance_method_comparison.py
```
