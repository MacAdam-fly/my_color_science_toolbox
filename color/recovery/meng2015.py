"""Meng et al. (2015) reflectance recovery."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.optimize import Bounds, minimize

from .solvers import solve_bounded_least_squares, validate_bounds


def _first_difference_matrix(size: int) -> np.ndarray:
    """Return a first-difference matrix with shape ``(size - 1, size)``."""
    if size < 2:
        raise ValueError("size must be at least 2 for a first-difference matrix")
    matrix = np.zeros((size - 1, size), dtype=np.float64)
    rows = np.arange(size - 1)
    matrix[rows, rows] = -1.0
    matrix[rows, rows + 1] = 1.0
    return matrix


def solve_meng2015_reflectance(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    bounds: Sequence[float],
    smoothness: float | None = None,
) -> np.ndarray:
    """Solve Meng et al. (2015) smooth reflectances for all target rows.

    The optimisation minimises adjacent reflectance differences while enforcing
    exact tristimulus closure through equality constraints.
    """
    del smoothness

    lower, upper = validate_bounds(bounds)
    difference = _first_difference_matrix(matrix.shape[1])
    hessian = difference.T @ difference
    variable_bounds = Bounds(
        np.full(matrix.shape[1], lower, dtype=np.float64),
        np.full(matrix.shape[1], upper, dtype=np.float64),
    )

    def objective(values: np.ndarray) -> float:
        return float(values @ hessian @ values)

    def objective_jacobian(values: np.ndarray) -> np.ndarray:
        return 2.0 * hessian @ values

    recovered = []
    for target in np.asarray(targets, dtype=np.float64):
        initial = solve_bounded_least_squares(
            target.reshape(1, 3),
            matrix,
            bounds=(lower, upper),
            smoothness=0.0,
        )[0]

        constraints = {
            "type": "eq",
            "fun": lambda values, target=target: matrix @ values - target,
            "jac": lambda values: matrix,
        }
        result = minimize(
            objective,
            initial,
            method="SLSQP",
            jac=objective_jacobian,
            bounds=variable_bounds,
            constraints=constraints,
            options={"ftol": 1e-10, "maxiter": 1000},
        )
        if not result.success:
            raise RuntimeError(
                "Meng 2015 optimisation failed after "
                f"{result.nit} iterations: {result.message}"
            )
        recovered.append(result.x)

    return np.asarray(recovered, dtype=np.float64)


__all__ = [
    "solve_meng2015_reflectance",
]
