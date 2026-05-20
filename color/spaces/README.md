# spaces

`color.spaces` contains colour-space conversion helpers built around XYZ.

Current v1 scope is intentionally narrow:

- RGB colour-space definitions.
- RGB transfer functions for common SDR spaces.
- `RGB <-> XYZ` conversions.
- sRGB convenience wrappers.

Lab, Luv, Oklab, chromatic adaptation, colour appearance models, PQ and HLG are
not part of this first RGB-focused version.

## Quick Start

```python
from color.spaces import RGB_to_XYZ, XYZ_to_RGB, sRGB_to_XYZ, XYZ_to_sRGB

XYZ = sRGB_to_XYZ([0.25, 0.50, 0.75])
RGB = XYZ_to_sRGB(XYZ)

XYZ_p3 = RGB_to_XYZ([0.25, 0.50, 0.75], colourspace="Display P3")
RGB_p3 = XYZ_to_RGB(XYZ_p3, colourspace="Display P3")
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
