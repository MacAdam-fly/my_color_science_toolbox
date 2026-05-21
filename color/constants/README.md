# constants

Purpose

- Authoritative home for important standard constants used by the project.
- High-level modules such as `color.spaces`, `color.colorimetry`,
  `color.appearance`, and `color.adaptation` should import shared standard
  constants from here.

Naming

- Use descriptive, lowercase names (snake_case) for constants.
- Group related constants in files like display_standards.py, standard_observer_matrices.py, illuminants_XYZ.py, adaptation_matrices.py.

Entry points

- `color.constants` is the main public entry point for common standard
  constants.
- Submodules such as `display_standards.py`, `adaptation_matrices.py`, and
  `standard_observer_matrices.py` group related constants by subject.

Semantic ownership

- Whitepoint and reference illuminant tristimulus constants such as `D65_XYZ`
  are defined in `illuminants_XYZ.py` because
  they are shared across colorimetry, spaces, appearance, and adaptation.
- RGB colour-space matrices and definitions are defined in
  `display_standards.py`.
- Standard-observer LMS/XYZ matrices are defined in
  `standard_observer_matrices.py`.
- Chromatic adaptation transform matrices are defined in `adaptation_matrices.py`:
  - `CAT_VON_KRIES`
  - `CAT_BRADFORD`
  - `CAT_CAT02`
  - `CAT_CAT16`
  - `CHROMATIC_ADAPTATION_TRANSFORMS`

RGB data policy

- `display_standards.py` keeps common compatibility matrix constants such as
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
- v1 RGB definitions cover SDR transfer identifiers such as `srgb`, `bt709`,
  `bt2020`, `gamma_2p6`, `adobe_rgb_1998`, and `linear`.
- PQ and HLG are intentionally not part of this v1 RGB definitions layer. They need
  HDR luminance and system-transfer semantics, so they should be added later in
  a dedicated HDR transfer design.
