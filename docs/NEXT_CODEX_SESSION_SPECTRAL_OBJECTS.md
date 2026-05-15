# Next Codex Session: Spectral Object Layer

This document is a handoff note for the next Codex session. It records the
current state of the static datasets module and gives a concrete plan for the
next feature: spectral object wrappers with interpolation, reshape, and
integration support.

## Current Project State

The current completed work is focused on `color.data` and `color.datasets`.

`color/data/` is the immutable static reference-data store. It should contain
standard or reference data files shipped with the package, not user experiment
files and not test-only dirty files.

`color/datasets/` is the static dataset loading layer. Its responsibilities are:

- Register static reference datasets.
- Parse CSV/XLSX/XLS files when they are regular tabular files.
- Compute formula-based datasets such as blackbody and CIE daylight.
- Parse special static files through `compute_fn`.
- Return raw parsed arrays as `dict[str, np.ndarray]`.
- Cache loaded data by canonical dataset identity and call kwargs.
- Return read-only array copies to protect cached data.

Important boundary: `color.datasets` must stay a raw-data layer. It should not
return `SpectralDistribution` or `MultiSpectralDistribution` objects directly.

## Current DatasetEntry Contract

The core registry object is `color.datasets._registry.DatasetEntry`.

Its intended field semantics are:

```text
category      Registered category, e.g. "illuminants" or "standard_observers.cmfs".
name          Dataset name within category.
description   Human-readable description.
source        Source citation or origin string.
file_path     Backing file path for regular file datasets.
computed      True when data is produced by compute_fn.
compute_fn    Formula generator or special static-file parser.
columns       Explicit output column names.
read_options  Generic file reader options only.
metadata      Descriptive information only; must not affect reading.
```

`read_options` is validated at registration time. Current allowed keys:

```text
header
skiprows
usecols
sheet
coerce_numeric
```

`metadata` is intentionally descriptive only. Do not put parser behavior or
callables in `metadata`.

## Current Dataset API

Core API:

```python
from color.datasets import (
    get,
    describe,
    list_categories,
    list_datasets,
    search,
    clear_cache,
    canonicalize_name,
)
```

Category API examples:

```python
from color.datasets import (
    get_illuminant,
    get_standard_observer,
    get_color_card,
    get_gamut_data,
    get_color_system,
)
```

The return type is always raw:

```python
dict[str, np.ndarray]
```

Example:

```python
d65 = get_illuminant("D65")
# {"wavelength": array(...), "spd": array(...)}
```

## Canonical Name Support

Canonical lookup is already implemented in `color.datasets._registry`.

The helper:

```python
canonicalize_name("CIE 1931 XYZ 1 nm")
# "cie1931xyz1nm"
```

Rules include:

- Lowercase.
- Ignore separators such as spaces, underscores, hyphens, slashes, and
  parentheses.
- Convert `°` to `degree`.
- Convert `λ` to `lambda`.
- Convert decimal dots between digits to `p`, e.g. `0.1 nm -> 0p1nm`.

Registry lookup supports canonical category and dataset names:

```python
get("standard_observers.cmfs", "cie1931_xyz_1nm")
get("Standard Observers CMFS", "CIE 1931 XYZ 1 nm")
get("standard-observers/cmfs", "cie-1931-xyz-1nm")
```

Standard observer convenience API also uses canonical category resolution:

```python
get_standard_observer("Cone Fundamentals", "cie2006_lms2_logE_5nm")
get_standard_observer("cmfs", "CIE 1931 XYZ 1 nm")
```

## Test Status at Handoff

The dataset test suite is currently expected to pass cleanly:

```powershell
.\.venv\Scripts\python.exe -m pytest color/datasets/tests -q --basetemp .pytest_tmp
```

Current result at handoff:

```text
153 passed
```

There should be no openpyxl warning. A previous warning came from parsing
`color/data/illuminants/reference/blackbody.xlsx`; that test was removed
because the file is a reference/tool workbook, not a supported production
dataset source.

