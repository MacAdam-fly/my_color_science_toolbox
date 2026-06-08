# color.recovery

`color.recovery` solves inverse spectral problems. It can recover an effective
spectrum from arbitrary three-channel responses, or recover a reflectance
spectrum from `XYZ` / `xyY` under a specified illuminant.

Recovery is not unique: many spectra can produce the same colour stimulus. The
functions here return one feasible spectrum under explicit bounds and smoothness
constraints.

中文 API 使用指南见 [`API_GUIDE.md`](API_GUIDE.md)。中文详细说明见
[`README_DETAILS.md`](README_DETAILS.md)。

## Quick Start

```python
from color.colorimetry import emission_to_XYZ, reflectance_to_XYZ
from color.recovery import (
    load_reflectance_library,
    recover_reflectance_from_XYZ,
    recover_spectrum_from_XYZ,
)

target_XYZ = [24.0, 20.0, 18.0]
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
    bounds=(0.0, 1.0),
    smoothness=1e-3,
)

closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")

reflectance_pca = recover_reflectance_from_XYZ(
    target_XYZ,
    method="pca",
    n_components=8,
)

reflectance_dictionary = recover_reflectance_from_XYZ(
    target_XYZ,
    method="dictionary",
)

reflectance_meng = recover_reflectance_from_XYZ(
    target_XYZ,
    method="meng2015",
)

spectrum = recover_spectrum_from_XYZ(target_XYZ, bounds=(0.0, float("inf")))
closed_emission_XYZ = emission_to_XYZ(spectrum)

library = load_reflectance_library()  # default: UEF Munsell matt, 400-700 nm / 5 nm
print(library.reflectances.shape)     # (samples, wavelengths)
```

## Public API

- `recover_spectrum_from_responses(...)`
- `recover_spectrum_from_XYZ(...)`
- `recover_spectrum_from_LMS(...)`
- `recover_reflectance_from_XYZ(...)`
- `recover_reflectance_from_xyY(...)`
- `ReflectanceLibrary`
- `load_reflectance_library(...)`
- `response_recovery_matrix(...)`
- `reflectance_recovery_matrix(...)`
- `second_difference_matrix(...)`
- `solve_bounded_least_squares(...)`
- `SPECTRUM_RECOVERY_METHODS`
- `REFLECTANCE_RECOVERY_METHODS`
- `resolve_spectrum_recovery_method(...)`
- `resolve_reflectance_recovery_method(...)`

`XYZ` uses the project-wide `Y=100` scale. Other colour spaces should be
converted explicitly with `color.spaces` before recovery.

Reflectance recovery supports bounded smooth least-squares, Meng 2015, PCA, and
convex dictionary recovery. PCA and dictionary methods use a reflectance library
prior and are not registered for generic spectrum recovery. Meng 2015 is an
optimisation method with exact XYZ equality constraints and does not use a
reflectance library.
