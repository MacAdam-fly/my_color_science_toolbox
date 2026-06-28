# adaptation

`color.adaptation` provides explicit chromatic adaptation helpers. It is a
standalone foundation module, not part of any single colour space.

中文 API 使用指南见 [`API_GUIDE.md`](API_GUIDE.md)。中文详细说明见
[`README_DETAILS.md`](README_DETAILS.md)。

The first version implements Von Kries style adaptation using four transforms:

- `Von Kries`
- `Bradford`
- `CAT02`
- `CAT16`

It also provides `chromatic_adaptation_Zhai2018(...)`, a higher-level two-step
chromatic adaptation model for workflows that need explicit source and target
degrees of adaptation. Zhai 2018 uses `CAT02` or `CAT16` internally; it is not a
new peer value for `transform`.

## Usage

```python
from color.adaptation import chromatic_adaptation_XYZ
from color.constants import D50_XYZ, D65_XYZ

XYZ_D50 = chromatic_adaptation_XYZ(
    XYZ_D65,
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform="Bradford",
)
```

For the common workflow of preparing XYZ values for D65-referred spaces such as
Oklab, IPT and Jzazbz, use the D65 convenience helpers:

```python
from color.adaptation import adapt_from_D65, adapt_to_D65
from color.constants import D50_XYZ

XYZ_D65_referred = adapt_to_D65(
    XYZ_D50,
    source_white_XYZ=D50_XYZ,
    transform="Bradford",
)

XYZ_D50 = adapt_from_D65(
    XYZ_D65_referred,
    target_white_XYZ=D50_XYZ,
    transform="Bradford",
)
```

`adapt_to_D65(...)` and `adapt_from_D65(...)` are thin wrappers around
`chromatic_adaptation_XYZ(...)`; they only fix one side of the whitepoint pair
to `D65_XYZ`.

`transform=None` performs no adaptation and returns a numeric copy. This is the
stimulus-matching path.

```python
same_XYZ = chromatic_adaptation_XYZ(
    XYZ,
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform=None,
)
```

For incomplete-adaptation workflows, use the Zhai and Luo 2018 two-step model
explicitly:

```python
from color.adaptation import chromatic_adaptation_Zhai2018

XYZ_target = chromatic_adaptation_Zhai2018(
    XYZ_source,
    source_white_XYZ=[109.85, 100.0, 35.585],
    target_white_XYZ=[95.047, 100.0, 108.883],
    D_source=0.9407,
    D_target=0.9800,
    baseline_white_XYZ=[100.0, 100.0, 100.0],
    transform="CAT02",
)
```

## Design Notes

Ordinary colour-space conversions do not automatically perform chromatic
adaptation. If a workflow needs to adapt between whitepoints, make that step
explicit:

```text
source space -> XYZ(source white)
XYZ(source white) -> chromatic_adaptation_XYZ(...)
XYZ(target white) -> target space
```

`RGB_to_RGB(...)` exposes a `chromatic_adaptation` option because RGB spaces
carry explicit media/display whitepoints. The generic `convert_color(...)`
remains a routing helper and does not perform hidden adaptation.
