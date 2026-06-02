# color.recovery

`color.recovery` solves inverse spectral problems. Version 1 recovers one
bounded, smooth reflectance spectrum from a target `XYZ` or `xyY` value.

Recovery is not unique: many reflectance spectra can produce the same colour
stimulus under the same illuminant and observer. The functions here return a
feasible spectrum under explicit bounds and smoothness constraints.

## Quick Start

```python
from color.recovery import recover_reflectance_from_XYZ
from color.colorimetry import reflectance_to_XYZ

target_XYZ = [24.0, 20.0, 18.0]
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
    bounds=(0.0, 1.0),
    smoothness=1e-3,
)

closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```

## Public API

- `recover_reflectance_from_XYZ(...)`
- `recover_reflectance_from_xyY(...)`
- `reflectance_recovery_matrix(...)`
- `second_difference_matrix(...)`

`XYZ` uses the project-wide `Y=100` scale. Other colour spaces should be
converted explicitly with `color.spaces` before recovery.
