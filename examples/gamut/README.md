# gamut examples

Examples for display-primary feasibility, Lab/LCHab boundary metrics, 3D colour
solids, xy/Lab coverage, Pointer gamut, MacAdam limits, and high-level gamut
analysis.

## Run

```powershell
.\.venv\Scripts\python.exe examples\gamut\example_01_display_primary_gamut.py
.\.venv\Scripts\python.exe examples\gamut\example_02_lch_boundary_metrics.py
.\.venv\Scripts\python.exe examples\gamut\example_03_gamut_solids_3d.py
.\.venv\Scripts\python.exe examples\gamut\example_04_projected_plane_and_rings.py
.\.venv\Scripts\python.exe examples\gamut\example_05_gamut_coverage.py
.\.venv\Scripts\python.exe examples\gamut\example_06_pointer_gamut.py
.\.venv\Scripts\python.exe examples\gamut\example_07_macadam_limits.py
.\.venv\Scripts\python.exe examples\gamut\example_08_computed_macadam_limits.py
.\.venv\Scripts\python.exe examples\gamut\example_09_gamut_analysis.py
```

## Example 01: Display Primary Gamut

`example_01_display_primary_gamut.py`

Demonstrates point-level display-primary feasibility:

- resolve RGB colour-space primaries;
- test whether XYZ values are inside sRGB / Display P3 / Rec.2020;
- solve primary weights for RGB and a synthetic RGBC display;
- show that multi-primary weights are usually non-unique.

This example is about feasibility. It is not a full multi-primary display
driving strategy.

## Example 02: LCH Boundary Metrics

`example_02_lch_boundary_metrics.py`

Computes `GamutBoundary` objects and compares:

- fixed `L*=50` Lab `a*b*` boundary slices;
- slice area;
- approximate Lab volume;
- projected Lab `a*b*` plane area.

Output:

```text
examples/gamut/output/02_lch_boundary_L50_comparison.png
```

## Example 03: 3D Lab Colour Solids

`example_03_gamut_solids_3d.py`

Uses `boundary.to_Lab()` with 3D plotting primitives:

- `plot_3d_surface`;
- `plot_3d_wireframe`;
- `set_3d_axis_limits_from_data`.

Output:

```text
examples/gamut/output/03_lab_colour_solids_3d.png
```

## Example 04: Projected Plane And Rings

`example_04_projected_plane_and_rings.py`

Compares display gamuts in several views:

- CIE 1931 xy comparison using `boundary.xy_boundary()`;
- polar LCHab comparison of projected maximum chroma by hue;
- projected Lab `a*b*` plane-gamut comparison;
- one fixed `L*=50` boundary slice shown in xy, polar LCHab, and Lab `a*b*`;
- cumulative `gamut_rings(...)`.

Outputs:

```text
examples/gamut/output/04_projected_plane_comparison_subplots.png
examples/gamut/output/04_gamut_rings_comparison.png
```

The xy subplot uses `xy_boundary()`. It does not use Lab projected boundaries
converted into xy.

## Example 05: Gamut Coverage

`example_05_gamut_coverage.py`

Compares directional gamut coverage:

- xy area coverage from primary chromaticity hulls;
- Lab volume coverage from precomputed `GamutBoundary` objects;
- heatmap matrices where rows are test gamuts and columns are reference gamuts.

Output:

```text
examples/gamut/output/05_gamut_coverage_matrices.png
```

## Example 06: Pointer Gamut

`example_06_pointer_gamut.py`

Demonstrates Pointer's real-surface colour gamut:

- loads Pointer as a `PointerGamutBoundary`;
- prints Pointer whitepoint, grid and Lab volume;
- compares display Lab volume coverage of Pointer;
- compares display xy area coverage of Pointer's published xy boundary;
- plots Pointer projected `a*b*` against display projected plane gamuts;
- plots Pointer's published 32-point xy boundary against display primary hulls.

Output:

```text
examples/gamut/output/06_pointer_gamut_comparison.png
```

## Example 07: MacAdam Limits

`example_07_macadam_limits.py`

Demonstrates cached A / C / D65 MacAdam optimal-colour limits:

- loads MacAdam limits through `macadam_limits(...)`;
- compares their xy boundaries on the CIE 1931 diagram;
- resamples MacAdam D65 as a `MacAdamLimitsBoundary`;
- compares MacAdam D65, Pointer, sRGB and Rec.2020 in projected Lab `a*b*`;
- demonstrates `is_within_macadam_limits(...)`.

Output:

```text
examples/gamut/output/07_macadam_limits_comparison.png
```

## Example 08: Computed MacAdam Limits

`example_08_computed_macadam_limits.py`

Demonstrates the computed MacAdam route:

- forces `source="computed"` to use the L*-derived brightness-factor method;
- compares computed D65 against the cached D65 table in xy and projected Lab `a*b*`;
- computes a custom D-series daylight case not available as a cached table;
- shows one fixed `L*=50` chroma boundary;
- prints computed vertex counts and sample generated data rows.

Output:

```text
examples/gamut/output/08_computed_macadam_limits.png
```

## Example 09: Gamut Analysis

`example_09_gamut_analysis.py`

Runs the high-level `analyze_gamut(...)` summary:

- analyses sRGB / Display P3 / Rec.2020 / RGBC;
- prints xy area, Lab volume, and coverage against Rec.2020 / Pointer / D65 MacAdam;
- plots xy and Lab coverage bars.

Output:

```text
examples/gamut/output/09_gamut_analysis_summary.png
```
