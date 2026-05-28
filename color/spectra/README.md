# spectra - spectral object wrappers

`color.spectra` is the object layer for discrete spectral signals. It sits
above `color.datasets` and `color.generators`:

```text
color.datasets     static data files -> dict[str, ndarray]
color.generators   formula-generated data -> dict[str, ndarray]
color.spectra      immutable spectral objects, sampling and alignment
color.colorimetry  XYZ/LMS integration and colour calculations
```

The important rule is simple: datasets and generators return raw column
mappings, while `spectra` wraps those columns as objects that can be sampled,
interpolated, reshaped, aligned, exported, and combined.

## Quick Start

```python
from color.spectra import (
    SpectralShape,
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_columns,
    from_individual_cone_fundamentals,
)

d65 = from_D65_illuminant()
cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
lms = from_individual_cone_fundamentals(observer_degree=2)

d65_5nm = d65.reshape(SpectralShape(400, 700, 5))
y_bar = cmfs["Y"]
l_bar = lms["l"]
values_450_550 = y_bar.sample([450, 550])
```

## Object Creation

Use `from_columns(...)` when you already have a raw column mapping:

```python
sd = from_columns(raw, x="wavelength", y="spd")
msd = from_columns(raw, x="wavelength", ys=("X", "Y", "Z"))
```

Use `from_dataset(...)` for a registered static dataset:

```python
d65 = from_dataset("illuminants", "D65")
cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
```

For common standards, prefer the semantic shortcuts:

| Shortcut | Returns |
| --- | --- |
| `from_D65_illuminant()` | CIE standard illuminant D65 |
| `from_cie1931_xyz_cmfs(interval_nm=1)` | CIE 1931 2-degree XYZ CMFs |
| `from_cie1964_xyz_cmfs(interval_nm=1)` | CIE 1964 10-degree XYZ CMFs |
| `from_cie2012_xyz_2degree_cmfs(interval_nm=1)` | CIE 2012 2-degree XYZ CMFs |
| `from_cie2012_xyz_10degree_cmfs(interval_nm=1)` | CIE 2012 10-degree XYZ CMFs |
| `from_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")` | CIE 2006 2-degree LMS fundamentals |
| `from_cie2006_lms_10degree_fundamentals(interval_nm=1, energy="linE")` | CIE 2006 10-degree LMS fundamentals |
| `from_individual_cone_fundamentals(...)` | Stockman/Rider 2023 individual LMS fundamentals |

`interval_nm` selects an existing source file sampling interval; it does not
interpolate. Use `reshape(...)` or `align(...)` when you need a new wavelength
grid.

CIE 2006 LMS shortcuts default to `fill_nan=0.0`, matching their common use as
response functions for numerical integration. Generic constructors preserve
missing values unless you explicitly pass `fill_nan`.

`from_individual_cone_fundamentals(...)` wraps generated data rather than a
static dataset. It accepts the same parameters as
`color.individual_cone_fundamentals.generate_individual_cone_fundamentals(...)`,
including `observer_degree`, `photopigment_od`, `macular_density_460`,
`lens_density_400`, and L/M/S wavelength shifts.

## Objects And Access

| Object | Purpose |
| --- | --- |
| `SpectralShape` | Regular wavelength domain, e.g. 400-700 nm at 5 nm |
| `SpectralDistribution` | Single-channel spectral signal |
| `MultiSpectralDistribution` | Multi-channel spectral signal sharing one wavelength domain |

Constructors copy input arrays and expose read-only arrays. Operations return
new objects and do not mutate the source object.

Core attributes:

```python
sd.wavelengths
sd.values
sd.domain  # alias for wavelengths
sd.range   # alias for values

msd.labels
```

`keys()` and `[]` follow the raw column view:

```python
d65.keys()   # ("wavelength", "value")
cmfs.keys()  # ("wavelength", "X", "Y", "Z")

d65["wavelength"]  # wavelength array
d65["value"]       # value array
cmfs["wavelength"] # wavelength array
cmfs["Y"]          # SpectralDistribution for the Y channel
```

For a multi-channel object, `obj["label"]` is equivalent to
`obj.channel("label")` and returns a `SpectralDistribution`, not a bare array.
Use `obj.to_dict()["label"]` when you need a writable array copy.

## Sampling And Alignment

| Method | Behavior |
| --- | --- |
| `sample(wavelengths, method="auto")` | Return interpolated numeric values |
| `__call__(wavelengths, method="auto")` | Shortcut for `sample(...)` |
| `interpolate(wavelengths, method="auto")` | Return a new object sampled at explicit wavelengths |
| `reshape(shape, method="auto")` | Resample inside the current domain at a `SpectralShape` |
| `trim(shape)` | Keep existing source samples inside the shape bounds |
| `extrapolate(shape, method="fill")` | Sample a shape and extrapolate out-of-domain samples |
| `align(shape, extrapolator="constant")` | Sample a shape with interpolation and edge extrapolation |

Interpolation methods are `auto`, `nearest`, `linear`, `cubic`, `pchip`, and
`sprague`. `auto` uses Sprague for uniform data with at least 6 samples, cubic
for non-uniform data with at least 4 samples, and linear otherwise.

Extrapolation methods are `constant`, `linear`, and `fill`.

## Export And Arithmetic

Use `to_dict()` for a writable column mapping, `to_numpy()` for a dense array,
and `to_pandas()` for a DataFrame.

```python
raw = cmfs.to_dict()
array = cmfs.to_numpy()
frame = cmfs.to_pandas()
```

Spectral objects support scalar arithmetic and same-type object arithmetic:

```python
scaled = d65 * 0.5
product = illuminant * reflectance
```

Object arithmetic requires identical wavelength samples. Multi-channel
arithmetic also requires identical labels. Automatic alignment is intentionally
not performed; call `align(...)` explicitly first.

## Scope

This module does not compute XYZ or LMS directly. Prepare spectral objects here,
then use `color.colorimetry` for response integration:

```python
from color.colorimetry import emission_to_XYZ, reflectance_to_XYZ
```

That separation keeps raw data loading, signal preparation, and colorimetric
calculation cleanly separated.
