# spaces examples

These examples exercise colour-space conversion helpers.

Run from the project root:

```powershell
.\.venv\Scripts\python.exe examples\spaces\example_01_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\spaces\example_02_colourspace_chain.py
```

Plots are written to `examples/spaces/output/`.

## Examples

- `example_01_rgb_colourspace_conversion.py` visualises RGB gamut triangles,
  RGB-to-RGB coordinate changes, and preview swatches for the same XYZ stimuli.
- `example_02_colourspace_chain.py` demonstrates a full conversion chain across
  `sRGB -> XYZ -> Lab -> Luv -> Oklab -> sRGB`, including `SpaceSpec`
  whitepoint parameters and derived `LCH` nodes.
