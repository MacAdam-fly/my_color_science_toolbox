# color.recovery

`color.recovery` solves inverse spectral problems. It returns one feasible
spectrum or reflectance under explicit numerical, parametric, or database
priors.

Recovery is not unique. The same `XYZ`, `xyY`, `LMS`, or generic three-channel
response can be produced by many different spectra, so method choice is part of
the model.

中文 API 使用指南见 [`API_GUIDE.md`](API_GUIDE.md)。中文设计说明见
[`README_DETAILS.md`](README_DETAILS.md)。

## What This Module Does

- Recover an effective spectrum from arbitrary three-channel responses.
- Recover an effective spectrum from `XYZ`, `xyY`, or `LMS`.
- Recover a bounded reflectance spectrum from `XYZ` or `xyY` under an
  illuminant and CMFs.
- Load reflectance libraries for PCA and dictionary-based recovery.

This module does not accept RGB directly. Convert RGB or other colour spaces to
`XYZ` explicitly with `color.spaces` before recovery.

## Quick Start

Reflectance recovery from `XYZ`:

```python
from color.colorimetry import reflectance_to_XYZ
from color.recovery import (
    BoundedLeastSquaresOptions,
    recover_reflectance_from_XYZ,
)

target_XYZ = [24.0, 20.0, 18.0]
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    method=BoundedLeastSquaresOptions(bounds=(0.0, 1.0), smoothness=1e-3),
)

closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```

Database-prior reflectance recovery:

```python
from color.recovery import (
    DictionaryReflectanceOptions,
    PCAReflectanceOptions,
    load_reflectance_library,
    recover_reflectance_from_XYZ,
)

library = load_reflectance_library("munsell_matt")

pca = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    method=PCAReflectanceOptions(library=library, n_components=12),
)

dictionary = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    method=DictionaryReflectanceOptions(library=library, top_k=120),
)
```

Effective spectrum recovery:

```python
from color.colorimetry import emission_to_XYZ
from color.recovery import (
    AutoGaussianRecoveryOptions,
    BoundedLeastSquaresOptions,
    recover_spectrum_from_XYZ,
)

spectrum = recover_spectrum_from_XYZ(
    target_XYZ,
    method=BoundedLeastSquaresOptions(bounds=(0.0, float("inf"))),
)
closed_XYZ = emission_to_XYZ(spectrum)

parametric = recover_spectrum_from_XYZ(
    target_XYZ,
    method=AutoGaussianRecoveryOptions(),
)
```

## Method Families

| Family | Methods | Main use |
| --- | --- | --- |
| Smooth least-squares | `bounded_least_squares` | Baseline spectrum or reflectance recovery |
| Parametric spectrum | `gaussian`, `multi_gaussian`, `auto_gaussian` | Emission-like effective spectra |
| Smooth reflectance | `burns2019`, `meng2015` | Database-free bounded reflectance recovery |
| Database reflectance | `pca`, `dictionary` | Reflectance recovery constrained by a measured library |

PCA and dictionary methods are not expected to minimise `XYZ` closure error in
all cases. They trade freedom for a reflectance-library prior.

## Public API

```text
recover_spectrum_from_responses
recover_spectrum_from_XYZ
recover_spectrum_from_xyY
recover_spectrum_from_LMS
recover_reflectance_from_XYZ
recover_reflectance_from_xyY

ReflectanceLibrary
load_reflectance_library

BoundedLeastSquaresOptions
GaussianRecoveryOptions
MultiGaussianRecoveryOptions
AutoGaussianRecoveryOptions
Burns2019RecoveryOptions
Meng2015RecoveryOptions
PCAReflectanceOptions
DictionaryReflectanceOptions

response_recovery_matrix
reflectance_recovery_matrix
second_difference_matrix
solve_bounded_least_squares

SPECTRUM_RECOVERY_METHODS
REFLECTANCE_RECOVERY_METHODS
resolve_spectrum_recovery_method
resolve_reflectance_recovery_method
```

## Scale

`XYZ` and `xyY` use the project-wide `Y=100` convention. `xyY` entries keep the
same `Y` value as the corresponding `XYZ`.
