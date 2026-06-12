# individual_cone_fundamentals

`color.individual_cone_fundamentals` generates individual LMS cone
fundamentals from explicit physiological observer models.

Chinese API usage examples are available in [`API_GUIDE.md`](API_GUIDE.md).
Chinese design notes are available in [`README_DETAILS.md`](README_DETAILS.md).

## Quick Start

Stockman/Rider 2023:

```python
from color.individual_cone_fundamentals import (
    generate_stockman_rider_2023_individual_cone_fundamentals,
)

raw = generate_stockman_rider_2023_individual_cone_fundamentals(observer_degree=2)
raw.keys()  # wavelength, l, m, s
```

Intermediate components for the same observer:

```python
from color.individual_cone_fundamentals import stockman_rider_2023_model_components

components = stockman_rider_2023_model_components(observer_degree=2)
components.keys()  # wavelength, photopigment_absorbance, ..., corneal_energy
```

Asano et al. 2016:

```python
from color.individual_cone_fundamentals import (
    generate_asano2016_individual_cone_fundamentals,
)

raw = generate_asano2016_individual_cone_fundamentals(
    age=32,
    field_size_degree=2,
)
```

Asano model components use the same field names:

```python
from color.individual_cone_fundamentals import asano2016_model_components

components = asano2016_model_components(age=32, field_size_degree=2)
```

The returned `l`, `m`, and `s` columns are corneal, energy-based LMS cone
fundamentals, normalised independently to unit peak.

## Registered Generators

Both models are registered in `color.generators`:

```python
from color.generators import generate

stockman = generate("individual_cone_fundamentals", "stockman_rider_2023")
asano = generate("individual_cone_fundamentals", "asano2016")
```

For interpolation and numerical workflows, use the dedicated `color.spectra`
wrappers:

```python
from color.spectra import (
    from_asano2016_individual_cone_fundamentals,
    from_stockman_rider_2023_individual_cone_fundamentals,
)

lms = from_asano2016_individual_cone_fundamentals(age=45, field_size_degree=2)
l_channel = lms["l"]
```

## Scope

This module currently implements deterministic single-observer curves. It does
not yet implement Asano population Monte Carlo sampling, codon-to-shift
inference, or genotype/hybrid convenience models.
