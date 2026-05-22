# spaces

`color.spaces` is the colour-space layer of the project. It provides colour
space definitions, direct conversion functions, a lightweight `XYZ`-centred
router, and plotting helpers for inspecting conversion routes.

The public import path is intentionally simple:

```python
from color.spaces import convert_color, SpaceSpec
from color.spaces import RGB_to_XYZ, XYZ_to_RGB, RGB_to_RGB
from color.spaces import XYZ_to_Lab, Lab_to_XYZ
```

Internally, implementation is grouped by responsibility:

```text
color.spaces.rgb          RGB standards, transfer functions and RGB <-> XYZ
color.spaces.basic        XYZ-connected spaces independent of appearance models
color.spaces.appearance   uniform spaces built from appearance-model correlates
```

Appearance models themselves live in `color.appearance`; this package exposes
CAM02/CAM16 uniform colour spaces that are built from those appearance-model
correlates.

## Core Rules

- `XYZ` is the only global conversion hub.
- Public `XYZ` values use the `Y=100` scale.
- `SpaceSpec` carries endpoint-specific parameters such as Lab whitepoints or
  CAM viewing conditions.
- `convert_color(...)` never performs hidden chromatic adaptation.
- RGB standards are managed by their own `RGB_COLORSPACES` registry.
- Generic colour-space nodes are managed by `SPACE_REGISTRY`.
- `Oklab`, `IPT` and `Jzazbz` require D65-referred XYZ input.

If your XYZ values are not D65-referred, adapt them explicitly before using
`Oklab`, `IPT` or `Jzazbz`:

```python
from color.adaptation import adapt_from_D65, adapt_to_D65
from color.constants import D50_XYZ
from color.spaces import Oklab_to_XYZ, XYZ_to_Oklab

XYZ_D65_referred = adapt_to_D65(XYZ_D50, source_white_XYZ=D50_XYZ)
Oklab = XYZ_to_Oklab(XYZ_D65_referred)

XYZ_D50 = adapt_from_D65(Oklab_to_XYZ(Oklab), target_white_XYZ=D50_XYZ)
```

`convert_color(...)` does not adapt automatically. When a route is known to
cross a reference whitepoint that is not the project D65 reference domain into
or out of a D65-referred space, it emits a warning and continues. The check is
about both chromaticity and scale: `D65_XYZ / 10` has D65 chromaticity, but it
is not the spaces `Y=100` reference domain. You can attach whitepoint metadata
to the XYZ hub when you want this validation:

```python
from color.constants import D50_XYZ
from color.spaces import SpaceSpec, convert_color

Oklab = convert_color(
    XYZ_D50,
    SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ),  # warns: not D65-referred
    "Oklab",
)
```

## RGB

Registered RGB standards:

- `sRGB`
- `Rec.709`
- `Display P3`
- `DCI-P3`
- `Rec.2020`
- `Adobe RGB (1998)`
- `NTSC (1953)`

RGB conversion defaults to encoded RGB, which is the usual representation for
image and display values:

```python
from color.spaces import RGB_to_RGB, RGB_to_XYZ, XYZ_to_RGB

XYZ = RGB_to_XYZ([0.25, 0.50, 0.75], colourspace="sRGB")
RGB = XYZ_to_RGB(XYZ, colourspace="sRGB")
RGB_p3 = RGB_to_RGB([0.25, 0.50, 0.75], "sRGB", "Display P3")
```

Use `apply_decoding=False` only when the source RGB is already linear. Use
`apply_encoding=False` when you want linear RGB output:

```python
XYZ = RGB_to_XYZ(linear_rgb, colourspace="sRGB", apply_decoding=False)
linear_rgb = XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False)
```

RGB functions do not clip to `[0, 1]`. Out-of-gamut and intermediate values can
legitimately be below `0` or above `1`.

`RGB_to_RGB(...)` can explicitly apply a Von Kries style chromatic adaptation:

