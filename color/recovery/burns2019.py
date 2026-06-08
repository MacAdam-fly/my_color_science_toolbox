"""Burns (2019) smoothest bounded reflectance recovery."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .solvers import solve_bounded_least_squares, validate_bounds


def _slope_difference_matrix(size: int) -> np.ndarray:
    """Return Burns' first-slope quadratic matrix."""
    if size < 2:
        raise ValueError("size must be at least 2")
    matrix = np.zeros((size, size), dtype=np.float64)
    diagonal = np.full(size, 4.0, dtype=np.float64)
    diagonal[0] = 2.0
    diagonal[-1] = 2.0
    off_diagonal = np.full(size - 1, -2.0, dtype=np.float64)
    rows = np.arange(size)
    matrix[rows, rows] = diagonal
    matrix[rows[:-1], rows[1:]] = off_diagonal
    matrix[rows[1:], rows[:-1]] = off_diagonal
    return matrix


def _validate_burns_bounds(bounds: Sequence[float]) -> None:
    """Validate that Method 3 is used with reflectance bounds [0, 1]."""
    lower, upper = validate_bounds(bounds)
    if not np.isclose(lower, 0.0) or not np.isclose(upper, 1.0):
        raise ValueError("Burns 2019 Method 3 supports only bounds=(0, 1)")


def _initial_z(target: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Return a stable initial ``z`` vector from a bounded linear solve."""
    initial = solve_bounded_least_squares(
        target.reshape(1, 3),
        matrix,
        bounds=(0.0, 1.0),
        smoothness=1e-6,
    )[0]
    clipped = np.clip(initial, 1e-6, 1.0 - 1e-6)
    return np.arctanh(2.0 * clipped - 1.0)


def _solve_single_burns2019(
    target: np.ndarray,
    matrix: np.ndarray,
    *,
    max_iterations: int,
    tolerance: float,
) -> np.ndarray:
    """Solve one target with Burns' Method 3 Newton system."""
    size = matrix.shape[1]
    black = np.zeros(3, dtype=np.float64)
    white = matrix @ np.ones(size, dtype=np.float64)
    if np.allclose(target, black, rtol=0.0, atol=tolerance):
        return np.zeros(size, dtype=np.float64)
    if np.allclose(target, white, rtol=1e-8, atol=max(tolerance, 1e-8)):
        return np.ones(size, dtype=np.float64)

    difference = _slope_difference_matrix(size)
    z = _initial_z(target, matrix)
    lagrange = np.zeros(3, dtype=np.float64)
    zero_block = np.zeros((3, 3), dtype=np.float64)

    for _iteration in range(max_iterations):
        tanh_z = np.tanh(z)
        reflectance = 0.5 * (tanh_z + 1.0)
        sech2 = 1.0 - tanh_z * tanh_z
        d1 = 0.5 * sech2
        d2 = sech2 * tanh_z

        projected_lagrange = matrix.T @ lagrange
        top = difference @ z + d1 * projected_lagrange
        bottom = matrix @ reflectance - target
        residual = np.concatenate((top, bottom))
        if np.max(np.abs(residual)) < tolerance:
            return reflectance

        top_right = d1[:, np.newaxis] * matrix.T
        top_left = difference - np.diag(d2 * projected_lagrange)
        jacobian = np.block(
            [
                [top_left, top_right],
                [top_right.T, zero_block],
            ]
        )
        try:
            delta = np.linalg.solve(jacobian, -residual)
        except np.linalg.LinAlgError as error:
            raise RuntimeError(
                "Burns 2019 reflectance recovery failed because the Newton "
                "system became singular; the target may be on or outside the "
                "object-colour solid boundary"
            ) from error
        z = z + delta[:size]
        lagrange = lagrange + delta[size:]

    raise RuntimeError(
        "Burns 2019 reflectance recovery did not converge within "
        f"{max_iterations} iterations"
    )


def solve_burns2019_reflectance(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    bounds: Sequence[float],
    smoothness: float | None = None,
    max_iterations: int = 50,
    tolerance: float = 1e-8,
) -> np.ndarray:
    """Solve Burns (2019) Method 3 bounded smooth reflectances.

    Method 3 minimises slope energy in ``atanh(2 * rho - 1)`` space and
    therefore guarantees reflectance values strictly inside ``(0, 1)`` for
    interior object colours. Black and white boundary targets are handled as
    explicit practical special cases.
    """
    del smoothness

    _validate_burns_bounds(bounds)
    iteration_count = int(max_iterations)
    if iteration_count <= 0:
        raise ValueError("max_iterations must be positive")
    tolerance_value = float(tolerance)
    if not np.isfinite(tolerance_value) or tolerance_value <= 0:
        raise ValueError("tolerance must be a finite positive value")

    recovered = [
        _solve_single_burns2019(
            np.asarray(target, dtype=np.float64),
            matrix,
            max_iterations=iteration_count,
            tolerance=tolerance_value,
        )
        for target in np.asarray(targets, dtype=np.float64)
    ]
    return np.asarray(recovered, dtype=np.float64)


__all__ = [
    "solve_burns2019_reflectance",
]
