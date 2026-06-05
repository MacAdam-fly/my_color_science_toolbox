# datasets - static reference data loading

`color.datasets` is the public loading layer for static files stored under
`color/data/`. It owns dataset registration, lazy loading, caching, generic
CSV/XLS/XLSX parsing, and custom parsers for special static files.

Formula-generated data is intentionally outside this package. Use
`color.generators` for blackbody radiation, CIE D-series daylight, LEDs,
ideal spectra, and other equation-generated data.

- For the Chinese API guide, see [`API_GUIDE.md`](API_GUIDE.md).
- For Chinese design notes, see [`README_DETAILS.md`](README_DETAILS.md).

## Quick Start

```python
from color.datasets import (
    get_color_card,
    get_gamut_data,
    get_illuminant,
    get_reflectance_spectrum,
    get_standard_observer,
)

d65 = get_illuminant("D65")
xyz_cmfs = get_standard_observer("cmfs", "cie1931_xyz_1nm")
pmc = get_color_card("pmc")
munsell = get_reflectance_spectrum("munsell_matt")
pointer = get_gamut_data("pointer", L=50)
```

All loaders return `dict[str, numpy.ndarray]`. Returned arrays are read-only
views of cached data; call `.copy()` before modifying values.

## Public API

### Core Registry

| API | Purpose |
| --- | --- |
| `DatasetEntry` | Registration record for one static dataset |
| `canonicalize_name` | Canonical resource-name matching helper |
| `get` | Load a registered dataset |
| `describe` | Inspect a `DatasetEntry` without loading data |
| `clear_cache` | Clear cached dataset reads |
| `list_categories` | List registered categories |
| `list_datasets` | List datasets in a category |
| `register` | Register a new `DatasetEntry` |
| `search` | Search dataset names and descriptions |

### Category Shortcuts

| API | Purpose |
| --- | --- |
| `get_illuminant`, `list_illuminants` | Static illuminant SPDs |
| `get_color_card`, `list_color_cards` | Static colour-card reflectance data |
| `get_standard_observer`, `list_standard_observers`, `list_standard_observer_categories`, `describe_standard_observer` | Standard-observer subcategories |
| `get_gamut_data`, `list_gamut_data` | Pointer and MacAdam reference data |
| `get_color_system`, `list_color_systems` | Static colour-system data |
| `get_reflectance_spectrum`, `list_reflectance_spectra` | UEF spectral reflectance datasets |

## Registered Data

| Category | Examples |
| --- | --- |
| `illuminants` | `A`, `D65`, `fluorescents` |
| `standard_observers.*` | CMFs, chromaticity coordinates, LMS fundamentals, luminous efficiency |
| `color_cards` | `macbeth`, `pmc`, `bcra` |
| `reflectance_spectra.uef` | `munsell_matt`, `agfa_it872`, `forest_birch` |
| `gamut_data` | `pointer`, `macadam_limits_A`, `macadam_limits_C`, `macadam_limits_D65` |
| `color_systems` | `munsell_srgb` |

High-use standard observer semantic shortcuts, such as
`get_cie1931_xyz_cmfs(...)`, live in `color.datasets.standard_observers`.
They are intentionally not re-exported from `color.datasets` to keep this
top-level API compact.

## Design Notes

- `datasets` loads static reference data only; generated data belongs in
  `color.generators` or domain-specific computation modules.
- Reader behavior belongs in `DatasetEntry.read_options` or `parser_fn`.
  `metadata` is descriptive only.
- Category and dataset names use canonical matching, so small differences in
  case, spaces, hyphens, underscores, slashes, `lambda`, degree symbols, and
  resource-name decimal notation do not affect lookup.
- Runtime UEF reflectance spectra are read from CSV files under
  `color/data/reflectance_spectra/uef_csv/`; audit workbooks are kept under
  `color/data/reflectance_spectra/uef_sources_data/`.
