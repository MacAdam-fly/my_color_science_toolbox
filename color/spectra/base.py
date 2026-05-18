"""Shared helpers for spectral object wrappers."""

from __future__ import annotations

from typing import Any, Callable, Mapping

import numpy as np

from color.math import Extrapolator, Interpolator, extrapolate_1d, interpolate_1d


def readonly_array(value: Any, *, ndim: int, name: str) -> np.ndarray:
    """Return a float array copy with a fixed dimensionality."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.ndim != ndim:
        raise ValueError(f"{name} must be {ndim}D, got shape {arr.shape}")
    arr = np.array(arr, dtype=np.float64, copy=True)
    arr.setflags(write=False)
    return arr


def metadata_copy(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return a shallow metadata copy."""
    return dict(metadata or {})


def apply_nan_policy(
    values: np.ndarray,
    metadata: Mapping[str, Any] | None,
    *,
    fill_nan: float | None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Return values and metadata after an explicit NaN handling policy."""
    meta = metadata_copy(metadata)
    if fill_nan is None:
        return values, meta
    if not np.isfinite(fill_nan):
        raise ValueError("fill_nan must be finite")

    filled = np.array(values, dtype=np.float64, copy=True)
    filled[np.isnan(filled)] = fill_nan
    filled.setflags(write=False)
    meta["nan_policy"] = "fill"
    meta["nan_fill_value"] = float(fill_nan)
    return filled, meta


def check_wavelengths(wavelengths: np.ndarray) -> None:
    """Validate wavelength array."""
    if wavelengths.size == 0:
        raise ValueError("wavelengths must not be empty")
    if not np.all(np.isfinite(wavelengths)):
        raise ValueError("wavelengths must be finite")
    if np.any(np.diff(wavelengths) <= 0):
        raise ValueError("wavelengths must be strictly increasing")


def target_wavelengths(wavelengths: Any) -> np.ndarray:
    """Validate target wavelengths."""
    target = np.asarray(wavelengths, dtype=np.float64)
    if target.ndim != 1:
        raise ValueError(f"target wavelengths must be 1D, got shape {target.shape}")
    if target.size == 0:
        raise ValueError("target wavelengths must not be empty")
    if not np.all(np.isfinite(target)):
        raise ValueError("target wavelengths must be finite")
    if np.any(np.diff(target) <= 0):
        raise ValueError("target wavelengths must be strictly increasing")
    return target


def immutable_array(value: np.ndarray) -> np.ndarray:
    """Return a read-only copy of *value*."""
    arr = np.array(value, dtype=np.float64, copy=True)
    arr.setflags(write=False)
    return arr


def evaluate_channels(
    wavelengths: np.ndarray,
    values: np.ndarray,
    target: np.ndarray,
    evaluator: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray],
) -> np.ndarray:
    """Evaluate one or more spectral channels."""
    if values.ndim == 1:
        return evaluator(wavelengths, values, target)
    columns = [
        evaluator(wavelengths, values[:, index], target)
        for index in range(values.shape[1])
    ]
    return np.column_stack(columns)


def interpolate_values(
    wavelengths: np.ndarray,
    values: np.ndarray,
    target: np.ndarray,
    *,
    method: Interpolator,
    bounds_error: bool,
    fill_value: float,
) -> np.ndarray:
    """Interpolate one or more spectral channels."""
    return evaluate_channels(
        wavelengths,
        values,
        target,
        lambda x, y, t: interpolate_1d(
            x,
            y,
            t,
            method=method,
            bounds_error=bounds_error,
            fill_value=fill_value,
        ),
    )


def extrapolate_values(
    wavelengths: np.ndarray,
    values: np.ndarray,
    target: np.ndarray,
    *,
    interpolator: Interpolator,
    method: Extrapolator,
    fill_value: float,
    left: float | None,
    right: float | None,
) -> np.ndarray:
    """Extrapolate one or more spectral channels."""
    return evaluate_channels(
        wavelengths,
        values,
        target,
        lambda x, y, t: extrapolate_1d(
            x,
            y,
            t,
            interpolator=interpolator,
            method=method,
            fill_value=fill_value,
            left=left,
            right=right,
        ),
    )