## Next Feature Goal

Add a new spectral object layer without changing `color.datasets` return types.

Suggested package:

```text
color/spectra/
```

or, if the project prefers singular naming:

```text
color/spectrum/
```

Recommended name: `color/spectra`, because it can contain both single and
multi-spectral objects.

The new layer should provide:

```text
SpectralShape
SpectralDistribution
MultiSpectralDistribution
from_dataset(...)
from_columns(...)
```

This layer should consume raw data from `color.datasets`, but `color.datasets`
should not import this layer. Keep dependency direction one-way:

```text
color.spectra -> color.datasets
color.datasets -> no dependency on color.spectra
```

## Proposed Public API

### SpectralShape

Represents a regular wavelength domain.

Suggested behavior:

```python
shape = SpectralShape(360, 830, 1)
shape.wavelengths
len(shape)
400 in shape
```

Fields:

```text
start: float
end: float
interval: float
```

Validation:

- `start < end`
- `interval > 0`
- generated wavelengths include both start and end when possible

### SpectralDistribution

Represents one spectral signal over wavelength.

Suggested constructor:

```python
sd = SpectralDistribution(
    wavelengths,
    values,
    name="D65",
    quantity="relative_spd",
    wavelength_unit="nm",
    value_unit="relative",
)
```

Suggested classmethod:

```python
sd = SpectralDistribution.from_columns(
    raw,
    x="wavelength",
    y="spd",
    name="D65",
)
```

Expected properties:

```text
name
wavelengths
values
shape
metadata
```

Expected methods:

```text
copy()
to_dict()
interpolate(wavelengths)
reshape(shape)
align(shape)
```

Start with linear interpolation. Avoid implementing every interpolation method
from `colour-science` in the first pass.

### MultiSpectralDistribution

Represents multiple channels over the same wavelength domain, e.g. XYZ CMFs.

Suggested constructor:

```python
msd = MultiSpectralDistribution(
    wavelengths,
    values,
    labels=("X", "Y", "Z"),
    name="CIE 1931 XYZ 1 nm",
)
```

Where `values` can be shape:

```text
(n_wavelengths, n_channels)
```

Suggested classmethod:

```python
cmfs = MultiSpectralDistribution.from_columns(
    raw,
    x="wavelength",
    ys=("X", "Y", "Z"),
    name="CIE 1931 XYZ 1 nm",
)
```

Expected properties:

```text
name
wavelengths
values
labels
shape
metadata
```

Expected methods:

```text
copy()
to_dict()
channel(label)
interpolate(wavelengths)
reshape(shape)
align(shape)
```

`channel(label)` can return a `SpectralDistribution`.

## Dataset Conversion Helpers

Keep these helpers in `color.spectra`, not in `color.datasets`.

Suggested API:

```python
from color.spectra import from_dataset

d65 = from_dataset("illuminants", "D65")
cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
```

Possible implementation strategy:

1. Call `color.datasets.get(category, name, **kwargs)`.
2. Call `color.datasets.describe(category, name)`.
3. Use `entry.metadata["quantity"]` and output columns to choose
   `SpectralDistribution` vs `MultiSpectralDistribution`.

Initial conservative rules:

- If raw data has `wavelength` plus exactly one other column, return
  `SpectralDistribution`.
- If raw data has `wavelength` plus multiple numeric spectral channels, return
  `MultiSpectralDistribution`.
- If there is no `wavelength` column, raise `ValueError`.
- For non-spectral tables such as Munsell or Pointer gamut, raise `ValueError`
  unless explicit column hints are provided.

Avoid trying to auto-wrap every dataset in the first pass.

Suggested helper:

```python
from color.spectra import from_columns

sd = from_columns(raw, x="wavelength", y="spd")
msd = from_columns(raw, x="wavelength", ys=("X", "Y", "Z"))
```

## Interpolation and Reshape

Start simple and explicit.

Recommended first-pass behavior:

