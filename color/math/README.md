# math

Purpose
- Numerical methods such as interpolation, extrapolation, fitting, and solvers.

Naming
- Use descriptive function names and avoid side effects.

Entry points
- Prefer `color.math.<module>`.

Current modules
- `interpolation`: one-dimensional interpolation helpers for spectral data.
- `extrapolation`: one-dimensional extrapolation helpers for spectral data.

Interpolation
- `interpolate_1d(x, y, target, method="auto")` supports `nearest`, `linear`,
  `cubic`, `pchip`, `sprague`, and `auto`.
- `auto` follows the same broad policy as `colour-science`: use Sprague for
  uniform data with at least 6 samples, cubic for non-uniform data with at
  least 4 samples, and linear otherwise.
- Sprague interpolation delegates to `colour.algebra.SpragueInterpolator` so
  the first implementation stays close to the reference library behavior.
- PCHIP uses SciPy's monotonicity-preserving piecewise cubic interpolator.

Extrapolation
- `extrapolate_1d(...)` evaluates in-domain samples with interpolation and
  handles out-of-domain samples with `constant`, `linear`, or `fill`.
- `left` and `right` can override the two extrapolated sides explicitly.
