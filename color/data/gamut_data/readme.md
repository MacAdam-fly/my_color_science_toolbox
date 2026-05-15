# Real Surface Color Gamut Data

**Folder:** `color/data/gamut_data/`
**Purpose:** Color gamut boundaries of real surface colors, used for gamut mapping and color reproduction research.

---

## Files

### PointerData.xls

**Source:** M.R. Pointer, "The Gamut of Real Surface Colors", Color Research & Application, 5(3), 1980

| Property | Value |
|----------|-------|
| Samples | 4089 (real surface colors) |
| Format | XLS (multi-sheet) |

**Sheets:**
- **Data** — C\*ab as a function of L\* and hab (Illuminant C, 2° observer)
- **Calculations** — Gamut boundary at 8 L\* levels (20–90), each with 37 hue angles (0°–360° in 10° steps). Columns: L\*, C\*, a\*, b\*, X', Y', Z', x, y, u', v'. Reference white (Illuminant C, SC 2°): Xn=98.07, Yn=100.00, Zn=118.23
- **IllumDat** — Illuminant spectral data
- **SpecLoc** — 324 chromaticity coordinate points (x, y, u', v')

This dataset defines the gamut boundary of real surface colors, widely used in gamut mapping and color reproduction research.

---

## Usage Example (Python)

```python
from color.datasets.gamut_data import get_gamut_data

# Calculations sheet (default) — Pointer gamut boundary
pointer = get_gamut_data("pointer")           # all L* levels, 296 rows
pointer_50 = get_gamut_data("pointer", L=50)  # L*=50 only, 37 rows

pointer["L"]    # L* values
pointer["hab"]  # hue angles (0–360)
pointer["C"]    # chroma C*
pointer["a"]    # a*
pointer["b"]    # b*
pointer["x"]    # chromaticity x
pointer["y"]    # chromaticity y

# Other sheets via generic reader
data = get_gamut_data("pointer_raw", sheet="Data")
specloc = get_gamut_data("pointer_raw", sheet="SpecLoc")
```

---

## References

- Pointer, M.R. (1980). The Gamut of Real Surface Colors. Color Research & Application, 5(3).
