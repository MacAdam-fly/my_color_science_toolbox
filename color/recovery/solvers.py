"""Numerical solvers for spectral recovery."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.optimize import lsq_linear


def validate_bounds(bounds: Sequence[float]) -> tuple[float, float]:
    """Validate solver bounds."""
    if len(bounds) != 2:
        raise ValueError("bounds must contain exactly two values")
    lower, upper = (float(bounds[0]), float(bounds[1]))
    if not np.isfinite(lower):
        raise ValueError("bounds lower value must be finite")
    if np.isnan(upper):
        raise ValueError("bounds upper value must not be NaN")
    if upper <= lower:
        raise ValueError("bounds lower value must be less than upper value")
    return lower, upper


def second_difference_matrix(size: int) -> np.ndarray:
    """Return a second-difference matrix with shape ``(size - 2, size)``."""
    if size < 3:
        raise ValueError("size must be at least 3 for a second-difference matrix")
    matrix = np.zeros((size - 2, size), dtype=np.float64)
    rows = np.arange(size - 2)
    matrix[rows, rows] = 1.0
    matrix[rows, rows + 1] = -2.0
    matrix[rows, rows + 2] = 1.0
    return matrix


def solve_bounded_least_squares(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    bounds: Sequence[float],
    smoothness: float,
) -> np.ndarray:
    """Solve bounded smooth spectra for all target rows."""
    lower, upper = validate_bounds(bounds)
    smoothness_value = float(smoothness)
    if not np.isfinite(smoothness_value) or smoothness_value < 0:
        raise ValueError("smoothness must be a finite non-negative value")

    if smoothness_value > 0:
        difference = second_difference_matrix(matrix.shape[1])
        lhs = np.vstack((matrix, np.sqrt(smoothness_value) * difference))
        zero_tail = np.zeros(difference.shape[0], dtype=np.float64)
    else:
        lhs = matrix
        zero_tail = np.empty(0, dtype=np.float64)

    recovered = []
    for target in targets:
        rhs = np.concatenate((target, zero_tail))
        result = lsq_linear(lhs, rhs, bounds=(lower, upper))
        recovered.append(result.x)
    return np.asarray(recovered, dtype=np.float64)


__all__ = [
    "validate_bounds",
    "second_difference_matrix",
    "solve_bounded_least_squares",
]
