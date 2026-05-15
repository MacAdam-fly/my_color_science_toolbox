# Color Science Data

**Folder:** `color/data/`
**Purpose:** Static reference datasets for colorimetric calculations, including color matching functions, standard illuminants, color checker spectral data, real surface color gamut, and color difference formulae.

All data files are immutable reference data. Use clear filenames with units when relevant.

---

## Directory Structure

```
data/
├── standard_observer_data/            # CVRL physiological color science data
│   ├── cmfs/                   # Colour Matching Functions
│   ├── cone_fundamentals/      # Cone Spectral Sensitivities
│   ├── luminous_efficiency/    # Luminous Efficiency Functions
│   ├── prereceptoral_filters/  # Macular Pigment & Lens Density
│   ├── chromaticity_coordinates/
│   ├── photopigments/
│   └── README.md
│
├── color_cards/                # Standard color checker spectral data
│   ├── MacbethColorChecker(Sheet1).csv
│   ├── PMC.xlsx
│   ├── RepresentativeBCRA.xls
│   └── readme.md
│
├── gamut_data/                 # Real surface color gamut data
│   ├── PointerData.xls
│   └── readme.md
│
├── color_systems/              # Color notation system data
│   ├── real_sRGB.xls
│   └── readme.md
│
├── illuminants/                # Standard illuminant spectral data
│   ├── illuminant_A.csv        # CIE A (~2856K)
│   ├── illuminant_D65.csv      # CIE D65 (~6504K)
│   ├── DaylightSeries.xlsx     # D series (4000–25000K)
│   ├── Fluorescents.xls        # F1–F12
│   ├── blackbody.xlsx          # Planck radiation
│   └── readme.md
│
└── __init__.py
```

---

## Category Overview

### 1. Standard Observer Data (`standard_observer_data/`)

CVRL (Colour & Vision Research Laboratory, UCL) physiological color science data. 106 CSV files covering the human visual system fundamentals.

| Subfolder | Content | Files |
|-----------|---------|-------|
| `cmfs/` | CIE 1931/1964/2012 XYZ colour matching functions | 15 |
| `cone_fundamentals/` | Stockman & Sharpe LMS cone sensitivities | 27 |
| `luminous_efficiency/` | Photopic/scotopic V(λ) functions | 29 |
| `prereceptoral_filters/` | Macular pigment & lens density spectra | 11 |
| `chromaticity_coordinates/` | CIE & MacLeod-Boynton chromaticity coords | 16 |
| `photopigments/` | Photopigment absorption spectra | 8 |

Source: [CVRL](http://www.cvrl.org/)

### 2. Color Cards (`color_cards/`)

Standard color card spectral reflectance data for calibration, reproduction, and evaluation.

| File | Patches | Wavelength | Source |
|------|---------|------------|--------|
| MacbethColorChecker(Sheet1).csv | 24 | 380–780 nm, 5nm | Ohta (1997) |
| PMC.xlsx | 31 | 400–700 nm, 10nm | Luo (2024) |
| RepresentativeBCRA.xls | 12 | 380–730 nm, 10nm | RIT MCSL |

### 3. Gamut Data (`gamut_data/`)

Color gamut boundaries of real surface colors.

| File | Samples | Source |
|------|---------|--------|
| PointerData.xls | 4089 | Pointer (1980) |

### 4. Color Systems (`color_systems/`)

Color notation system reference data.

| File | Samples | Source |
|------|---------|--------|
| real_sRGB.xls | 1625 | RIT Munsell Renotation |

### 5. Illuminants (`illuminants/`)

CIE standard illuminant spectral power distributions.

| File | Description | Wavelength |
|------|-------------|------------|
| illuminant_A.csv | CIE Illuminant A (~2856K) | 360–830 nm, 1nm |
| illuminant_D65.csv | CIE Illuminant D65 (~6504K) | 360–830 nm, 1nm |
| DaylightSeries.xlsx | CIE Daylight D series (4000–25000K) | 300–830 nm, 5nm |
| Fluorescents.xls | CIE F1–F12 fluorescent lamps | 380–780 nm, 5nm |
| blackbody.xlsx | Planck blackbody radiation | 300–800 nm, 10nm |

---

## Quick Start

```python
import numpy as np

# --- CVRL base data ---
# CIE 1931 2° XYZ CMFs
data = np.loadtxt('standard_observer_data/cmfs/cie1931_xyz_5nm.csv', delimiter=',')
wl, x_bar, y_bar, z_bar = data.T

# --- Color cards ---
# Macbeth ColorChecker
data = np.loadtxt('color_cards/MachbethColorChecker(Sheet1).csv', delimiter=',', skiprows=3)

# --- Illuminants ---
import numpy as np
# CIE A
data = np.loadtxt('illuminants/illuminant_A.csv', delimiter=',')
wl, spd_A = data[:, 0], data[:, 1]
# CIE D65
data = np.loadtxt('illuminants/illuminant_D65.csv', delimiter=',')
wl, spd_D65 = data[:, 0], data[:, 1]
# Daylight series from CCT
import openpyxl
wb = openpyxl.load_workbook('illuminants/DaylightSeries.xlsx')

# --- Gamut data ---
import xlrd
wb = xlrd.open_workbook('gamut_data/PointerData.xls')
```

---

## Data Sources

| Source | URL |
|--------|-----|
| CVRL (UCL) | http://www.cvrl.org/ |
| RIT Munsell Color Science Lab | https://www.rit.edu/science/munsell-color-science-lab-educational-resources |
| RIT Munsell Renotation | http://www.rit-mcsl.org/MunsellRenotation/ |

---

## Naming Conventions

- Keep data files immutable
- Use clear filenames with units when relevant (e.g., `_5nm`, `_1nm`, `_logE`)
- Access via `color_agent.data` or `color_agent.io` loaders
