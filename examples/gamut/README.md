# gamut examples

Examples for display-primary gamut feasibility, LCH boundary metrics, 3D colour
solids, projected plane gamuts, gamut rings and coverage.

## Run

```powershell
.\.venv\Scripts\python.exe examples\gamut\example_01_display_primary_gamut.py
.\.venv\Scripts\python.exe examples\gamut\example_02_lch_boundary_metrics.py
.\.venv\Scripts\python.exe examples\gamut\example_03_gamut_solids_3d.py
.\.venv\Scripts\python.exe examples\gamut\example_04_projected_plane_and_rings.py
.\.venv\Scripts\python.exe examples\gamut\example_05_gamut_coverage.py
.\.venv\Scripts\python.exe examples\gamut\example_06_pointer_gamut.py
```

## Examples

`example_01_display_primary_gamut.py`

Demonstrates the point-level display-primary problem:

- resolve RGB colour-space primaries;
- check whether XYZ values are inside sRGB / Display P3 / Rec.2020;
- solve primary weights for RGB and a synthetic RGBC display;
- show that multi-primary weights are usually non-unique.

`example_02_lch_boundary_metrics.py`

Computes `GamutBoundary` objects and compares:

- fixed `L*=50` Lab `a*b*` boundary slices;
- slice area;
- approximate Lab volume;
- projected plane-gamut area.

Output:

```text
examples/gamut/output/02_lch_boundary_L50_comparison.png
```

`example_03_gamut_solids_3d.py`

Uses `boundary.to_Lab()` with the 3D plot primitives:

- `plot_3d_surface`;
- `plot_3d_wireframe`;
- `set_3d_axis_limits_from_data`.

Output:

```text
examples/gamut/output/03_lab_colour_solids_3d.png
```

`example_04_projected_plane_and_rings.py`

Shows how the 3D LCH boundary collapses to plane-gamut summaries:

- CIE 1931 xy comparison of the exact primary chromaticity hull;
- polar `LCHab` comparison of projected maximum chroma by hue;
- projected Lab `a*b*` plane-gamut comparison;
- one fixed `L*=50` boundary slice shown in xy, polar `LCHab`, and Lab `a*b*`;
- cumulative `gamut_rings(...)`.

Outputs:

```text
examples/gamut/output/04_projected_plane_comparison_subplots.png
examples/gamut/output/04_gamut_rings_comparison.png
```

`example_05_gamut_coverage.py`

Compares directional gamut coverage:

- xy area coverage from primary chromaticity hulls;
- Lab volume coverage from precomputed `GamutBoundary` objects;
- heatmap matrices where each row is the test gamut and each column is the reference gamut.

Output:

```text
examples/gamut/output/05_gamut_coverage_matrices.png
```

`example_06_pointer_gamut.py`

Demonstrates Pointer's real-surface colour gamut:

- loads Pointer as a `GamutBoundary`;
- prints Pointer whitepoint, grid and Lab volume;
- compares sRGB / RGBC / Rec.2020 Lab volume coverage of Pointer;
- compares sRGB / Rec.2020 xy area coverage of Pointer's published xy boundary;
- plots Pointer projected `a*b*` against display projected plane gamuts;
- plots Pointer's published 32-point xy boundary against display primary hulls on the CIE 1931 diagram.

Output:

```text
examples/gamut/output/06_pointer_gamut_comparison.png
```