```python
RGB_target = RGB_to_RGB(
    RGB_source,
    "DCI-P3",
    "sRGB",
    chromatic_adaptation="Bradford",
)
```

Supported adaptation transforms are provided by `color.adaptation`: `Von Kries`,
`Bradford`, `CAT02` and `CAT16`.

## Basic Spaces

Current basic spaces and chromaticity helpers:

```text
XYZ <-> xyY
XYZ <-> Lab <-> LCHab
XYZ <-> Luv <-> LCHuv
XYZ <-> UVW
XYZ <-> Oklab <-> Oklch
XYZ <-> IPT
XYZ <-> Jzazbz <-> JzCzhz
xy, uv1960 and u'v'1976 helpers
```

Examples:

```python
from color.constants import D50_XYZ
from color.spaces import SpaceSpec, convert_color
from color.spaces import XYZ_to_Jzazbz, Jzazbz_to_JzCzhz

Lab_D50 = convert_color(XYZ, "XYZ", SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ))
Oklch = convert_color(XYZ_D65_referred, "XYZ", "Oklch")
JzCzhz = Jzazbz_to_JzCzhz(XYZ_to_Jzazbz(XYZ_D65_referred))
```

`xy`, `uv1960` and `u'v'1976` are exposed as chromaticity helpers, not full
registered colour-space nodes, because they do not contain luminance.

## Appearance Uniform Spaces

`CAM02-UCS / CAM02-LCD / CAM02-SCD` and
`CAM16-UCS / CAM16-LCD / CAM16-SCD` are registered as colour-space nodes. They
are not appearance models themselves; they wrap CIECAM02 or CIECAM16 `J, M, h`
correlates into uniform `J', a', b'` coordinates.

Use `SpaceSpec` for viewing-condition parameters:

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16 = convert_color(
    XYZ,
    "XYZ",
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
)
XYZ_again = convert_color(
    cam16,
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
    "XYZ",
)
```

`UCS` is the general-purpose uniform space. `LCD` and `SCD` use coefficients
tuned for larger and smaller colour differences.

## Conversion Routing

`convert_color(...)` routes through `XYZ` and keeps source and target parameters
separate:

```python
from color.constants import D50_XYZ, D65_XYZ
from color.spaces import SpaceSpec, convert_color

Luv = convert_color(
    Lab,
    SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
    SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
)
```

This means:

```text
Lab(D50) -> XYZ -> Luv(D65)
```

It is a parameterized colour-space conversion, not chromatic adaptation. If the
workflow needs adaptation, adapt the intermediate XYZ explicitly with
`color.adaptation`.

`convert_color(...)` rejects `chromatic_adaptation=...` by design. The only
high-level RGB function that accepts it is `RGB_to_RGB(...)`.

## Path Description And Plotting

Use `describe_conversion_path(...)` to inspect the route without converting
numeric colour values:

```python
from color.spaces import describe_conversion_path

path = describe_conversion_path("JzCzhz", "Lab")
for edge in path.edges:
    print(edge.source, "->", edge.target, edge.operation)
```

This reports:

```text
JzCzhz -> Jzazbz -> XYZ -> Lab
```

Use `plot_conversion_path(...)` for one route and `plot_conversion_graph(...)`
for the full registered graph:

```python
from color.spaces import plot_conversion_graph, plot_conversion_path

fig_path, ax_path = plot_conversion_path(path)
fig_graph, ax_graph = plot_conversion_graph()
```

The graph is registry-driven. New registered generic spaces or RGB standards
will appear the next time the plotting function is run.

## Registered Generic Nodes

```text
XYZ
xyY
Lab
LCHab
Luv
LCHuv
UVW
Oklab
Oklch
IPT
Jzazbz
JzCzhz
CAM02-UCS
CAM02-LCD
CAM02-SCD
CAM16-UCS
CAM16-LCD
CAM16-SCD
```
