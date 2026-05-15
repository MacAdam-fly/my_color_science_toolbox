# Standard Illuminant Spectral Data

**Folder:** `data/illuminants/`
**Purpose:** CIE standard illuminant spectral power distributions for colorimetric calculations.

---

## Files

### CIE Standard Illuminants (CSV)

**Source:** [CVRL](http://www.cvrl.org/) — Colour & Vision Research Laboratory, UCL

| File | Description | Wavelength | Step |
|------|-------------|------------|------|
| illuminant_A.csv | **CIE Illuminant A** — typical incandescent/tungsten (~2856K) | 360–830 nm | 1 nm |
| illuminant_D65.csv | **CIE Illuminant D65** — average daylight (~6504K) | 360–830 nm | 1 nm |

**Columns:** `wavelength, spectral_power`

**Key reference:** CIE (2004). Colorimetry, 3rd edition. CIE 15:2004.

---

### Fluorescent Lamps (XLS)

**Source:** [RIT Munsell Color Science Lab](https://www.rit.edu/science/munsell-color-science-lab-educational-resources)

| Property | Value |
|----------|-------|
| Illuminants | F1–F12 (CIE standard fluorescent lamps) |
| Wavelength | 380–780 nm, step 5 nm |
| Format | XLS |

CIE F1–F12 fluorescent lamp **relative spectral power distributions (SPD)**.

| Group | Models | Description |
|-------|--------|-------------|
| Common illuminants | F1–F3 | Daylight fluorescent |
| Common illuminants | F4–F6 | Cool white fluorescent |
| High CRI | F7–F9 | Daylight fluorescent (high color rendering) |
| Three-band | F10–F12 | Tri-phosphor fluorescent (energy-saving) |

---

### Reference Data (reference/)

Daylight series and blackbody radiation data files stored in `reference/`. These are **reference tables** backing the computed datasets (`get_illuminant("blackbody")`, `get_illuminant("daylight")`), not directly loaded as tabulated illuminants.

| File                  | Description                              | Source                  |
| --------------------- | ---------------------------------------- | ----------------------- |
| reference/DaylightSeries.xlsx | CIE D-series daylight (4000-25000 K) | RIT MCSL / Wyszecki & Stiles |
| reference/blackbody.xlsx      | Planck blackbody radiation (3000 K)  | RIT MCSL                |

The computed versions (`"blackbody"`, `"daylight"`) are preferred for programmatic use — they accept arbitrary temperature/CCT parameters.

---

## Usage Example (Python)

```python
from color.datasets import get_illuminant

# CIE Illuminant A
A = get_illuminant("A")
# A["wavelength"] → array([360., 361., ..., 830.])
# A["spd"]        → array([0.0, 3.2, ..., 56.1])

# CIE F1-F12 Fluorescents
fluor = get_illuminant("fluorescents")
# fluor["wavelength"] → array([380., 385., ..., 780.])
# fluor["F1"]         → array([1.87, 2.36, ..., 1.93])

# Computed blackbody (any temperature)
bb = get_illuminant("blackbody", temperature=6500)

# Computed daylight (any CCT)
daylight = get_illuminant("daylight", cct=5000)
```

---

## References

- CIE (2004). Colorimetry, 3rd edition. CIE 15:2004.
- Wyszecki, G. & Stiles, W.S. Color Science: Concepts and Methods. Wiley.
- CVRL. http://www.cvrl.org/
- RIT Munsell Color Science Lab. https://www.rit.edu/science/munsell-color-science-lab-educational-resources
