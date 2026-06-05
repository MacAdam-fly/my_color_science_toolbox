# individual_cone_fundamentals

`color.individual_cone_fundamentals` generates individual LMS cone
fundamentals from the Stockman & Rider 2023 formulae.

Chinese API usage examples are available in [`API_GUIDE.md`](API_GUIDE.md).
Chinese design notes are available in [`README_DETAILS.md`](README_DETAILS.md).

The default result is a raw column dictionary:

```python
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

raw = generate_individual_cone_fundamentals(observer_degree=2)
raw.keys()  # wavelength, l, m, s
```

The returned `l`, `m`, and `s` columns are corneal, energy-based LMS cone
fundamentals, normalised independently to unit peak.

## Parameters

Common parameters:

```python
raw = generate_individual_cone_fundamentals(
    observer_degree=2,
    photopigment_od=(0.50, 0.50, 0.40),
    macular_density_460=0.350,
    lens_density_400=1.7649,
    l_shift_nm=0.0,
    m_shift_nm=0.0,
    s_shift_nm=0.0,
    l_template="mean",
)
```

Defaults follow the CIE 2006 / Stockman-Sharpe standard observer assumptions:

| Observer | L/M/S OD | Macular density at 460 nm | Lens density at 400 nm |
| --- | --- | --- | --- |
| 2 degree | `(0.50, 0.50, 0.40)` | `0.350` | `1.7649` |
| 10 degree | `(0.38, 0.38, 0.30)` | `0.095` | `1.7649` |

## Integration

The same model is registered in `color.generators`:

```python
from color.generators import generate

raw = generate("individual_cone_fundamentals", "stockman_rider_2023")
```

For interpolation and numerical workflows, use the dedicated `color.spectra`
wrapper:

```python
from color.spectra import from_individual_cone_fundamentals

lms = from_individual_cone_fundamentals(observer_degree=2)
l_channel = lms["l"]
```

This wrapper calls the registered generator and preserves generator metadata
and parameters on the returned `MultiSpectralDistribution`.

## Implementation Layout

The public API is intentionally small, while the implementation is split by
responsibility:

- `constants.py`: Stockman/Rider reference, defaults, and Fourier coefficients.
- `templates.py`: macular, lens, and cone absorbance templates.
- `transforms.py`: absorbance-to-absorptance and quantal-to-energy transforms.
- `generation.py`: the final parameter validation and generation pipeline.

## Scope

Version 1 does not implement codon/hybrid genotype-to-shift inference. It
expects users to provide wavelength shifts directly when modelling individual
L/M/S photopigment differences.
