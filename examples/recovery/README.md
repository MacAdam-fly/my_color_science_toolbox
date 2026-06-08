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
- `example_07_gaussian_spectrum_recovery.py` - Recover a single-peak effective
  spectrum with `method="gaussian"` and inspect dominant-wavelength metadata.
- `example_08_multi_gaussian_spectrum_recovery.py` - Compare single and
  multi-Gaussian recovery for a two-peak effective spectrum.
- `example_09_auto_gaussian_spectrum_recovery.py` - Show `auto_gaussian`
  selecting single or multi-Gaussian models from chromaticity analysis.

Generated figures are written to `examples/recovery/output/` and ignored by Git.
