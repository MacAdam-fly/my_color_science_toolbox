"""Dictionary-based reflectance recovery."""

from __future__ import annotations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, minimize

from .library import ReflectanceLibrary


_DEFAULT_SOLVER_OPTIONS = {
    "ftol": 1e-10,
    "maxiter": 1000,
}


def _validate_regularization(value: float) -> float:
    """Return a valid dictionary regularisation strength."""
    regularization = float(value)
    if not np.isfinite(regularization) or regularization < 0:
        raise ValueError("dictionary_regularization must be finite and non-negative")
    return regularization


def _validate_top_k(value: int | None, sample_count: int) -> int:
    """Return the number of dictionary atoms to use for optimisation."""
    if value is None:
        return sample_count
    top_k = int(value)
    if top_k <= 0:
        raise ValueError("dictionary_top_k must be positive or None")
    return min(top_k, sample_count)


def _candidate_indices(
    response_matrix: np.ndarray,
    target: np.ndarray,
    top_k: int,
) -> np.ndarray:
    """Return nearest dictionary atoms in response space."""
    sample_count = response_matrix.shape[1]
    if top_k >= sample_count:
        return np.arange(sample_count)
    distances = np.linalg.norm(response_matrix.T - target, axis=1)
    indices = np.argpartition(distances, top_k - 1)[:top_k]
    return indices[np.argsort(distances[indices])]


def _solve_convex_weights(
    target: np.ndarray,
    responses: np.ndarray,
    regularization: float,
) -> np.ndarray:
    """Solve exact non-negative convex weights for candidate responses."""
    sample_count = responses.shape[1]
    initial = np.full(sample_count, 1.0 / sample_count, dtype=np.float64)
    bounds = Bounds(np.zeros(sample_count), np.ones(sample_count))
    constraint = LinearConstraint(
        np.ones((1, sample_count), dtype=np.float64),
        lb=np.array([1.0]),
        ub=np.array([1.0]),
    )

    def objective(weights: np.ndarray) -> float:
        residual = responses @ weights - target
        return float(residual @ residual + regularization * (weights @ weights))

    def jacobian(weights: np.ndarray) -> np.ndarray:
        residual = responses @ weights - target
        return 2.0 * (responses.T @ residual + regularization * weights)

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        jac=jacobian,
        bounds=bounds,
        constraints=(constraint,),
        options=_DEFAULT_SOLVER_OPTIONS,
    )
    if not result.success:
        raise ValueError(f"dictionary reflectance recovery failed: {result.message}")

    weights = np.clip(np.asarray(result.x, dtype=np.float64), 0.0, 1.0)
    weight_sum = np.sum(weights)
    if weight_sum <= 0:
        raise ValueError("dictionary reflectance recovery produced zero weights")
    return weights / weight_sum


def solve_dictionary_reflectance(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    library: ReflectanceLibrary,
    dictionary_regularization: float,
    dictionary_top_k: int | None,
) -> np.ndarray:
    """Recover reflectances as convex combinations of library samples."""
    regularization = _validate_regularization(dictionary_regularization)

    reflectances = np.asarray(library.reflectances, dtype=np.float64)
    if reflectances.shape[1] != matrix.shape[1]:
        raise ValueError(
            "library wavelength count must match recovery matrix columns, "
            f"got {reflectances.shape[1]} and {matrix.shape[1]}"
        )

    sample_count = reflectances.shape[0]
    if sample_count == 0:
        raise ValueError("library must contain at least one reflectance sample")

    top_k = _validate_top_k(dictionary_top_k, sample_count)
    response_matrix = matrix @ reflectances.T

    recovered = []
    for target in targets:
        target = np.asarray(target, dtype=np.float64)
        indices = _candidate_indices(response_matrix, target, top_k)
        weights = _solve_convex_weights(
            target,
            response_matrix[:, indices],
            regularization,
        )
        recovered.append(weights @ reflectances[indices])

    return np.asarray(recovered, dtype=np.float64)


__all__ = [
    "solve_dictionary_reflectance",
]
