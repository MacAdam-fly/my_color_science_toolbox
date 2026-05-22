# generators - formula-generated data

`color.generators` contains data generated from formulas or procedural models.
It is separate from `color.datasets`, which only loads static data files.

Generators return raw column dictionaries:

```python
dict[str, numpy.ndarray]
```

Use `color.spectra.from_columns(...)` when an object wrapper is useful.

## Quick Start

```python
from color.generators import generate
from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.generators.illuminants import daylight_spd
from color.generators.leds import single_led_spd

bb = generate("blackbody", "blackbody_spd", temperature=6500)
d50 = daylight_spd(cct=5000)
gaussian = gaussian_spd(peak_wavelength=555, width=25)
led = single_led_spd(peak_wavelength=630, half_spectral_width=20)
```

## Registered Categories

| Category | Registered names | Purpose |
| --- | --- | --- |
| `blackbody` | `blackbody_spd` | Planck blackbody spectral radiance |
| `illuminants` | `A`, `cie_d_daylight` | CIE illuminant generation formulas |
| `ideal` | `constant`, `zero`, `equal_energy`, `gaussian` | Idealised spectral distributions |
| `leds` | `single`, `multi` | LED source models |

## Blackbody Generator

The `blackbody` category contains physically based blackbody radiation models:

```python
from color.generators import generate

blackbody = generate("blackbody", "blackbody_spd", temperature=6500)
```

## Illuminant Generators

The `illuminants` category contains CIE illuminant formulas:

```python
from color.generators import generate

illuminant_a = generate("illuminants", "A")
daylight = generate("illuminants", "cie_d_daylight", cct=5000)
```

## Ideal Spectral Generators

The `ideal` category follows the same raw-data contract as datasets:

```python
from color.generators import generate
from color.spectra import from_columns

raw = generate("ideal", "gaussian", peak_wavelength=555, width=25)
sd = from_columns(raw, y="spd", name="Gaussian 555 nm")
```

Available direct functions:

```python
from color.generators.ideal import (
    constant_spd,
    zero_spd,
    equal_energy_spd,
    gaussian_spd,
)
```

`gaussian_spd(...)` supports:

```python
gaussian_spd(peak_wavelength=555, width=25, method="normal")
gaussian_spd(peak_wavelength=555, width=50, method="fwhm")
```

## LED Generators

`single_led_spd(...)` and `multi_led_spd(...)` use the Ohno 2005 LED model.

```python
from color.generators.leds import multi_led_spd

rgb_led = multi_led_spd(
    peak_wavelengths=(457, 530, 615),
    half_spectral_widths=(20, 30, 20),
    peak_power_ratios=(0.731, 1.0, 1.66),
)
```
