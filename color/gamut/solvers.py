"""Primary-gamut inside tests and primary-weight solvers."""

from __future__ import annotations

from itertools import product
from typing import Sequence

import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

from color.utils.arrays import as_last_axis_triplets

from .primaries import DisplayPrimaries, as_display_primaries


def _resolve_method(method: str, count: int, *, for_weights: bool = False) -> str:
    """Resolve an algorithm name for a primary count."""
    key = method.lower().replace("_", "").replace("-", "")
    if key == "auto":
        return "matrix" if count == 3 else "linprog" if for_weights else "hull"
    if key in {"matrix", "hull", "linprog"}:
        return key
    raise ValueError("method must be one of: auto, matrix, hull, linprog")


def primary_gamut_vertices(
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
) -> np.ndarray:
    """Return the XYZ vertices from all off/on primary combinations."""
    display = as_display_primaries(primaries)
    weights = np.array(list(product((0.0, 1.0), repeat=display.count)), dtype=np.float64)
    return weights @ display.primaries_XYZ


def primary_gamut_halfspaces(
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
) -> np.ndarray:
    """Return convex-hull halfspaces for the primary gamut volume."""
    vertices = primary_gamut_vertices(primaries)
    hull = ConvexHull(vertices)
    return np.array(hull.equations, dtype=np.float64, copy=True)


def _matrix_weights(xyz: np.ndarray, display: DisplayPrimaries) -> np.ndarray:
    """Solve unique weights for a three-primary display."""
    if display.count != 3:
        raise ValueError("matrix method requires exactly three primaries")
    inverse = np.linalg.inv(display.primaries_XYZ)
    return xyz @ inverse


def _is_within_matrix(
    xyz: np.ndarray,
    display: DisplayPrimaries,
    tolerance: float,
) -> np.ndarray:
    """Return inside mask using unique three-primary weights."""
    weights = _matrix_weights(xyz, display)
    reconstructed = weights @ display.primaries_XYZ
    matches = np.all(np.abs(reconstructed - xyz) <= tolerance, axis=-1)
    in_bounds = np.all(
        (weights >= -tolerance) & (weights <= 1.0 + tolerance),
        axis=-1,
    )
    return matches & in_bounds


def _is_within_hull(
    xyz: np.ndarray,
    display: DisplayPrimaries,
    tolerance: float,
) -> np.ndarray:
    """Return inside mask using convex-hull halfspaces."""
    equations = primary_gamut_halfspaces(display)
    normals = equations[:, :3]
    offsets = equations[:, 3]
    flat = xyz.reshape(-1, 3)
    inside = np.all(flat @ normals.T + offsets <= tolerance, axis=-1)
    return inside.reshape(xyz.shape[:-1])


def is_within_primary_gamut(
    XYZ: Sequence[float] | np.ndarray,
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
    *,
    method: str = "auto",
    tolerance: float = 1e-9,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside a display-primary gamut.

    Parameters
    ----------
    XYZ
        XYZ values with final-axis shape ``(..., 3)`` in the same scale as the
        primary definitions.
    primaries
        Display primaries, RGB colour space name or raw primary XYZ rows.
    method
        ``"auto"`` uses a matrix solve for three primaries and convex-hull
        halfspaces for four or more primaries.
    tolerance
        Non-negative numerical tolerance for inside tests.

    Returns
    -------
    bool or ndarray
        Inside mask matching the leading shape of ``XYZ``.

    Notes
    -----
    This answers feasibility only: whether some bounded linear primary mixture
    can reproduce the XYZ. It does not choose an optimal drive strategy.

    Examples
    --------
    >>> is_within_primary_gamut([0.0, 0.0, 0.0], "sRGB")
    True
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    display = as_display_primaries(primaries)
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    resolved = _resolve_method(method, display.count)
    if resolved == "matrix":
        inside = _is_within_matrix(xyz, display, tolerance)
    elif resolved == "hull":
        inside = _is_within_hull(xyz, display, tolerance)
    else:
        flat = xyz.reshape(-1, 3)
        inside = np.array([
            _is_feasible_linprog_point(point, display)
            for point in flat
        ]).reshape(xyz.shape[:-1])
    inside = np.asarray(inside, dtype=bool)
    return inside[()] if inside.shape == () else inside


def _solve_linprog_point(
    XYZ: np.ndarray,
    display: DisplayPrimaries,
    objective: str,
) -> np.ndarray:
    """Solve one feasible primary-weight vector with linear programming."""
    key = objective.lower().replace("_", "").replace("-", "")
    if key != "minsum":
        raise ValueError("objective must be 'min_sum'")
    result = linprog(
        c=np.ones(display.count, dtype=np.float64),
        A_eq=display.primaries_XYZ.T,
        b_eq=XYZ,
        bounds=[(0.0, 1.0)] * display.count,
        method="highs",
    )
    if not result.success:
        raise ValueError("XYZ is outside the primary gamut; no feasible weights found")
    return np.asarray(result.x, dtype=np.float64)


def _is_feasible_linprog_point(XYZ: np.ndarray, display: DisplayPrimaries) -> bool:
    """Return whether one XYZ point has feasible primary weights."""
    result = linprog(
        c=np.zeros(display.count, dtype=np.float64),
        A_eq=display.primaries_XYZ.T,
        b_eq=XYZ,
        bounds=[(0.0, 1.0)] * display.count,
        method="highs",
    )
    return bool(result.success)


def solve_primary_weights(
    XYZ: Sequence[float] | np.ndarray,
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
    *,
    method: str = "auto",
    objective: str = "min_sum",
) -> np.ndarray:
    """Return bounded primary weights reproducing XYZ values.

    Parameters
    ----------
    XYZ
        XYZ values with final-axis shape ``(..., 3)``.
    primaries
        Display primaries, RGB colour space name or raw primary XYZ rows.
    method
        ``"auto"`` uses the unique matrix solve for three primaries and
        ``linprog`` for four or more primaries.
    objective
        Linear-programming objective for multi-primary solutions. Currently
        only ``"min_sum"`` is supported.

    Returns
    -------
    ndarray
        Weight array with final axis equal to the number of primaries.

    Notes
    -----
    Three-primary weights are unique if the primary matrix is valid.
    Multi-primary weights are generally not unique; this function returns one
    feasible solution, not a perceptual or device-optimal drive recipe.

    Examples
    --------
    >>> solve_primary_weights([0.0, 0.0, 0.0], "sRGB").shape
    (3,)
    """
    display = as_display_primaries(primaries)
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    resolved = _resolve_method(method, display.count, for_weights=True)
    if resolved == "matrix":
        return _matrix_weights(xyz, display)
    if resolved == "hull":
        raise ValueError("hull method only supports inside tests, not weight solving")

    flat = xyz.reshape(-1, 3)
    weights = np.vstack([
        _solve_linprog_point(point, display, objective)
        for point in flat
    ])
    return weights.reshape(*xyz.shape[:-1], display.count)


__all__ = [
    "is_within_primary_gamut",
    "solve_primary_weights",
    "primary_gamut_vertices",
    "primary_gamut_halfspaces",
]
