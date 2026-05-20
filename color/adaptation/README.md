# adaptation

`color.adaptation` provides explicit chromatic adaptation helpers. It is a
standalone foundation module, not part of any single colour space.

The first version implements Von Kries style adaptation using four transforms:

- `Von Kries`
- `Bradford`
- `CAT02`
- `CAT16`

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
