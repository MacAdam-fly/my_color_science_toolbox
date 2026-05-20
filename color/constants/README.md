# constants

Purpose
- Immutable matrices, white points, and standard primaries.
- RGB colour-space standard data used to seed future `color.spaces.rgb`
  registration.

Naming
- Use descriptive, lowercase names (snake_case) for constants.
- Group related constants in files like display_matrices.py, standard_observer_matrices.py, illuminants.py.

Entry points
- Prefer imports via color.constants.<module>.

RGB data policy
- `display_matrices.py` keeps common compatibility matrix constants such as
  `SRGB_TO_XYZ` and `XYZ_TO_SRGB`.
- `RGB_COLOURSPACE_DEFINITIONS` is the canonical RGB standards table. Each
  definition contains:
  - `name`
  - `aliases`
  - `primaries`
  - `white_xy`
  - `white_name`
  - `transfer`
  - `matrix_RGB_to_XYZ`
  - `matrix_XYZ_to_RGB`
  - `reference`
- `RGB_GAMUT_METADATA` is kept only as a backwards-compatible alias to the new
  definition table; it no longer has the old coarse `gamma` field.
- v1 RGB constants cover SDR transfer identifiers such as `srgb`, `bt709`,
  `bt2020`, `gamma_2p6`, `adobe_rgb_1998`, and `linear`.
- PQ and HLG are intentionally not part of this v1 constants layer. They need
  HDR luminance and system-transfer semantics, so they should be added later in
  a dedicated HDR transfer design.
