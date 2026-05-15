# Standard Color Checker Data

**Folder:** `color_checker/color_cards/`
**Purpose:** Standard color card spectral reflectance data for color calibration, reproduction, and evaluation.

---

## Files

### 1. MacbethColorChecker(Sheet1).csv

**Source:** N. Ohta, "The Basis of Color Reproduction Engineering (Japanese)", Corona-sha Co, Japan, 1997

| Property | Value |
|----------|-------|
| Patches | 24 (standard Macbeth ColorChecker) |
| Wavelength | 380–780 nm, step 5 nm |
| Format | CSV |
| Values | Spectral reflectance factor (0–1) |

24 patches in order: Dark Skin, Light Skin, Blue Sky, Foliage, Blue Flower, Bluish Green, Orange, Purplish Blue, Moderate Red, Purple, Yellow Green, Orange Yellow, Blue, Green, Red, Yellow, Magenta, Cyan, White, Neutral 8, Neutral 6.5, Neutral 5, Neutral 3.5, Black

---

### 2. PMC.xlsx

**Source:** M.R. Luo, "The new preferred memory color (PMC) chart", Color Research & Application, 2024

| Property | Value |
|----------|-------|
| Patches | 31 |
| Wavelength | 400–700 nm, step 10 nm |
| Format | XLSX |
| Values | Spectral reflectance (%) |

31 patches representing "preferred memory colors" (idealized common object colors), in 6 categories:

| Category | Patches |
|----------|---------|
| Skin (4) | Caucasian, Oriental, South Asian, African |
| Food (5) | Pork, Carrot, Orange, Orange Yellow, Banana |
| Nature (5) | Yellow Green, Green Apple, Summer Grass, Bluish Green, Smurf |
| Blue-Purple (4) | Blue Sky, Lavender, Purple, Purple Cabbage |
| Unitary (6) | Unitary Red, Yellow, Green, Blue, Magenta, Cyan |
| Neutral (6) | White, Gray-80, Gray-70, Gray-50, Gray-35, Black |

---

### 3. RepresentativeBCRA.xls

**Source:** [RIT Munsell Color Science Lab](https://www.rit.edu/science/munsell-color-science-lab-educational-resources) — CERAM Series II (BCRA) calibration tiles

| Property | Value |
|----------|-------|
| Tiles | 12 |
| Wavelength | 380–730 nm, step 10 nm |
| Format | XLS |
| Values | Spectral reflectance factor |

12 BCRA calibration tiles: Black, Deep Grey, Mid Grey, Light Grey, White, Orange, Cyan, Green, Deep Blue, Bright Yellow, Deep Pink, Red

BCRA (British Ceramic Research Association) tiles are industrial standard reference samples for instrument evaluation and color management.

---

## Usage Example (Python)

```python
import numpy as np

# Macbeth ColorChecker (CSV)
data = np.loadtxt('MacbethColorChecker(Sheet1).csv', delimiter=',', skiprows=3)
wl = data[:, 0]           # 380-780 nm, 5nm step
dark_skin = data[:, 1]    # patch 1

# PMC (XLSX)
import openpyxl
wb = openpyxl.load_workbook('PMC.xlsx')
ws = wb['Sheet1']
pmc = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[0] is not None:
        pmc.append(list(row[:31]))
pmc = np.array(pmc)
wl_pmc = pmc[:, 0]        # 400-700 nm, 10nm step

# RepresentativeBCRA (XLS)
import xlrd
wb = xlrd.open_workbook('RepresentativeBCRA.xls')
ws = wb.sheet_by_name('data')
bcra_wl = [ws.cell_value(r, 0) for r in range(1, ws.nrows)]
bcra_black = [ws.cell_value(r, 1) for r in range(1, ws.nrows)]
```

---

## References

- Ohta, N. (1997). The Basis of Color Reproduction Engineering. Corona-sha Co, Japan.
- Luo, M.R. (2024). The new preferred memory color (PMC) chart. Color Research & Application.
- RIT Munsell Color Science Lab. https://www.rit.edu/science/munsell-color-science-lab-educational-resources
