"""Numerical quadrature helpers for sampled data."""

from __future__ import annotations

from typing import Literal

import numpy as np


Quadrature = Literal["rectangle", "trapezoid"]


def quadrature_weights(
    wavelengths: np.ndarray,
    *,
    interval: float | None = None,
    quadrature: Quadrature = "rectangle",
) -> np.ndarray:
    """Return per-sample weights for the requested quadrature rule."""
    wavelength_array = np.asarray(wavelengths, dtype=np.float64)
    if quadrature == "rectangle":
        step = _interval_from_wavelengths(wavelength_array) if interval is None else interval
        return np.full(wavelength_array.shape, float(step), dtype=np.float64)
    if quadrature != "trapezoid":
        raise ValueError(f"unsupported quadrature {quadrature!r}")

    weights = np.zeros(wavelength_array.shape, dtype=np.float64)
    if wavelength_array.size > 1:
        deltas = np.diff(wavelength_array)
        weights[0] = deltas[0] / 2.0
        weights[-1] = deltas[-1] / 2.0
        if wavelength_array.size > 2:
            weights[1:-1] = (deltas[:-1] + deltas[1:]) / 2.0
    return weights


def integrate_samples(
    values: np.ndarray,
    wavelengths: np.ndarray,
    *,
    interval: float | None = None,
    quadrature: Quadrature = "rectangle",
    axis: int = -1,
) -> np.ndarray:
    """Integrate sampled values along *axis* using the requested rule."""
    value_array = np.asarray(values, dtype=np.float64)
    wavelength_array = np.asarray(wavelengths, dtype=np.float64)
    if quadrature == "trapezoid":
        return _trapezoid(value_array, wavelength_array, axis=axis)
    if quadrature != "rectangle":
        raise ValueError(f"unsupported quadrature {quadrature!r}")

    step = _interval_from_wavelengths(wavelength_array) if interval is None else interval
    return np.sum(value_array, axis=axis) * float(step)


def _interval_from_wavelengths(wavelengths: np.ndarray) -> float:
    """Return a rectangle-rule interval for sampled wavelengths."""
    intervals = np.diff(wavelengths)
    return float(intervals.min()) if intervals.size else 1.0


def _trapezoid(
    values: np.ndarray,
    wavelengths: np.ndarray,
    *,
    axis: int,
) -> np.ndarray:
    """Return trapezoid integration with compatibility for older NumPy."""
    if hasattr(np, "trapezoid"):
        return np.trapezoid(values, wavelengths, axis=axis)
    return getattr(np, "trapz")(values, wavelengths, axis=axis)


__all__ = [
    "Quadrature",
    "integrate_samples",
    "quadrature_weights",
]