```python
sd.interpolate([400, 405, 410])
msd.interpolate(np.arange(400, 701, 5))
```

Use `numpy.interp` for linear interpolation.

Out-of-domain behavior should be explicit. Recommended default:

```text
bounds_error=True
```

If `bounds_error=False`, allow a `fill_value` argument:

```python
sd.interpolate(target_wavelengths, bounds_error=False, fill_value=np.nan)
```

`reshape(shape)` should be a convenience wrapper around interpolation:

```python
sd.reshape(SpectralShape(400, 700, 5))
```

## Integration Direction

Do not overbuild integration immediately. The first integration target should
probably be spectral-to-XYZ later, but that requires careful decisions about:

- CMF object shape.
- Illuminant alignment.
- Integration interval.
- Normalization constant.
- Domain clipping.

For the first spectral-object PR/session, implement object construction,
validation, interpolation, reshape, and conversion from datasets. Leave
colorimetric integration for a second phase unless the user explicitly asks.

## Suggested Implementation Order

1. Create `color/spectra/__init__.py`.
2. Create `color/spectra/core.py` or `color/spectra/distributions.py`.
3. Implement `SpectralShape`.
4. Implement `SpectralDistribution`.
5. Implement `MultiSpectralDistribution`.
6. Implement `from_columns(...)`.
7. Implement `from_dataset(...)`.
8. Add tests under `color/spectra/tests/`.
9. Add examples under `examples/spectra/` or `examples/database/`.
10. Update README or create `color/spectra/README.md`.

## Suggested Tests

Add focused tests instead of broad end-to-end tests at first.

`SpectralShape`:

- Valid construction.
- Reject invalid `start >= end`.
- Reject non-positive interval.
- Wavelength generation includes expected values.

`SpectralDistribution`:

- Construct from arrays.
- Reject mismatched wavelength/value lengths.
- `from_columns` reads `wavelength` and one value column.
- `to_dict()` round-trips.
- `interpolate()` works inside domain.
- `interpolate()` rejects out-of-domain by default.
- `reshape()` returns a new object.

`MultiSpectralDistribution`:

- Construct from arrays.
- Reject mismatched channel labels.
- `from_columns` reads multiple channels.
- `channel("X")` returns a `SpectralDistribution`.
- Interpolation preserves labels and channel count.
- `to_dict()` returns `wavelength` plus channel columns.

Dataset conversion:

- `from_dataset("illuminants", "D65")` returns `SpectralDistribution`.
- `from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")` returns
  `MultiSpectralDistribution`.
- Canonical names work through `from_dataset`.
- Non-spectral dataset such as `from_dataset("color_systems", "munsell_srgb")`
  raises `ValueError`.

## Design Guardrails

- Do not change `color.datasets.get()` return type.
- Do not import `color.spectra` from `color.datasets`.
- Do not make object wrappers mutate raw cached arrays.
- Prefer immutable or copy-on-write behavior for spectral objects.
- Keep interpolation behavior explicit and tested.
- Keep object metadata lightweight; do not build a large schema yet.
- Avoid depending on `colour-science` at runtime. It can be a design reference,
  not a dependency.

## Useful Colour-Science Reference Ideas

The installed `colour-science` package uses these relevant concepts:

- `SpectralShape`
- `SpectralDistribution`
- `MultiSpectralDistributions`
- `CanonicalMapping`
- `LazyCanonicalMapping`

Its design wraps standard data as domain objects and then uses those objects
through colorimetric algorithms. For this project, preserve raw dataset access
first, then offer optional object wrapping in `color.spectra`.

## Current Git/Workspace Notes

At the time this document was written, there are many modified files from the
dataset refactor. Before moving to another computer:

```powershell
git status
git add .
git commit -m "Refine dataset registry and static data loading"
git push origin <branch>
```

If merging into `main`, prefer committing first, then merge/cherry-pick. Do not
delete the current branch until the commit is safely pushed.
