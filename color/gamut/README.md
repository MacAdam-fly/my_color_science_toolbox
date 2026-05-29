# gamut

`color.gamut` computes display-primary feasibility, LCHab gamut boundaries,
gamut coverage, and standard object-colour gamuts such as Pointer's gamut.

The public `XYZ` scale follows the rest of the project: values are on the
`Y=100` reference scale.

## Scope

The module works with linear colour stimuli. It does not apply RGB transfer
functions, chromatic adaptation, colour appearance viewing conditions, display
calibration models, or spectral integration.

## Display Primaries

```python
from color.gamut import DisplayPrimaries

primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
```

`DisplayPrimaries.primaries_XYZ` has shape `(n, 3)`: each row is one primary
stimulus in `XYZ(Y=100)`.

## Primary Gamut Tests

```python
from color.gamut import is_within_primary_gamut

inside = is_within_primary_gamut([20, 30, 40], primaries)
```

For three primaries, `method="auto"` uses a direct matrix solve. For four or
more primaries, it builds the convex hull of all off/on primary combinations
and uses hull halfspaces for vectorised inside tests.

## Primary Weights

```python
from color.gamut import solve_primary_weights

weights = solve_primary_weights([20, 30, 40], primaries)
```

Three-primary displays have a unique solution. Multi-primary displays usually
have non-unique solutions; v1 uses `scipy.optimize.linprog` to find one
feasible solution.

## LCHab Boundary

```python
from color.gamut import compute_LCH_gamut_boundary

boundary = compute_LCH_gamut_boundary(
    "Rec.2020",
    L_values=range(0, 101, 5),
    hue_values=range(0, 361, 5),
    C_upper=260,
)
```

The boundary stores `C_max[L, h]`: the maximum displayable chroma for each
lightness and hue direction.

Useful conversions and summaries:

```python
boundary.to_LCHab()
boundary.to_Lab()
boundary.to_XYZ()
boundary.slice_L(50)

area = boundary.area_at_L(50)
volume = boundary.volume()
rings, L_steps = boundary.gamut_rings([25, 50, 75, 100])
```

`projected_ab()` and `projected_area()` collapse all lightness layers onto the
Lab `a*b*` plane. They are not xy chromaticity boundaries.

For display-primary xy geometry, use:

```python
xy_primary_hull = boundary.primary_xy_hull()
```

`primary_xy_hull()` is only available when the boundary has display primaries.

## xy Coverage

Coverage is directional:

```text
coverage(test, reference) = overlap(test, reference) / measure(reference)
```

Use `xy_gamut_coverage(...)` for display-primary inputs:

```python
from color.gamut import xy_gamut_coverage

xy_gamut_coverage("sRGB", "Rec.2020")
xy_gamut_coverage(primaries, "Rec.2020")
xy_gamut_coverage(primaries.primaries_XYZ, DisplayPrimaries.from_RGB_colourspace("Rec.2020").primaries_XYZ)
```

Use `*_from_xy` helpers when the data is already CIE xy points or an xy hull:

```python
from color.gamut import pointer_gamut_xy_boundary, xy_gamut_coverage_from_xy

rec2020_xy = [
    [0.708, 0.292],
    [0.170, 0.797],
    [0.131, 0.046],
]
pointer_xy = pointer_gamut_xy_boundary()

coverage = xy_gamut_coverage_from_xy(rec2020_xy, pointer_xy)
```

`*_from_xy` computes a convex hull from the xy points. Three-primary,
four-primary, and higher-primary xy sets can be passed directly.

## Lab Coverage

Use Lab volume coverage from precomputed `GamutBoundary` objects:

```python
from color.gamut import lab_gamut_coverage

coverage = lab_gamut_coverage(test_boundary, reference_boundary)
```

Lab coverage compares stored `C_max[L, h]` boundaries directly. If
`whitepoint_XYZ` differs, a `UserWarning` is emitted and no chromatic adaptation
is performed. If `L_values` or `hue_values` differ, a `UserWarning` is emitted
and the test boundary is interpolated onto the reference grid.

## Pointer Gamut

Pointer's gamut describes the empirical gamut of real surface colours. It is
not a display-primary gamut:

```python
from color.gamut import (
    is_within_pointer_gamut,
    pointer_gamut_boundary,
    pointer_gamut_xy_boundary,
)

pointer = pointer_gamut_boundary()
pointer_xy = pointer_gamut_xy_boundary()
inside = is_within_pointer_gamut([32.05, 41.31, 51.00])
```

`pointer_gamut_boundary()` returns a `GamutBoundary` with `primaries=None`, so
`primary_xy_hull()` is not available. `pointer_gamut_xy_boundary()` returns the
published 32-point Pointer xy boundary used by `colour`.
