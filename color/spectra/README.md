# spectra - spectral object wrappers

`color.spectra` is the optional object layer above `color.datasets`.

`color.datasets` returns raw parsed arrays:

```python
dict[str, numpy.ndarray]
```

`color.spectra` wraps those arrays as immutable spectral objects for
interpolation, extrapolation, alignment, reshaping, export, and arithmetic. It
does not replace raw dataset access.

For a detailed guide to object creation, sampling, interpolation, alignment,
export, and common workflows, see `README_DETAILS.md`.

## Quick Start

```python
from color.spectra import SpectralShape, from_cie1931_xyz_cmfs, from_dataset

d65 = from_dataset("illuminants", "D65")
d65_5nm = d65.reshape(SpectralShape(400, 700, 5))
d65_visible = d65.trim(SpectralShape(400, 700, 10))
d65_aligned = d65.align(SpectralShape(360, 830, 5))
d65_values = d65.sample([450, 550])

cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
y_bar = cmfs.channel("Y")
```

Common standard observer shortcuts such as `from_cie1931_xyz_cmfs(...)` and
`from_cie2006_lms_2degree_fundamentals(...)` wrap the corresponding raw
`color.datasets.standard_observers.get_*` helpers. `interval_nm` selects an
existing source file sampling interval; use `reshape(...)` when you need a new
interpolated sampling interval.

Missing values are preserved by default. When a data source uses blank cells to
mean zero response in a known computation context, opt in explicitly:

```python
lms = from_dataset(
    "standard_observers.cone_fundamentals",
    "cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

## Objects

| Object | Purpose |
| --- | --- |
| `SpectralShape` | Regular wavelength domain, e.g. 400-700 nm at 5 nm |
| `SpectralDistribution` | Single-channel spectral signal |
| `MultiSpectralDistribution` | Multi-channel spectral signal sharing one wavelength domain |

Constructors copy input arrays and expose read-only arrays. Operations return
new objects and do not mutate the source object.

`domain` and `range` are read-only aliases for `wavelengths` and `values`.
They are provided for users who prefer the mathematical function vocabulary.

## Operations

| Method | Behavior |
| --- | --- |
| `sample(wavelengths, method="auto")` | Return interpolated numeric values |
| `__call__(wavelengths, method="auto")` | Shortcut for `sample(...)` |
| `interpolate(wavelengths, method="auto")` | Sample inside the current domain |
| `reshape(shape, method="auto")` | Sample inside the current domain at a `SpectralShape` |
| `trim(shape)` | Keep existing source samples inside the shape bounds |
| `extrapolate(shape, method="fill")` | Sample a shape and extrapolate out-of-domain samples |
| `align(shape, extrapolator="constant")` | Sample a shape with interpolation and edge extrapolation |

Interpolation methods are `auto`, `nearest`, `linear`, `cubic`, `pchip`, and
`sprague`. `auto` uses Sprague for uniform data with at least 6 samples, cubic
for non-uniform data with at least 4 samples, and linear otherwise.

Extrapolation methods are `constant`, `linear`, and `fill`. `constant` matches
the boundary values, `linear` extends the boundary slope, and `fill` writes
`fill_value` outside the source domain. `left` and `right` can override the two
outside regions explicitly.

## Export

Use `to_dict()` for column mappings, `to_numpy()` for a dense array, and
`to_pandas()` for a DataFrame.

```python
array = d65.to_numpy()
frame = cmfs.to_pandas()
```

## Arithmetic

Spectral objects support scalar arithmetic and same-type object arithmetic:

```python
scaled = d65 * 0.5
sum_spd = d65 + d65.copy()
```

Object arithmetic requires identical wavelength samples. Multi-channel
arithmetic also requires identical labels. Automatic alignment is intentionally
not performed; call `align(...)` explicitly first.

## Scope

This object layer includes:

- object construction and validation
- conversion from raw columns and registered datasets
- interpolation with explicit out-of-domain handling
- reshape, trim, extrapolate, and align
- numpy and pandas export
- arithmetic operations

It does not implement spectral integration or colorimetric response
computation directly. Use `color.colorimetry` for XYZ/LMS computations once
spectral objects have been prepared and aligned.
