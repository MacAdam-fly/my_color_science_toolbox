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
```

## Example 01 - RGB Colour-Space Conversion

Demonstrates RGB standard spaces, encoded RGB conversion, RGB-to-RGB routing and
xy gamut triangles.

Outputs:

- `01_rgb_gamuts_xy.png`
- `01_rgb_conversion_swatches.png`
- `01_rgb_coordinate_values.png`

## Example 02 - Colour-Space Chain

Demonstrates a longer conversion chain across basic spaces:

```text
sRGB -> XYZ -> Lab -> LCHab -> Luv -> LCHuv -> Oklab -> Oklch -> XYZ -> sRGB
```

It also shows `SpaceSpec` whitepoint parameters and derived `LCH` nodes.

Outputs:

- `02_space_chain_swatches.png`
- `02_lab_luv_oklab_planes.png`
- `02_chain_roundtrip_error.png`

## Example 03 - CAM Uniform Spaces

Compares CAM02 and CAM16 uniform spaces, including `UCS / LCD / SCD` variants,
long round trips back to sRGB, and Average/Dim viewing-condition shifts.

Outputs:

- `03_cam_uniform_roundtrip_swatches.png`
- `03_cam02_cam16_uniform_planes.png`
- `03_cam02_vs_cam16_coordinate_delta.png`
- `03_cam_viewing_condition_shift.png`

## Example 04 - Reference Accuracy

Compares non-appearance spaces against the local `colour` library and checks
`Jzazbz <-> JzCzhz` round-trip accuracy.

Covered groups:

- RGB
- xyY
- Lab / Luv / UVW
- Oklab / IPT / Jzazbz
- LCHab / LCHuv / JzCzhz

Output:

- `04_reference_accuracy_errors.png`

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
