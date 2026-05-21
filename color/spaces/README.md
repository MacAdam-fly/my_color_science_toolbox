# spaces

`color.spaces` contains colour-space conversion helpers built around XYZ.

Current scope is intentionally narrow:

- RGB colour-space definitions.
- RGB transfer functions for common SDR spaces.
- `RGB <-> XYZ` conversions.
- `RGB -> RGB` conversions with optional explicit chromatic adaptation.
- sRGB convenience wrappers.
- CIE `XYZ <-> xyY` conversions re-exported from `color.colorimetry`.
- CIE `Lab / Luv / UVW`, `Oklab`, and cylindrical `LCHab / LCHuv / Oklch`.
- `CAM02-UCS / CAM02-LCD / CAM02-SCD` and
  `CAM16-UCS / CAM16-LCD / CAM16-SCD` uniform colour spaces.
- A lightweight colour-space node registry for `XYZ`-centred routing.

Colour appearance models, PQ and HLG are not part of this version.

The implementation is grouped by responsibility:

```text
color.spaces.rgb          RGB standards, transfer functions and RGB <-> XYZ
color.spaces.basic        XYZ-connected spaces independent of appearance models
color.spaces.appearance   uniform spaces built from appearance-model correlates
```

The recommended user-facing import path is still the top-level `color.spaces`
package. The subpackages keep implementation ownership clear as the number of
spaces grows.

`color.spaces` uses CIE XYZ values on the `Y=100` reference scale. This matches
`color.colorimetry` spectral integration results and `color.appearance`
CIECAM02/CIECAM16 viewing conditions.

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
UVW = convert_color(XYZ, "XYZ", "UVW")

xyY_from_router = convert_color(XYZ, source="XYZ", target="xyY")
Lab = convert_color(XYZ, "XYZ", "Lab")
Oklch = convert_color(XYZ, "XYZ", "Oklch")
CAM02UCS = convert_color(XYZ, "XYZ", "CAM02-UCS")
CAM16UCS = convert_color(XYZ, "XYZ", "CAM16-UCS")
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

Registered RGB spaces are created from
`color.spaces.rgb.display_standards.RGB_COLOURSPACE_DEFINITIONS`, which
re-exports the authoritative constants from `color.constants.display_standards`.
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

## Lab, Luv, UVW, Oklab And LCH

`Lab` and `Luv` use a reference whitepoint as a space parameter:

```python
from color.constants import D50_XYZ
from color.spaces import Lab_to_XYZ, XYZ_to_Lab

Lab_D50 = XYZ_to_Lab(XYZ, whitepoint_XYZ=D50_XYZ)
XYZ_roundtrip = Lab_to_XYZ(Lab_D50, whitepoint_XYZ=D50_XYZ)
```

The default reference whitepoint is D65 on the `Y=100` scale:

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
    SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
)

Oklch = convert_color(
    LCHab_D50,
    SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
    "Oklch",
)
```

`Lab(D50) -> Luv(D65)` is a parameterized colour-space conversion. It is not
chromatic adaptation by itself. If the workflow needs appearance-preserving
whitepoint adaptation, explicitly adapt the intermediate XYZ values with
`color.adaptation`.

`UVW` is the historical CIE 1964 U*V*W* space. It is registered because it is a
complete three-channel space and can round-trip through XYZ, but it is mostly
useful for reproducing older references rather than as a modern perceptual
workhorse:

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

UVW = convert_color(XYZ, "XYZ", SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ))
XYZ_again = convert_color(UVW, SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ), "XYZ")
```

## xyY And The Conversion Registry

`xyY` is both a colour-space representation and a core colorimetry coordinate.
The formulas live in `color.colorimetry.chromaticity`; `color.spaces` re-exports
them so users can access them from the colour-space layer:

```python
from color.spaces import (
    XYZ_to_xyY,
    xyY_to_XYZ,
    XYZ_to_xy,
    xyY_to_xy,
    XYZ_to_uv1960,
    XYZ_to_upvp1976,
)
```

`xyY` is registered as a complete three-channel colour-space node because it can
round-trip through XYZ:

```text
XYZ <-> xyY
```

The two-channel `xy`, `uv1960` and `u'v'1976` coordinates are exposed only as
chromaticity projections. They are not registered as full colour-space nodes
because they lose luminance and cannot be converted back to XYZ without an
external `Y` value.

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

Lab_D50 = SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ)
Luv_D65 = SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ)

Luv = convert_color(Lab, Lab_D50, Luv_D65)
```

Plain strings are equivalent to `SpaceSpec("name")` and use that space's
defaults.

`convert_color(...)` never performs chromatic adaptation and does not accept a
`chromatic_adaptation` option. If a workflow needs adaptation between RGB
whitepoints, use `RGB_to_RGB(..., chromatic_adaptation=...)` or adapt XYZ
explicitly with `color.adaptation`.

Colour-space nodes are declared next to their implementation. Basic spaces
export their grouped nodes from `color.spaces.basic`; CAM02/CAM16 uniform
spaces export their grouped nodes from `color.spaces.appearance`.
`color.spaces.registry` collects those groups, checks name and alias conflicts,
and provides lookup helpers.

## CAM02-UCS, CAM02-LCD And CAM02-SCD

The CAM02 spaces are uniform colour spaces built on top of CIECAM02 appearance
correlates:

```text
XYZ -> CIECAM02 J, M, h -> CAM02 J'a'b'
CAM02 J'a'b' -> CIECAM02 J, M, h -> XYZ
```

They use the same `Y=100` XYZ scale as the rest of `color.spaces`:

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam = convert_color(
    XYZ,
    "XYZ",
    SpaceSpec("CAM02-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
)
XYZ_again = convert_color(
    cam,
    SpaceSpec("CAM02-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
    "XYZ",
)
```

`CAM02-UCS` is the general uniform space, while `CAM02-LCD` and `CAM02-SCD`
use Luo et al. 2006 coefficients tuned for larger and smaller colour
differences respectively.

## CAM16-UCS, CAM16-LCD And CAM16-SCD

The CAM16 spaces mirror the CAM02 uniform-space structure, but use CIECAM16
appearance correlates:

```text
XYZ -> CIECAM16 J, M, h -> CAM16 J'a'b'
CAM16 J'a'b' -> CIECAM16 J, M, h -> XYZ
```

The public colour-space names follow common usage and colour-science naming:
`CAM16-UCS`, `CAM16-LCD` and `CAM16-SCD`. The lower-level JMh helpers use the
project's appearance-model naming style, for example
`JMh_CIECAM16_to_CAM16UCS`.

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam = convert_color(
    XYZ,
    "XYZ",
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
)
XYZ_again = convert_color(
    cam,
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
    "XYZ",
)
```

`CAM16-UCS` is the general uniform space, while `CAM16-LCD` and `CAM16-SCD`
use Li et al. 2017 / Luo-style coefficients for larger and smaller colour
differences respectively.
