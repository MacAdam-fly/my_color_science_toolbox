# generators - formula-generated data

`color.generators` contains data generated from formulas or procedural models.
It is separate from `color.datasets`, which only loads static data files.

## Quick Start

```python
from color.generators import generate
from color.generators.illuminants import blackbody_spd, daylight_spd

bb = generate("illuminants", "blackbody", temperature=6500)
d50 = daylight_spd(cct=5000)
```

Generators return raw column dictionaries:

```python
dict[str, numpy.ndarray]
```

Use `color.spectra.from_columns(...)` when an object wrapper is useful.
