# color.recovery

`color.recovery` solves inverse spectral problems. It can recover an effective
spectrum from arbitrary three-channel responses, or recover a reflectance
spectrum from `XYZ` / `xyY` under a specified illuminant.

Recovery is not unique: many spectra can produce the same colour stimulus. The
functions here return one feasible spectrum under explicit bounds and smoothness
constraints.

## Quick Start

```python
from color.colorimetry import emission_to_XYZ, reflectance_to_XYZ
from color.recovery import recover_reflectance_from_XYZ, recover_spectrum_from_XYZ

target_XYZ = [24.0, 20.0, 18.0]
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
    bounds=(0.0, 1.0),
    smoothness=1e-3,
)

closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")

spectrum = recover_spectrum_from_XYZ(target_XYZ, bounds=(0.0, float("inf")))
closed_emission_XYZ = emission_to_XYZ(spectrum)
```

## Public API

- `recover_spectrum_from_responses(...)`
- `recover_spectrum_from_XYZ(...)`
- `recover_spectrum_from_LMS(...)`
- `recover_reflectance_from_XYZ(...)`
- `recover_reflectance_from_xyY(...)`
- `response_recovery_matrix(...)`
- `reflectance_recovery_matrix(...)`

`XYZ` uses the project-wide `Y=100` scale. Other colour spaces should be
converted explicitly with `color.spaces` before recovery.
