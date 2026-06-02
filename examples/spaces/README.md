# spaces examples

These examples exercise the `color.spaces` API and write figures to
`examples/spaces/output/`.

Run from the project root:

```powershell
.\.venv\Scripts\python.exe examples\spaces\example_01_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\spaces\example_02_colourspace_chain.py
.\.venv\Scripts\python.exe examples\spaces\example_03_cam_uniform_spaces.py
.\.venv\Scripts\python.exe examples\spaces\example_04_reference_accuracy.py
.\.venv\Scripts\python.exe examples\spaces\example_05_conversion_paths.py
.\.venv\Scripts\python.exe examples\spaces\example_06_image_lchab_edit.py
.\.venv\Scripts\python.exe examples\spaces\example_07_custom_rgb_colourspace.py
```

## Example 01 - RGB Colour-Space Conversion

Demonstrates RGB standard spaces, encoded RGB conversion, RGB-to-RGB routing and
xy gamut triangles.

Outputs:

- `01_rgb_gamuts_xy.png`
- `01_rgb_conversion_swatches.png`
- `01_rgb_coordinate_values.png`

## Example 02 - Long Closed Colour-Space Chain

Demonstrates a full long closed conversion chain across the current RGB,
basic and appearance-uniform spaces:

```text
sRGB -> XYZ -> xyY -> Lab/Luv/UVW -> Oklab/IPT/Jzazbz -> CAM02/CAM16 -> sRGB
```

It uses explicit D65/Y=100 `SpaceSpec` metadata so the chain can enter
D65-referred spaces without reference-domain warnings.

Outputs:

- `02_long_chain_swatches.png`
- `02_long_chain_planes.png`
- `02_long_chain_roundtrip_error.png`

## Example 03 - CAM Uniform Spaces

Compares CAM02 and CAM16 uniform spaces, including `UCS / LCD / SCD` variants,
long round trips back to sRGB, and Average/Dim viewing-condition shifts.

Outputs:

- `03_cam_uniform_roundtrip_swatches.png`
- `03_cam02_cam16_uniform_planes.png`
- `03_cam02_vs_cam16_coordinate_delta.png`
- `03_cam_viewing_condition_shift.png`

## Example 04 - D65 Whitepoint Semantics

Shows how D65 chromaticity, rounded RGB-standard D65 xy values and the project
`Y=100` reference domain differ. It also demonstrates the warning behaviour for
routes into D65-referred spaces such as Oklab, IPT and Jzazbz.

Covered cases:

- `D65_XYZ -> xy` versus rounded `(0.3127, 0.3290)`
- `D65_XYZ / 10`, `D65_XYZ` and `D65_XYZ * 2`
- `SpaceSpec("XYZ", whitepoint_XYZ=...) -> Oklab`
- `sRGB -> Jzazbz`, `DCI-P3 -> Oklab`
- explicit `adapt_to_D65(...)` before entering Oklab

Outputs:

- `04_d65_whitepoint_precision.png`
- `04_d65_reference_domain_scale.png`
- `04_d65_warning_cases.png`

## Example 05 - Conversion Paths

Prints and plots single conversion paths and the full registry-driven
conversion graph.

Single paths:

- `sRGB -> Display P3`
- `JzCzhz -> Lab`
- `sRGB -> CAM16-UCS`

Outputs:

- `05_path_srgb_to_display_p3.png`
- `05_path_jzczhz_to_lab.png`
- `05_path_srgb_to_cam16_ucs.png`
- `05_conversion_graph.png`

## Example 06 - Image LCHab Edit

Reads `input_test_img/img1.jpg` as encoded sRGB, converts every pixel to
`LCHab(D65)`, boosts `L*` and `C_ab` by `1.2`, clips the output sRGB values for
image export, and writes a JPEG result.

Outputs:

- `06_image_lchab_boost.jpg`
- `06_image_lchab_boost_comparison.png`

## Example 07 - Custom RGB Colourspace

Creates a custom three-primary RGB colour space, registers it manually, and
uses it in the same routing APIs as standard RGB spaces.

Demonstrates:

- `RGB_colourspace_from_primaries_xy(...)`
- `RGB_colourspace_from_primaries_XYZ(...)`
- `register_RGB_colourspace(...)`
- dynamic per-channel gamma, e.g. `("gamma", (2.2, 2.3, 2.1))`
- `RGB_to_XYZ(...)`, `XYZ_to_RGB(...)`, `RGB_to_RGB(...)`
- `convert_color(...)` and `describe_conversion_path(...)`

Outputs:

- `07_custom_rgb_conversion_swatches.png`
- `07_custom_rgb_dynamic_gamma.png`
