# spaces

`color.spaces` contains colour-space conversion helpers built around XYZ.

Current scope is intentionally narrow:

- RGB colour-space definitions.
- RGB transfer functions for common SDR spaces.
- `RGB <-> XYZ` conversions.
- `RGB -> RGB` conversions with optional explicit chromatic adaptation.
- sRGB convenience wrappers.
- CIE `XYZ <-> xyY` conversions re-exported from `color.colorimetry`.
- CIE `Lab / Luv`, `Oklab`, and cylindrical `LCHab / LCHuv / Oklch`.
- A lightweight colour-space node registry for `XYZ`-centred routing.

Colour appearance models, PQ and HLG are not part of this version.

## Quick Start

```python
from color.spaces import RGB_to_RGB, RGB_to_XYZ, XYZ_to_RGB, sRGB_to_XYZ, XYZ_to_sRGB
from color.spaces import SpaceSpec, XYZ_to_xyY, xyY_to_XYZ, convert_color

XYZ = sRGB_to_XYZ([0.25, 0.50, 0.75])
RGB = XYZ_to_sRGB(XYZ)

XYZ_p3 = RGB_to_XYZ([0.25, 0.50, 0.75], colourspace="Display P3")
RGB_p3 = XYZ_to_RGB(XYZ_p3, colourspace="Display P3")
RGB_display_p3 = RGB_to_RGB([0.25, 0.50, 0.75], "sRGB", "Display P3")

xyY = XYZ_to_xyY(XYZ)
XYZ_roundtrip = xyY_to_XYZ(xyY)

xyY_from_router = convert_color(XYZ, source="XYZ", target="xyY")
Lab = convert_color(XYZ, "XYZ", "Lab")
Oklch = convert_color(XYZ, "XYZ", "Oklch")
xyY_with_fallback = convert_color(
    [0.0, 0.0, 0.0],
    source="XYZ",
    target=SpaceSpec("xyY", fallback_xy=(0.3127, 0.3290)),
)
```

By default, RGB inputs and outputs are encoded values. Use
`apply_decoding=False` or `apply_encoding=False` for linear RGB:

```python
XYZ = RGB_to_XYZ(linear_rgb, colourspace="sRGB", apply_decoding=False)
linear_rgb = XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False)
```

## Encoded RGB And Linear RGB

`RGB_to_XYZ(...)` applies transfer decoding by default:

```text
encoded RGB -> linear RGB -> XYZ
```

This is the correct choice for ordinary image or display RGB values, such as
standard sRGB pixel values in `[0, 1]`. For example, encoded sRGB `0.5` is not
half linear light; it is decoded to a smaller linear value before the RGB to XYZ
matrix is applied.

Set `apply_decoding=False` only when the input is already linear RGB:

```python
XYZ = RGB_to_XYZ(linear_rgb, colourspace="sRGB", apply_decoding=False)
```

In that case the function skips the transfer function and directly applies the
RGB-to-XYZ matrix.

`XYZ_to_RGB(...)` mirrors this behaviour. By default it returns encoded RGB:

```text
XYZ -> linear RGB -> encoded RGB
```

Set `apply_encoding=False` when you want the intermediate linear RGB values
instead of display/image-ready encoded values:

```python
linear_rgb = XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False)
```

The conversion functions do not clip RGB values to `[0, 1]`. Out-of-gamut or
intermediate calculations can legitimately produce values below `0` or above
`1`; clipping should be a separate, explicit decision by the caller.

## RGB API

```python
from color.spaces import (
    RGBColorSpace,
    RGB_COLORSPACES,
    get_RGB_colourspace,
    list_RGB_colourspaces,
    RGB_to_XYZ,
    XYZ_to_RGB,
    RGB_to_RGB,
    sRGB_to_XYZ,
    XYZ_to_sRGB,
)
```

Registered RGB spaces are created from `color.constants.RGB_COLOURSPACE_DEFINITIONS`.
The first set includes:

- `sRGB`
- `Rec.709`
- `Display P3`
- `DCI-P3`
- `Rec.2020`
- `Adobe RGB (1998)`
- `NTSC (1953)`

`RGB_to_RGB(...)` converts through XYZ:

```text
source RGB -> source XYZ -> target RGB
```

By default, it does not perform chromatic adaptation. This is the
stimulus-matching path:

```python
RGB_target = RGB_to_RGB(RGB_source, "DCI-P3", "sRGB")
```

When you explicitly want source-white to target-white adaptation, pass a Von
Kries style transform:

```python
RGB_target = RGB_to_RGB(
    RGB_source,
    "DCI-P3",
    "sRGB",
    chromatic_adaptation="Bradford",
)
```

