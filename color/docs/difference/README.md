# color.difference

`color.difference` computes colour differences between coordinates that are
already expressed in the same colour space. It does not convert RGB, XYZ, Lab,
CAM02, CAM16, Oklab or Jzazbz values for you.

Use `color.spaces` first when your data is not already in the target space.

中文 API 使用指南见 [`API_GUIDE.md`](API_GUIDE.md)。中文详细说明见
[`README_DETAILS.md`](README_DETAILS.md)。

## Quick Start

```python
import numpy as np

from color.difference import delta_E_CIE2000

Lab_1 = np.array([50.0, 2.6772, -79.7751])
Lab_2 = np.array([50.0, 0.0, -82.7485])

de = delta_E_CIE2000(Lab_1, Lab_2)
```

For RGB input, convert explicitly:

```python
from color.constants import D65_XYZ
from color.difference import delta_E
from color.spaces import SpaceSpec, convert_color

lab_spec = SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ)
Lab_1 = convert_color(rgb_1, "sRGB", lab_spec)
Lab_2 = convert_color(rgb_2, "sRGB", lab_spec)

de = delta_E(Lab_1, Lab_2, method="CIE 2000")
```

## Public API

Standard Lab formulae:

```python
JND_CIE1976
delta_E_CIE1976(Lab_1, Lab_2)
delta_E_CIE1994(Lab_1, Lab_2, textiles=False)
delta_E_CIE2000(Lab_1, Lab_2, textiles=False)
delta_E_CMC(Lab_1, Lab_2, l=2, c=1)
```

Appearance-uniform spaces:

```python
delta_E_CAM02UCS(Jpapbp_1, Jpapbp_2)
delta_E_CAM02LCD(Jpapbp_1, Jpapbp_2)
delta_E_CAM02SCD(Jpapbp_1, Jpapbp_2)
delta_E_CAM16UCS(Jpapbp_1, Jpapbp_2)
delta_E_CAM16LCD(Jpapbp_1, Jpapbp_2)
delta_E_CAM16SCD(Jpapbp_1, Jpapbp_2)
```

Modern space coordinate distances:

```python
delta_E_Oklab(Oklab_1, Oklab_2)
delta_E_Jzazbz(Jzazbz_1, Jzazbz_2)
```

Generic dispatcher:

```python
delta_E(a, b, method="CIE 2000", **kwargs)
```

The method registry is available for advanced inspection from
`color.difference.methods`.

## Method Names

`delta_E(...)` supports:

```text
CIE 1976
CIE 1994
CIE 2000
CMC
CAM02-UCS
CAM02-LCD
CAM02-SCD
CAM16-UCS
CAM16-LCD
CAM16-SCD
Oklab
Jzazbz
```

Common aliases include `cie1976`, `cie1994`, `cie2000`, `CIEDE2000`,
`CAM02UCS`, `CAM16UCS`, `OKLAB` and `JzAzBz`.

## Input Rules

- Inputs must have three values on the last axis.
- Single coordinates use shape `(3,)`.
- Batch coordinates use shape `(..., 3)`.
- Broadcast inputs are supported.
- Non-finite values raise `ValueError`.

The dispatcher does not guess the input space. For example,
`delta_E(a, b, method="Oklab")` assumes `a` and `b` are already Oklab values.

## Appearance Conditions

CAM02/CAM16 viewing conditions are not parameters of `difference`. Choose them
when converting into CAM02/CAM16 uniform spaces. In real appearance-uniform
workflows, prefer an explicit `SpaceSpec(...)` so the viewing environment is
visible at the conversion step:

```python
from color.constants import D65_XYZ
from color.difference import delta_E_CAM16UCS
from color.spaces import SpaceSpec, convert_color

cam16_spec = SpaceSpec(
    "CAM16-UCS",
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
    discount_illuminant=False,
)

cam16_1 = convert_color(rgb_1, "sRGB", cam16_spec)
cam16_2 = convert_color(rgb_2, "sRGB", cam16_spec)

de = delta_E_CAM16UCS(cam16_1, cam16_2)
```

The same principle applies to CAM02-UCS/LCD/SCD and CAM16-UCS/LCD/SCD:
observation conditions belong to the `spaces` conversion stage, while
`difference` receives only the resulting `J'a'b'` coordinates.
