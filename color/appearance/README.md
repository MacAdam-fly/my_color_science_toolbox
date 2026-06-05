# color.appearance

`color.appearance` implements colour appearance models. These models describe how
an `XYZ` stimulus appears under a specified viewing condition, producing
appearance correlates such as lightness, chroma, hue, brightness, colourfulness
and saturation.

The current module provides:

- `CIECAM02`
- `CIECAM16`

For the Chinese API guide, see [API_GUIDE.md](API_GUIDE.md).
For the full Chinese design notes and formula walkthrough, see
[README_DETAILS.md](README_DETAILS.md).

## Scope

This module contains the appearance models themselves:

```text
XYZ -> appearance correlates -> XYZ
```

It does not define uniform colour spaces. CAM02-UCS, CAM02-LCD, CAM02-SCD,
CAM16-UCS, CAM16-LCD and CAM16-SCD live in `color.spaces.appearance`; those
spaces call the CIECAM02 / CIECAM16 models implemented here.

It also does not perform implicit chromatic adaptation for general colour-space
routing. If a workflow needs explicit whitepoint adaptation, use
`color.adaptation` before or after the appearance-model step.

## Public API

```python
from color.appearance import (
    CIECAM02Specification,
    CIECAM02ViewingConditions,
    CIECAM02_to_XYZ,
    InductionFactors_CIECAM02,
    VIEWING_CONDITIONS_CIECAM02,
    XYZ_to_CIECAM02,
    CIECAM16Specification,
    CIECAM16ViewingConditions,
    CIECAM16_to_XYZ,
    InductionFactors_CIECAM16,
    VIEWING_CONDITIONS_CIECAM16,
    XYZ_to_CIECAM16,
)
```

## Quick Start

```python
import numpy as np

from color.appearance import CIECAM02Specification, CIECAM02_to_XYZ, XYZ_to_CIECAM02

XYZ = np.array([19.01, 20.0, 21.78])
XYZ_w = np.array([95.05, 100.0, 108.88])

spec = XYZ_to_CIECAM02(
    XYZ,
    XYZ_w=XYZ_w,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

print(spec.J, spec.C, spec.h)

recovered = CIECAM02_to_XYZ(
    CIECAM02Specification(J=spec.J, C=spec.C, h=spec.h),
    XYZ_w=XYZ_w,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)
```

`CIECAM16` uses the same workflow:

```python
from color.appearance import CIECAM16Specification, CIECAM16_to_XYZ, XYZ_to_CIECAM16

spec = XYZ_to_CIECAM16(XYZ, XYZ_w=XYZ_w, L_A=318.31, Y_b=20.0)
recovered = CIECAM16_to_XYZ(
    CIECAM16Specification(J=spec.J, C=spec.C, h=spec.h),
    XYZ_w=XYZ_w,
    L_A=318.31,
    Y_b=20.0,
)
```

## Viewing Conditions

Both models require a viewing condition:

- `XYZ_w`: reference white tristimulus values.
- `L_A`: adapting field luminance.
- `Y_b`: background luminance factor.
- `surround`: `"Average"`, `"Dim"` or `"Dark"`.
- `discount_illuminant`: whether the illuminant is fully discounted.

The default viewing condition follows the project convention:

```python
XYZ_w = D65_XYZ
L_A = 64 / np.pi * 0.2
Y_b = 20
surround = "Average"
discount_illuminant = False
```

`XYZ`, `XYZ_w` and `Y_b` must be expressed in a consistent luminance reference
domain. The recommended project convention is `Y=100`, matching
`color.constants.D65_XYZ` and the `colorimetry` spectral integration outputs.

## Appearance Specification

Forward conversion returns a specification object:

```text
J, C, h, s, Q, M, H, HC
```

The inverse conversion currently accepts either:

```text
J + C + h
J + M + h
```

`HC` is kept as `None` in this version.

## Examples

```powershell
.\.venv\Scripts\python.exe examples\appearance\example_01_ciecam02.py
.\.venv\Scripts\python.exe examples\appearance\example_02_ciecam16.py
```

The examples show:

- Average / Dim / Dark surround changes.
- Forward and inverse round-trips.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest color\appearance\tests -q --basetemp .pytest_tmp
```