Supported adaptation transforms live in `color.adaptation`: `Von Kries`,
`Bradford`, `CAT02` and `CAT16`.

## Transfer Functions

Supported v1 transfer identifiers:

- `linear`
- `srgb`
- `gamma_2p6`
- `gamma_2p8`
- `adobe_rgb_1998`
- `bt709`
- `bt2020`

PQ and HLG are left for a later HDR transfer module because they require
additional absolute or system luminance semantics.

## Lab, Luv, Oklab And LCH

`Lab` and `Luv` use a reference whitepoint as a space parameter:

```python
from color.constants import D50_XYZ
from color.spaces import Lab_to_XYZ, XYZ_to_Lab

Lab_D50 = XYZ_to_Lab(XYZ, whitepoint_XYZ=D50_XYZ / 100)
XYZ_roundtrip = Lab_to_XYZ(Lab_D50, whitepoint_XYZ=D50_XYZ / 100)
```

The default reference whitepoint is relative D65:

```python
from color.spaces import DEFAULT_WHITEPOINT_XYZ
```

`Oklab` does not take a whitepoint parameter:

```python
Oklab = convert_color(XYZ, "XYZ", "Oklab")
Oklch = convert_color(XYZ, "XYZ", "Oklch")
```

The cylindrical spaces are registered as derived nodes:

```text
LCHab -> Lab -> XYZ
LCHuv -> Luv -> XYZ
Oklch -> Oklab -> XYZ
```

This lets `convert_color(...)` route between derived spaces:

```python
from color.constants import D50_XYZ
from color.spaces import SpaceSpec, convert_color

LCHab_D50 = convert_color(
    XYZ,
    "XYZ",
    SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ / 100),
)

Oklch = convert_color(
    LCHab_D50,
    SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ / 100),
    "Oklch",
)
```

`Lab(D50) -> Luv(D65)` is a parameterized colour-space conversion. It is not
chromatic adaptation by itself. If the workflow needs appearance-preserving
whitepoint adaptation, explicitly adapt the intermediate XYZ values with
`color.adaptation`.

## xyY And The Conversion Registry

`xyY` is both a colour-space representation and a core colorimetry coordinate.
The formulas live in `color.colorimetry.chromaticity`; `color.spaces` re-exports
them so users can access them from the colour-space layer:

```python
from color.spaces import XYZ_to_xyY, xyY_to_XYZ, XYZ_to_xy, xyY_to_xy
```

`xyY` is registered as a complete three-channel colour-space node because it can
round-trip through XYZ:

```text
XYZ <-> xyY
```

The two-channel `xy` coordinate is exposed only as a chromaticity projection. It
is not registered as a full colour-space node because it loses luminance and
cannot be converted back to XYZ without an external `Y` value.

The generic conversion entry point supports `XYZ`, `xyY`, registered RGB
colour-space names, and parameterized `SpaceSpec` endpoints:

```python
from color.spaces import SpaceSpec, convert_color

xyY = convert_color(XYZ, "XYZ", "xyY")
XYZ = convert_color(xyY, "xyY", "XYZ")
XYZ = convert_color(RGB, "sRGB", "XYZ")
RGB = convert_color(xyY, "xyY", "Display P3")
RGB_p3 = convert_color(RGB, "sRGB", "Display P3")
```

Use `SpaceSpec` when a colour space needs endpoint-specific parameters:

```python
xyY = convert_color(
    [0.0, 0.0, 0.0],
    "XYZ",
    SpaceSpec("xyY", fallback_xy=(0.3127, 0.3290)),
)
```

The source and target endpoint parameters are kept separate. This matters for
future spaces such as `Lab(D50) -> Luv(D65)`, where the source conversion and
target conversion must use different reference whites:

```python
from color.constants import D50_XYZ, D65_XYZ

Lab_D50 = SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ / 100)
Luv_D65 = SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ / 100)

Luv = convert_color(Lab, Lab_D50, Luv_D65)
```

Plain strings are equivalent to `SpaceSpec("name")` and use that space's
defaults.

`convert_color(...)` never performs chromatic adaptation and does not accept a
`chromatic_adaptation` option. If a workflow needs adaptation between RGB
whitepoints, use `RGB_to_RGB(..., chromatic_adaptation=...)` or adapt XYZ
explicitly with `color.adaptation`.

Colour-space nodes are declared next to their implementation. For example,
`color.spaces.xyy`, `color.spaces.lab`, `color.spaces.luv` and
`color.spaces.oklab` expose `SPACE_NODES`; `color.spaces.registry` collects
node groups, checks name and alias conflicts, and provides lookup helpers.
