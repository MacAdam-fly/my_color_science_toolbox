# Generator Examples

Examples for `color.generators`. They demonstrate how generator functions return
raw column dictionaries, how the registry `generate(...)` entry works, and how
generated spectra can be plotted with `color.plot`.

Generated figures are written to `examples/generators/output/`. The output
images are ignored by Git and can be regenerated locally.

## Examples

- `example_01_registry_and_illuminants.py` - Generator registry lookup, direct calls and `generate(...)` calls for blackbody, Illuminant A and CIE D daylight.
- `example_02_ideal_spectra.py` - Zero, equal-energy, constant and Gaussian ideal spectral generators.
- `example_03_illuminant_a_comparison.py` - Formula-generated CIE Illuminant A compared with the static dataset.
- `example_04_led_spectra.py` - Single LED components and a weighted RGB LED mixture.

Run one example:

```bash
python examples/generators/example_02_ideal_spectra.py
```

Run all generator example checks:

```bash
python -m pytest color/generators/tests/test_generator_examples.py -q
```
