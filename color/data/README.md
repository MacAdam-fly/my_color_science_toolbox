# Color Science Data

`color/data/` stores immutable reference datasets used by the color science
toolbox.  The files are intentionally kept separate from the parsing layer:
raw data lives here, while public loading APIs live in `color/datasets/`.

## Directory Structure

```text
color/data/
├── standard_observer_data/
│   ├── cmfs/
│   ├── cone_fundamentals/
│   ├── luminous_efficiency/
│   ├── prereceptoral_filters/
│   ├── chromaticity_coordinates/
│   ├── photopigments/
│   └── README.md
├── illuminants/
│   ├── illuminant_A.csv
│   ├── illuminant_D65.csv
│   ├── Fluorescents.xls
│   ├── reference/
│   │   ├── blackbody.xlsx
│   │   └── DaylightSeries.xlsx
│   └── readme.md
├── color_cards/
│   ├── MacbethColorChecker(Sheet1).csv
│   ├── PMC.xlsx
│   ├── RepresentativeBCRA.xls
│   └── readme.md
├── gamut_data/
│   ├── PointerData.xls
│   └── readme.md
├── color_systems/
│   ├── real_sRGB.xls
│   └── readme.md
├── color_difference/
│   ├── CIEDE2000.xls
│   └── readme.md
└── __init__.py
```

## Dataset Summary

### Standard Observer Data

CVRL human visual-system reference data.  The production subfolders contain
106 CSV files registered automatically by `color.datasets.standard_observers`.

| Subfolder | Content | Files |
| --- | --- | ---: |
| `cmfs/` | CIE 1931/1964/2012 XYZ and RGB colour matching functions | 15 |
| `cone_fundamentals/` | LMS cone fundamentals and related sensitivities | 27 |
| `luminous_efficiency/` | Photopic and scotopic luminous efficiency functions | 29 |
| `prereceptoral_filters/` | Macular pigment and lens density spectra | 11 |
| `chromaticity_coordinates/` | CIE and MacLeod-Boynton chromaticity coordinates | 16 |
| `photopigments/` | Photopigment absorption spectra | 7 |

Parser tests create temporary files at runtime instead of storing test-only
datasets in this directory.

### Illuminants

| File | Description | Notes |
| --- | --- | --- |
| `illuminant_A.csv` | CIE Illuminant A | Loaded as `get_illuminant("A")` |
| `illuminant_D65.csv` | CIE Illuminant D65 | Loaded as `get_illuminant("D65")` |
| `Fluorescents.xls` | CIE F1-F12 fluorescent lamp SPDs | Loaded as `get_illuminant("fluorescents")` |
| `reference/DaylightSeries.xlsx` | Tabulated daylight reference data | Reference/validation data |
| `reference/blackbody.xlsx` | Tabulated blackbody reference data | Reference/validation data |

The public loader also provides computed datasets:
`get_illuminant("blackbody", temperature=...)` and
`get_illuminant("daylight", cct=...)`.

### Color Cards

| File | Dataset name | Patches | Wavelength range |
| --- | --- | ---: | --- |
| `MacbethColorChecker(Sheet1).csv` | `macbeth` | 24 | 380-780 nm, 5 nm |
| `PMC.xlsx` | `pmc` | 31 | 400-700 nm, 10 nm |
| `RepresentativeBCRA.xls` | `bcra` | 12 | 380-730 nm, 10 nm |

### Gamut Data

| File | Dataset name | Description |
| --- | --- | --- |
| `PointerData.xls` | `pointer`, `pointer_raw` | Pointer real-surface color gamut data |

### Color Systems

| File | Dataset name | Samples |
| --- | --- | ---: |
| `real_sRGB.xls` | `munsell_srgb` | 1625 |

### Color Difference

| File | Description |
| --- | --- |
| `CIEDE2000.xls` | Reference data for CIEDE2000 verification |

## Accessing Data

Prefer the public dataset loaders instead of reading raw files directly:

```python
from color.datasets import (
    get_color_card,
    get_color_system,
    get_gamut_data,
    get_illuminant,
    get_standard_observer,
)

d65 = get_illuminant("D65")
xyz = get_standard_observer("cmfs", "cie1931_xyz_1nm")
macbeth = get_color_card("macbeth")
pointer = get_gamut_data("pointer", L=50)
munsell = get_color_system("munsell_srgb")
```

Direct file access is still useful for source inspection or independent
validation, but application code should normally go through `color.datasets`.

## Data Stewardship

- Treat files in this directory as immutable source data.
- Add new datasets with clear filenames that include sampling or unit hints
  where practical, such as `_1nm`, `_5nm`, `_logE`, or `_logQ`.
- Keep parser-specific behavior in `color/datasets/`, not in this directory.
- Record source, units, wavelength range, and normalization details in
  `DatasetEntry.metadata`; keep parser/read behavior in
  `DatasetEntry.read_options` or `compute_fn`.

## Sources

| Source | URL |
| --- | --- |
| CVRL, UCL | http://www.cvrl.org/ |
| RIT Munsell Color Science Lab | https://www.rit.edu/science/munsell-color-science-lab-educational-resources |
| RIT Munsell Renotation | http://www.rit-mcsl.org/MunsellRenotation/ |
