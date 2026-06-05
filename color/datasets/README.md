# datasets - static reference data loading

`color.datasets` is the public loading layer for static files stored under
`color/data/`. It owns dataset registration, lazy loading, caching, generic
CSV/XLS/XLSX parsing, and custom parsers for special static files.

Formula-generated data is intentionally outside this package. Use
`color.generators` for data such as blackbody radiation or CIE D-series
daylight generated from equations.

For the full data inventory, column naming rules, registration guidance, and
metadata conventions, see `README_DETAILS.md`.

## Quick Start

```python
from color.datasets import (
    get_color_card,
    get_color_system,
    get_gamut_data,
    get_illuminant,
    get_reflectance_spectrum,
    get_standard_observer,
)

d65 = get_illuminant("D65")
xyz = get_standard_observer("cmfs", "cie1931_xyz_1nm")
macbeth = get_color_card("macbeth")
uef_munsell = get_reflectance_spectrum("munsell_matt")
pointer_50 = get_gamut_data("pointer", L=50)
macadam_d65 = get_gamut_data("macadam_limits_D65")
munsell = get_color_system("munsell_srgb")
```

All loaders return `dict[str, numpy.ndarray]`. Arrays returned by `get()` are
read-only copies of cached data.

## Registered Static Data

| Category | Examples |
| --- | --- |
| `illuminants` | `A`, `D65`, `fluorescents` |
| `standard_observers.*` | CMFs, chromaticity coordinates, LMS fundamentals, luminous efficiency |
| `color_cards` | `macbeth`, `pmc`, `bcra` |
| `reflectance_spectra.uef` | `munsell_matt`, `agfa_it872`, `forest_birch` |
| `gamut_data` | `pointer`, `pointer_raw`, `macadam_limits_A`, `macadam_limits_C`, `macadam_limits_D65` |
| `color_systems` | `munsell_srgb` |

Blackbody and daylight generators are available from `color.generators`, not
from `color.datasets`.

## Reflectance Spectra

UEF spectral reflectance datasets are available through:

```python
from color.datasets import get_reflectance_spectrum, list_reflectance_spectra

names = list_reflectance_spectra()
munsell = get_reflectance_spectrum("munsell_matt")
```

Runtime data are read from `color/data/reflectance_spectra/uef_csv/`.
Source workbooks with audit information are kept in
`color/data/reflectance_spectra/uef_sources_data/`. Natural colors are not
registered because the available AOTF data are not calibrated reflectance
factors.

## Common Standard Observers

High-use standard observer files have semantic shortcuts in
`color.datasets.standard_observers`. They return the same raw
`dict[str, numpy.ndarray]` as `get(...)`, but avoid requiring users to remember
CVRL file stems:

```python
from color.datasets.standard_observers import (
    get_cie1931_xyz_cmfs,
    get_cie2006_lms_2degree_fundamentals,
)
from color.datasets.illuminants import get_D65_illuminant

d65 = get_D65_illuminant()
cmfs = get_cie1931_xyz_cmfs(interval_nm=1)
lms = get_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")
```

`interval_nm` selects an existing source file sampling interval; it does not
interpolate the data. These shortcuts are intentionally not re-exported from
`color.datasets` to keep the top-level dataset API compact.

## DatasetEntry

All datasets are registered with `DatasetEntry`:

```python
from color.datasets._registry import DatasetEntry, register

register(DatasetEntry(
    category="illuminants",
    name="my_led",
    description="Custom LED SPD",
    file_path="path/to/my_led.csv",
    columns=("wavelength", "spd"),
    read_options={"header": False},
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))
```

Core fields:

| Field | Meaning |
| --- | --- |
| `category` | Registry category, e.g. `illuminants` or `standard_observers.cmfs` |
| `name` | Unique name within the category |
| `description` | Human-readable description |
| `source` | Source publication, URL, or collection |
| `file_path` | Static backing file path |
| `parser_fn` | Optional custom parser for special static files |
| `columns` | Explicit column names; highest priority |
| `read_options` | Generic reader options such as `header`, `skiprows`, `sheet` |
| `metadata` | Descriptive metadata only; does not affect loading |

`parser_fn` receives `file_path` as its first argument:

```python
def parse_special_file(path: str, **kwargs):
    ...
    return {"wavelength": wavelength, "spd": spd}

register(DatasetEntry(
    category="example",
    name="special",
    description="Special static file",
    file_path="path/to/file.txt",
    parser_fn=parse_special_file,
))
```

Do not use `metadata` to control reading behavior. Reader controls belong in
`read_options`; custom static-file logic belongs in `parser_fn`.

## Read Options

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `header` | `False | True | "auto" | int` | `False` | Header strategy |
| `skiprows` | `int` | `0` | Extra rows to skip before reading |
| `usecols` | `Sequence[int]` | `None` | Column indexes to read |
| `sheet` | `int | str` | `0` | Excel sheet |
| `coerce_numeric` | `bool` | `False` | Convert non-numeric cells to `NaN` |

`header=True` and `header="auto"` detect whether the first row contains text
labels. `header=N` means skip `N` rows and use the next row as the header.
If you only need to skip rows without reading a header, use
`read_options={"skiprows": N, "header": False}`.

## Public API

| Function | Meaning |
| --- | --- |
| `get(category, name, **kwargs)` | Load a registered static dataset |
| `describe(category, name)` | Return the `DatasetEntry` without loading data |
| `clear_cache(category=None, name=None)` | Clear cached static data |
| `list_datasets(category=None)` | List dataset names |
| `list_categories()` | List registered categories |
| `search(keyword)` | Search names and descriptions |

Category and dataset names support canonical matching, so spaces, case,
underscores, hyphens, slashes, and similar separators do not affect lookup.

## Behavior Rules

- `get()` returns read-only arrays; call `.copy()` before modifying values.
- Static file and parser results are cached per call-parameter set.
- Parser tests and examples create temporary files at runtime instead of
  storing test-only CSV files in `color/data/`.
- `datasets` does not generate formula data; use `color.generators`.
