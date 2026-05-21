# spaces examples

These examples exercise colour-space conversion helpers.

Run from the project root:

```powershell
.\.venv\Scripts\python.exe examples\spaces\example_01_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\spaces\example_02_colourspace_chain.py
.\.venv\Scripts\python.exe examples\spaces\example_03_cam_uniform_spaces.py
```

Plots are written to `examples/spaces/output/`.

## Examples

- `example_01_rgb_colourspace_conversion.py` visualises RGB gamut triangles,
  RGB-to-RGB coordinate changes, and preview swatches for the same XYZ stimuli.
- `example_02_colourspace_chain.py` demonstrates a full conversion chain across
  `sRGB -> XYZ -> Lab -> Luv -> Oklab -> sRGB`, including `SpaceSpec`
  whitepoint parameters and derived `LCH` nodes.
- `example_03_cam_uniform_spaces.py` compares CAM02 and CAM16 uniform spaces,
  demonstrates long routes through `UCS / LCD / SCD`, and visualises model
  differences plus Average/Dim surround shifts.

`example_03_cam_uniform_spaces.py` writes:

- `03_cam_uniform_roundtrip_swatches.png`
- `03_cam02_cam16_uniform_planes.png`
- `03_cam02_vs_cam16_coordinate_delta.png`
- `03_cam_viewing_condition_shift.png`
