"""PCA-based reflectance recovery."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.optimize import LinearConstraint, minimize

from .library import ReflectanceLibrary
from .solvers import validate_bounds


def _validate_n_components(n_components: int, max_components: int) -> int:
    """Return a valid PCA component count."""
    value = int(n_components)
    if value <= 0:
        raise ValueError("n_components must be positive")
    if value > max_components:
        raise ValueError(
            f"n_components must not exceed {max_components}, got {value}"
        )
    return value


def _pca_basis(
    library: ReflectanceLibrary,
    *,
    n_components: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(mean, basis, coefficient_scales)`` from a reflectance library."""
    reflectances = np.asarray(library.reflectances, dtype=np.float64)
    mean = np.mean(reflectances, axis=0)
    centered = reflectances - mean
    _, singular_values, components = np.linalg.svd(centered, full_matrices=False)
    count = _validate_n_components(
        n_components,
        min(components.shape[0], reflectances.shape[1]),
    )
    basis = components[:count]
    scales = singular_values[:count] / np.sqrt(max(reflectances.shape[0] - 1, 1))
    scales = np.where(scales > 0, scales, 1.0)
    return mean, basis, scales


def _validate_regularization(value: float) -> float:
    """Return a valid coefficient regularisation strength."""
    regularization = float(value)
    if not np.isfinite(regularization) or regularization < 0:
        raise ValueError(
            "coefficient_regularization must be a finite non-negative value"
        )
    return regularization


def solve_pca_reflectance(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    library: ReflectanceLibrary,
    bounds: Sequence[float],
    n_components: int,
    coefficient_regularization: float,
) -> np.ndarray:
    """Recover reflectances in a PCA subspace under reflectance bounds."""
    lower, upper = validate_bounds(bounds)
    regularization = _validate_regularization(coefficient_regularization)

    if library.reflectances.shape[1] != matrix.shape[1]:
        raise ValueError(
            "library wavelength count must match recovery matrix columns, "
            f"got {library.reflectances.shape[1]} and {matrix.shape[1]}"
        )

    mean, basis, scales = _pca_basis(library, n_components=n_components)
    basis_t = basis.T
    constraint = LinearConstraint(
        basis_t,
        np.full(mean.shape, lower, dtype=np.float64) - mean,
        np.full(mean.shape, upper, dtype=np.float64) - mean,
    )

    def reconstruct(coefficients: np.ndarray) -> np.ndarray:
        return mean + coefficients @ basis

    recovered = []
    initial = np.zeros(basis.shape[0], dtype=np.float64)
    for target in targets:
        target = np.asarray(target, dtype=np.float64)

        def objective(coefficients: np.ndarray) -> float:
            reflectance = reconstruct(coefficients)
            residual = matrix @ reflectance - target
            penalty = np.sum((coefficients / scales) ** 2)
            return float(np.dot(residual, residual) + regularization * penalty)

        result = minimize(
            objective,
            initial,
            method="SLSQP",
            constraints=(constraint,),
        )
        if not result.success:
            raise ValueError(f"PCA reflectance recovery failed: {result.message}")
        recovered.append(reconstruct(result.x))

    return np.asarray(recovered, dtype=np.float64)


__all__ = [
    "solve_pca_reflectance",
]
