# color.math

`color.math` provides low-level numerical helpers used by the package. The
current scope is one-dimensional interpolation and extrapolation for sampled
signals, especially spectral data.

Chinese API usage examples are available in [`API_GUIDE.md`](API_GUIDE.md).
Chinese design notes are available in [`README_DETAILS.md`](README_DETAILS.md).

## Scope

`color.math` handles numerical mechanics only:

```text
x, y, target arrays -> interpolated or extrapolated values
```

It does not manage spectral objects, channel labels, metadata, units,
colour-space conversion, or colour-science semantics.

For object-level spectral workflows, use `color.spectra`.

## Public API

Interpolation:

- `Interpolator`
- `interpolate_1d(...)`
- `is_uniform(...)`
- `resolve_interpolator(...)`

Extrapolation:

- `Extrapolator`
- `extrapolate_1d(...)`

## Quick Start

```python
import numpy as np
from color.math import extrapolate_1d, interpolate_1d

x = np.array([400.0, 500.0, 600.0])
y = np.array([0.1, 0.8, 0.2])

target = np.array([450.0, 550.0])
values = interpolate_1d(x, y, target, method="linear")

wide_target = np.array([350.0, 450.0, 650.0])
wide_values = extrapolate_1d(
    x,
    y,
    wide_target,
    interpolator="linear",
    method="constant",
)
```

## Interpolation

`interpolate_1d(...)` supports:

- `nearest`
- `linear`
- `cubic`
- `pchip`
- `sprague`
- `auto`

`auto` resolves to:

```text
uniform samples with at least 6 points -> sprague
non-uniform samples with at least 4 points -> cubic
otherwise -> linear
```

Sprague interpolation delegates to `colour.algebra.SpragueInterpolator` so the
first implementation stays close to the reference library behavior. PCHIP uses
SciPy's monotonicity-preserving piecewise cubic interpolator.

## Extrapolation

`extrapolate_1d(...)` first evaluates in-domain samples with interpolation and
then handles out-of-domain samples with:

- `constant`
- `linear`
- `fill`

`left` and `right` can explicitly override the two extrapolated sides.

## Input Rules

- `x`, `y`, and `target` must be one-dimensional arrays.
- `x` and `target` must be strictly increasing.
- `x` and `y` must have the same length.
- all values must be finite.

These strict rules are intentional. If a workflow needs units, metadata,
multi-channel behavior, or object semantics, use an upper-level module such as
`color.spectra`.
