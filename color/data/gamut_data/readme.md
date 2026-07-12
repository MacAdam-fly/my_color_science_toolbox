# Gamut Data

**Folder:** `color/data/gamut_data/`

This folder stores reference gamut datasets used by `color.datasets.gamut_data`
and higher-level `color.gamut` helpers.

All MacAdam CSV files use the project convention `XYZ(Y=100)`.

## Files

### PointerData.xls

**Source:** M. R. Pointer, "The Gamut of Real Surface Colors", Color Research
& Application, 5(3), 1980.

`PointerData.xls` contains Pointer real-surface colour gamut data.

Important sheets:

| Sheet | Meaning |
|-------|---------|
| `Data` | Original real-surface colour data. |
| `Calculations` | Regular Pointer boundary table used by `get_gamut_data("pointer")`. |
| `IllumDat` | Illuminant spectral data bundled in the workbook. |
| `SpecLoc` | Spectral locus chromaticity coordinates bundled in the workbook. |

The project mainly uses the `Calculations` sheet. It contains Pointer boundary
rows over:

```text
L*: 20, 30, ..., 90
hue: 0, 10, ..., 360
```

The parsed dataset includes `L`, `C`, `hab`, `a`, `b`, `x`, `y` and reference
white columns such as `Xn`, `Yn`, `Zn`.

In `color.gamut`, `pointer_gamut()` wraps this regular `L* x hue` table as a
`PointerGamutBoundary`. The xy-plane boundary used for plotting and xy coverage
is the published 32-point Pointer xy boundary, not a projection of the Lab
table.

### MacAdamBoundary_A_L1_H3.csv / MacAdamBoundary_C_L1_H3.csv / MacAdamBoundary_D65_L1_H3.csv

These are the packaged static MacAdam LCHab boundary resources for CIE
Illuminants A, C and D65.
Each file uses `L*=0..100` in 1-unit steps and `h=0..360 degrees` in 3-degree
steps, with columns `L`, `h`, and `C_max`.

The default `macadam_limits("A" / "C" / "D65")` request loads this L1/h3
boundary directly. Requests for a different grid use the computed MacAdam
route instead of interpolating the static boundary.

## Usage

```python
from color.datasets.gamut_data import get_gamut_data

pointer = get_gamut_data("pointer")
pointer_50 = get_gamut_data("pointer", L=50)

macadam_d65 = get_gamut_data("macadam_limits_D65")

pointer["L"]
pointer["C"]
pointer["hab"]
pointer["x"]
pointer["y"]

macadam_d65["L"]
macadam_d65["h"]
macadam_d65["C_max"]
```

Raw Pointer workbook sheets can still be read through:

```python
data = get_gamut_data("pointer_raw", sheet="Data")
specloc = get_gamut_data("pointer_raw", sheet="SpecLoc")
```

## Notes

- `color.datasets.gamut_data` only reads the stored tables.
- `color.gamut.pointer` and `color.gamut.macadam` provide the semantic wrappers,
  inside tests, boundaries and coverage workflows.
- Pointer and MacAdam are object-colour/reference gamuts, not display-primary
  gamuts.
