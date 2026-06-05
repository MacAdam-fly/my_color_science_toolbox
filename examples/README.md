# Examples

Minimal examples for the `color` package. Each subdirectory focuses on one
module family and writes generated figures to its own `output/` directory.

Generated output images are ignored by Git; rerun the examples to regenerate
them locally.

## Dataset Examples (`datasets/`)

Examples for `color.datasets` and runtime dataset registration.

- `example_01_illuminants.py` - Static illuminants, blackbody SPDs and CIE D daylight generators.
- `example_02_color_cards.py` - Macbeth, BCRA and colour-card reflectance spectra.
- `example_03_standard_observers.py` - CMFs, LMS fundamentals, luminous efficiency, filters, chromaticity and photopigments.
- `example_04_gamut_data.py` - Pointer gamut and MacAdam gamut datasets.
- `example_05_color_systems.py` - Munsell renotation data and sRGB fields.
- `example_06_custom_data.py` - Temporary CSV/XLSX/parser/generator registration without adding files to `color/data/`.
- `example_07_uef_reflectance_spectra.py` - UEF reflectance spectra loading, spectral wrapping, resampling and CIE 1931 xy computation.

Run one example:

```bash
python examples/datasets/example_01_illuminants.py
```

## Generator Examples (`generators/`)

Examples for `color.generators` and generated spectral data.

- `example_01_registry_and_illuminants.py` - Generator registry lookup, direct calls and `generate(...)` calls for common illuminants.
- `example_02_ideal_spectra.py` - Zero, equal-energy, constant and Gaussian ideal spectral generators.
- `example_03_illuminant_a_comparison.py` - CIE Illuminant A formula compared with the static dataset.
- `example_04_led_spectra.py` - Single LED components and weighted RGB LED mixture.

Run one example:

```bash
python examples/generators/example_02_ideal_spectra.py
```

## Integration Examples (`integration/`)

- `example_01_long_colour_pipeline.py` - Generated LED spectrum and sRGB signal
  through XYZ/LMS, Luv, CAM02-UCS with D50 viewing white, explicit chromatic
  adaptation for Oklab, final Lab, CIEDE2000, CCT and dominant-wavelength analysis.

## Recovery Examples (`recovery/`)

- `example_01_reflectance_recovery.py` - Recover bounded smooth reflectance
  spectra from XYZ and xyY targets and verify XYZ closure.
- `example_02_spectrum_recovery.py` - Recover effective spectra from XYZ and
  LMS responses and verify response closure.
