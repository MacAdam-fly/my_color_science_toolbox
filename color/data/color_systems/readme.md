# Color Notation Systems Data

**Folder:** `color/data/color_systems/`
**Purpose:** Reference data for color notation systems (Munsell, and more to come).

---

## Files

### real_sRGB.xls

**Source:** [RIT Munsell Renotation Data](http://www.rit-mcsl.org/MunsellRenotation/)

| Property | Value |
|----------|-------|
| Chips | 1625 (real/obtainable Munsell chips) |
| Format | XLS (2 sheets) |

**Sheets:**
- **notes** — Disclaimer and data description (empty in current version)
- **data** — 1625 rows × 19 columns, with header row

**Columns (data sheet):**

| # | Name | Description |
|---|------|-------------|
| 1 | `file_order` | Row number in original `real.dat` |
| 2 | `h` | Munsell Hue (string, e.g. "10RP", "2.5R") |
| 3 | `V` | Munsell Value |
| 4 | `C` | Munsell Chroma |
| 5 | `x` | Illuminant C chromaticity x |
| 6 | `y` | Illuminant C chromaticity y |
| 7 | `Y` | Luminance Y |
| 8 | `X_C` | X tristimulus under Illuminant C |
| 9 | `Y_C` | Y tristimulus under Illuminant C |
| 10 | `Z_C` | Z tristimulus under Illuminant C |
| 11 | `X_D65` | X under D65 (CIE CAT2002 chromatic adaptation) |
| 12 | `Y_D65` | Y under D65 |
| 13 | `Z_D65` | Z under D65 |
| 14 | `R` | Analog sRGB red [0, 1] |
| 15 | `G` | Analog sRGB green [0, 1] |
| 16 | `B` | Analog sRGB blue [0, 1] |
| 17 | `dR` | 8-bit digital sRGB red [0, 255] |
| 18 | `dG` | 8-bit digital sRGB green [0, 255] |
| 19 | `dB` | 8-bit digital sRGB blue [0, 255] |

**Notes:**
- D65 data uses CIE CAT2002 chromatic adaptation from Illuminant C
- sRGB values outside [0, 1] have been removed (file is shorter than original `real.dat`)
- Munsell Hue (`h`) is a string array (e.g. `"10RP"`, `"2.5R"`, `"7.5BG"`)
- `file_order` corresponds to the row number in the original `real.dat` from CVRL

---

## Usage Example (Python)

```python
from color.datasets.color_systems import get_color_system

munsell = get_color_system("munsell_srgb")

# Access columns
x = munsell["x"]           # Illuminant C chromaticity
y = munsell["y"]
R = munsell["R"]           # Analog sRGB [0, 1]
V = munsell["V"]           # Munsell Value
```

---

## References

- RIT Munsell Color Science Lab. http://www.rit-mcsl.org/MunsellRenotation/
- Original data: `real.dat` from CVRL
- sRGB conversion: sRGB IEC 61966-2-1 standard
