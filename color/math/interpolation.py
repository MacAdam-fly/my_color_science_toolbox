"""Interpolation helpers for one-dimensional spectral data."""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.interpolate import PchipInterpolator, interp1d


Interpolator = Literal["auto", "nearest", "linear", "cubic", "pchip", "sprague"]

_SPRAGUE_BOUNDARY_COEFFICIENTS = np.array(
    [
        [884, -1960, 3033, -2648, 1080, -180],
        [508, -540, 488, -367, 144, -24],
        [-24, 144, -367, 488, -540, 508],
        [-180, 1080, -2648, 3033, -1960, 884],
    ],
    dtype=np.float64,
)


def validate_samples(
    x: np.ndarray,
    y: np.ndarray,
    target: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return validated one-dimensional interpolation arrays."""
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    target_arr = np.asarray(target, dtype=np.float64)

    if x_arr.ndim != 1:
        raise ValueError(f"x must be 1D, got shape {x_arr.shape}")
    if y_arr.ndim != 1:
        raise ValueError(f"y must be 1D, got shape {y_arr.shape}")
    if target_arr.ndim != 1:
        raise ValueError(f"target must be 1D, got shape {target_arr.shape}")
    if x_arr.size == 0 or target_arr.size == 0:
        raise ValueError("x and target must not be empty")
    if x_arr.size != y_arr.size:
        raise ValueError(
            f"x and y must have the same length, got {x_arr.size} and {y_arr.size}"
        )
    if not np.all(np.isfinite(x_arr)):
        raise ValueError("x must be finite")
    if not np.all(np.isfinite(y_arr)):
        raise ValueError("y must be finite")
    if not np.all(np.isfinite(target_arr)):
        raise ValueError("target must be finite")
    if np.any(np.diff(x_arr) <= 0):
        raise ValueError("x must be strictly increasing")
    if np.any(np.diff(target_arr) <= 0):
        raise ValueError("target must be strictly increasing")

    return x_arr, y_arr, target_arr


def is_uniform(x: np.ndarray, *, rtol: float = 1e-7, atol: float = 1e-12) -> bool:
    """Return whether samples are regularly spaced."""
    intervals = np.diff(np.asarray(x, dtype=np.float64))
    if intervals.size <= 1:
        return True
    return bool(np.allclose(intervals, intervals[0], rtol=rtol, atol=atol))


def resolve_interpolator(x: np.ndarray, method: Interpolator = "auto") -> str:
    """Resolve the interpolation method for the source samples.

    ``"auto"`` selects Sprague for uniform data with at least six samples,
    cubic for non-uniform data with at least four samples, and linear
    otherwise.
    """
    if method != "auto":
        if method not in {"nearest", "linear", "cubic", "pchip", "sprague"}:
            raise ValueError(f"unsupported interpolator {method!r}")
        return method

    if x.size >= 6 and is_uniform(x):
        return "sprague"
    if x.size >= 4:
        return "cubic"
    return "linear"


def _sprague_interpolate_1d(
    x: np.ndarray,
    y: np.ndarray,
    target: np.ndarray,
) -> np.ndarray:
    """Return Sprague interpolated values for regularly spaced samples."""
    if y.size < 6:
        raise ValueError("Sprague interpolation requires at least 6 samples")
    if not is_uniform(x):
        raise ValueError("Sprague interpolation requires uniform samples")

    interval = np.diff(x)[0]
    xp = np.concatenate(
        (
            np.array([x[0] - 2.0 * interval, x[0] - interval], dtype=np.float64),
            x,
            np.array([x[-1] + interval, x[-1] + 2.0 * interval], dtype=np.float64),
        )
    )

    start_extra = _SPRAGUE_BOUNDARY_COEFFICIENTS[:2] @ y[:6] / 209.0
    end_extra = _SPRAGUE_BOUNDARY_COEFFICIENTS[2:] @ y[-6:] / 209.0
    yp = np.concatenate((start_extra, y, end_extra))

    indexes = np.searchsorted(xp, target) - 1
    with np.errstate(divide="ignore", invalid="ignore"):
        X = (target - xp[indexes]) / (xp[indexes + 1] - xp[indexes])

    r = yp
    a0 = r[indexes]
    a1 = (
        2.0 * r[indexes - 2]
        - 16.0 * r[indexes - 1]
        + 16.0 * r[indexes + 1]
        - 2.0 * r[indexes + 2]
    ) / 24.0
    a2 = (
        -r[indexes - 2]
        + 16.0 * r[indexes - 1]
        - 30.0 * r[indexes]
        + 16.0 * r[indexes + 1]
        - r[indexes + 2]
    ) / 24.0
    a3 = (
        -9.0 * r[indexes - 2]
        + 39.0 * r[indexes - 1]
        - 70.0 * r[indexes]
        + 66.0 * r[indexes + 1]
        - 33.0 * r[indexes + 2]
        + 7.0 * r[indexes + 3]
    ) / 24.0
    a4 = (
        13.0 * r[indexes - 2]
        - 64.0 * r[indexes - 1]
        + 126.0 * r[indexes]
        - 124.0 * r[indexes + 1]
        + 61.0 * r[indexes + 2]
        - 12.0 * r[indexes + 3]
    ) / 24.0
    a5 = (
        -5.0 * r[indexes - 2]
        + 25.0 * r[indexes - 1]
        - 50.0 * r[indexes]
        + 50.0 * r[indexes + 1]
        - 25.0 * r[indexes + 2]
        + 5.0 * r[indexes + 3]
    ) / 24.0

    return a0 + a1 * X + a2 * X**2 + a3 * X**3 + a4 * X**4 + a5 * X**5


def interpolate_1d(
    x: np.ndarray,
    y: np.ndarray,
    target: np.ndarray,
    *,
    method: Interpolator = "auto",
    bounds_error: bool = True,
    fill_value: float = np.nan,
) -> np.ndarray:
    """Interpolate one one-dimensional signal at target sample positions.

    Inputs are strict numeric arrays: ``x`` and ``target`` must be finite,
    one-dimensional and strictly increasing. This function has no wavelength,
    label or metadata semantics; spectral object handling lives in
    ``color.spectra``.
    """
    x_arr, y_arr, target_arr = validate_samples(x, y, target)
    outside = (target_arr < x_arr[0]) | (target_arr > x_arr[-1])
    if bounds_error and np.any(outside):
        raise ValueError(
            "target samples are outside the source domain; "
            "pass bounds_error=False or use align/extrapolate"
        )

    result = np.full(target_arr.shape, fill_value, dtype=np.float64)
    inside = ~outside
    if not np.any(inside):
        return result

    selected = resolve_interpolator(x_arr, method)
    inside_target = target_arr[inside]
    if selected == "nearest":
        indexes = np.searchsorted(x_arr, inside_target, side="left")
        indexes = np.clip(indexes, 0, x_arr.size - 1)
        previous_indexes = np.clip(indexes - 1, 0, x_arr.size - 1)
        use_previous = np.abs(inside_target - x_arr[previous_indexes]) <= np.abs(
            inside_target - x_arr[indexes]
        )
        nearest_indexes = np.where(use_previous, previous_indexes, indexes)
        result[inside] = y_arr[nearest_indexes]
    elif selected == "linear":
        result[inside] = np.interp(inside_target, x_arr, y_arr)
    elif selected == "cubic":
        if x_arr.size < 4:
            raise ValueError("cubic interpolation requires at least 4 samples")
        interpolator = interp1d(
            x_arr,
            y_arr,
            kind="cubic",
            bounds_error=True,
            assume_sorted=True,
        )
        result[inside] = interpolator(inside_target)
    elif selected == "pchip":
        if x_arr.size < 2:
            raise ValueError("PCHIP interpolation requires at least 2 samples")
        result[inside] = PchipInterpolator(x_arr, y_arr)(inside_target)
    elif selected == "sprague":
        result[inside] = _sprague_interpolate_1d(x_arr, y_arr, inside_target)
    else:  # pragma: no cover - guarded by resolve_interpolator.
        raise ValueError(f"unsupported interpolator {selected!r}")

    return result
