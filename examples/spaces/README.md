# spaces examples

These examples exercise colour-space conversion helpers.

Run from the project root:

```powershell
.\.venv\Scripts\python.exe examples\spaces\example_01_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\spaces\example_02_colourspace_chain.py
.\.venv\Scripts\python.exe examples\spaces\example_03_cam02_uniform_spaces.py
```

Plots are written to `examples/spaces/output/`.

## Examples

- `example_01_rgb_colourspace_conversion.py` visualises RGB gamut triangles,
  RGB-to-RGB coordinate changes, and preview swatches for the same XYZ stimuli.
- `example_02_colourspace_chain.py` demonstrates a full conversion chain across
  `sRGB -> XYZ -> Lab -> Luv -> Oklab -> sRGB`, including `SpaceSpec`
  whitepoint parameters and derived `LCH` nodes.
- `example_03_cam02_uniform_spaces.py` demonstrates the long route
  `sRGB -> XYZ -> CAM02-UCS -> CAM02-LCD -> CAM02-SCD -> XYZ -> sRGB`, and
  visualises how CIECAM02 viewing conditions shift CAM02-UCS coordinates.
