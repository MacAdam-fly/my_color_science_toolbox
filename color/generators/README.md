# generators - formula-generated data

`color.generators` contains data generated from formulas or procedural models.
It is separate from `color.datasets`, which only loads static data files.

中文 API 使用指南见 [`API_GUIDE.md`](API_GUIDE.md).
中文详细设计说明见 [`README_DETAILS.md`](README_DETAILS.md).

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
from color.generators.individual_cone_fundamentals import generate_individual_cone_fundamentals
from color.generators.leds import single_led_spd

bb = generate("blackbody", "blackbody_spd", temperature=6500)
d50 = daylight_spd(cct=5000)
gaussian = gaussian_spd(peak_wavelength=555, width=25)
led = single_led_spd(peak_wavelength=630, half_spectral_width=20)
lms = generate_individual_cone_fundamentals(observer_degree=2)
```

## Registered Categories

| Category | Registered names | Purpose |
| --- | --- | --- |
| `blackbody` | `blackbody_spd` | Planck blackbody spectral radiance |
| `illuminants` | `A`, `cie_d_daylight` | CIE illuminant generation formulas |
| `ideal` | `constant`, `zero`, `equal_energy`, `gaussian` | Idealised spectral distributions |
| `leds` | `single`, `multi` | LED source models |
| `individual_cone_fundamentals` | `stockman_rider_2023` | Individual LMS cone fundamentals |

## Public API Overview

### Registry

```python
GeneratorEntry
register
generate
describe
clear_cache
list_categories
list_generators
```

### Formula Generators

```python
blackbody_spd
generate_blackbody
list_blackbody_generators

illuminant_a_spd
daylight_spd
generate_illuminant
list_illuminant_generators

constant_spd
zero_spd
equal_energy_spd
gaussian_spd
generate_ideal
list_ideal_generators

single_led_spd
multi_led_spd
generate_led
list_led_generators

macular_density_spectrum
lens_density_spectrum
cone_absorbance_spectra
generate_individual_cone_fundamentals
generate_individual_cone_fundamental
list_individual_cone_fundamental_generators
```

See [`API_GUIDE.md`](API_GUIDE.md) for per-API examples.

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

## Individual Cone Fundamentals

The `individual_cone_fundamentals` category generates Stockman/Rider 2023
corneal energy LMS cone fundamentals:

```python
from color.generators import generate

lms = generate(
    "individual_cone_fundamentals",
    "stockman_rider_2023",
    observer_degree=2,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
)
```

The direct function is also available:

```python
from color.generators import generate_individual_cone_fundamentals

lms = generate_individual_cone_fundamentals(observer_degree=10)
```
