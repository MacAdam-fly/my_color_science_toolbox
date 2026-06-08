"""Dictionary-based reflectance recovery."""

from __future__ import annotations

import numpy as np
from scipy.optimize import lsq_linear

from .library import ReflectanceLibrary


_SUM_CONSTRAINT_WEIGHT = 1e6


def _validate_regularization(value: float) -> float:
    """Return a valid dictionary regularisation strength."""
    regularization = float(value)
    if not np.isfinite(regularization) or regularization < 0:
        raise ValueError("dictionary_regularization must be finite and non-negative")
    return regularization


def solve_dictionary_reflectance(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    library: ReflectanceLibrary,
    dictionary_regularization: float,
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

    response_matrix = matrix @ reflectances.T
    sqrt_sum_weight = np.sqrt(_SUM_CONSTRAINT_WEIGHT)
    sqrt_regularization = np.sqrt(regularization)
    lhs_blocks = [
        response_matrix,
        sqrt_sum_weight * np.ones((1, sample_count), dtype=np.float64),
    ]
    if regularization > 0:
        lhs_blocks.append(sqrt_regularization * np.eye(sample_count, dtype=np.float64))
    lhs = np.vstack(lhs_blocks)
    zero_tail = (
        np.zeros(sample_count, dtype=np.float64)
        if regularization > 0
        else np.empty(0, dtype=np.float64)
    )

    recovered = []
    for target in targets:
        target = np.asarray(target, dtype=np.float64)
        rhs = np.concatenate(
            (
                target,
                np.array([sqrt_sum_weight], dtype=np.float64),
                zero_tail,
            )
        )
        result = lsq_linear(lhs, rhs, bounds=(0.0, 1.0))
        if not result.success:
            raise ValueError(
                f"dictionary reflectance recovery failed: {result.message}"
            )
        weights = np.asarray(result.x, dtype=np.float64)
        weight_sum = np.sum(weights)
        if weight_sum <= 0:
            raise ValueError("dictionary reflectance recovery produced zero weights")
        weights = weights / weight_sum
        recovered.append(weights @ reflectances)

    return np.asarray(recovered, dtype=np.float64)


__all__ = [
    "solve_dictionary_reflectance",
]
