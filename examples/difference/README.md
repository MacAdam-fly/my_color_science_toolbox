# Difference Examples

These examples show how to use `color.difference` after coordinates have been
prepared in the correct colour space. The difference module does not perform
colour-space conversion itself.

Run all scripts from the project root:

```powershell
.\.venv\Scripts\python.exe examples\difference\example_01_lab_delta_e.py
.\.venv\Scripts\python.exe examples\difference\example_02_appearance_delta_e.py
.\.venv\Scripts\python.exe examples\difference\example_03_modern_space_delta_e.py
```

## 01 Lab Delta E

`example_01_lab_delta_e.py`

Demonstrates:

- Direct Lab inputs.
- `CIE 1976`, `CIE 1994`, `CIE 2000` and `CMC`.
- Explicit `sRGB -> Lab` conversion with `SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ)`.
- Method dispatch with `delta_E(..., method="CIEDE2000")`.

Use this example when comparing standard Lab colour-difference formulae.

## 02 Appearance Delta E

`example_02_appearance_delta_e.py`

Demonstrates:

- `sRGB -> CAM02-UCS/LCD/SCD -> delta_E_CAM02*`.
- `sRGB -> CAM16-UCS/LCD/SCD -> delta_E_CAM16*`.
- Changing CAM viewing conditions during `color.spaces` conversion.
- Method dispatch with `delta_E(..., method="CAM16UCS")`.

Use this example when comparing colour differences in CAM02/CAM16 uniform
spaces.

## 03 Modern Space Delta E

`example_03_modern_space_delta_e.py`

Demonstrates:

- `sRGB -> Oklab -> delta_E_Oklab`.
- `sRGB -> Jzazbz -> delta_E_Jzazbz`.
- Method dispatch with `delta_E(..., method="OKLAB")`.
- The fact that these values are direct coordinate distances, not CIE standard
  Delta E formulae.

Use this example when you want a lightweight distance in Oklab or Jzazbz.
