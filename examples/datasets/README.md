# Dataset Examples

These examples demonstrate the `color.datasets` layer: loading static reference
data, inspecting available datasets, and registering temporary custom files.

The plotting examples use `color.plot` primitives and save PNG files to
`examples/datasets/output/`. They do not call `plt.show()`, so they can run in
automated tests without blocking.

## Examples

- `example_01_illuminants.py`  
  Loads static CIE illuminants and compares generated blackbody and CIE D-series
  daylight SPDs.

- `example_02_color_cards.py`  
  Loads Macbeth ColorChecker and BCRA colour-card reflectance datasets.

- `example_03_standard_observers.py`  
  Loads standard observer datasets: CIE XYZ CMFs, CIE 2006 LMS fundamentals,
  luminous efficiency functions, prereceptoral filters, chromaticity coordinates
  and photopigment data.

- `example_04_gamut_data.py`  
  Loads Pointer real-surface colour gamut data and visualises Lab and xy slices.

- `example_05_color_systems.py`  
  Loads Munsell renotation data and shows chromaticity, luminance distribution
  and in-gamut sRGB samples.

- `example_06_custom_data.py`  
  Creates temporary CSV/XLSX/custom-parser data at runtime and registers them
  through the dataset registry. It is intentionally file-clean: temporary files
  are removed after the example exits.

- `example_07_uef_reflectance_spectra.py`  
  Loads all registered UEF reflectance spectra, selects 3-5 samples from each
  dataset, wraps them as `SpectralDistribution`, resamples them to
  `400-700 nm / 5 nm`, computes CIE 1931 xy coordinates under D65, and writes
  one spectra grid plus one chromaticity grid.

## Run

```bash
python examples/datasets/example_01_illuminants.py
python examples/datasets/example_02_color_cards.py
python examples/datasets/example_03_standard_observers.py
python examples/datasets/example_04_gamut_data.py
python examples/datasets/example_05_color_systems.py
python examples/datasets/example_06_custom_data.py
python examples/datasets/example_07_uef_reflectance_spectra.py
```
