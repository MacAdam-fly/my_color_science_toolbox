# Recovery Examples

Examples for `color.recovery`.

- `example_01_reflectance_recovery.py` - Recover bounded smooth reflectance
  spectra from `XYZ` and `xyY` targets computed from a colour-card patch.
- `example_02_spectrum_recovery.py` - Recover effective spectra from `XYZ`
  and `LMS` responses and verify response closure.
- `example_03_reflectance_library.py` - Load default, mixed, and `all_uef`
  reflectance libraries for future basis and dictionary recovery.
- `example_04_pca_reflectance_recovery.py` - Compare bounded least-squares
  and PCA reflectance recovery for the same colour target.
- `example_05_pca_parameter_sweep.py` - Sweep PCA component count and
  coefficient regularisation to show their effect on closure error and curve
  shape.
- `example_06_dictionary_reflectance_recovery.py` - Compare bounded
  least-squares, PCA, and convex dictionary recovery.

Generated figures are written to `examples/recovery/output/` and ignored by Git.
