"""Extrapolation helpers for one-dimensional spectral data."""

from __future__ import annotations

from typing import Literal

import numpy as np

from .interpolation import Interpolator, interpolate_1d, validate_samples


Extrapolator = Literal["constant", "linear", "fill"]


def extrapolate_1d(
    x: np.ndarray,
    y: np.ndarray,
    target: np.ndarray,
    *,
    interpolator: Interpolator = "auto",
    method: Extrapolator = "constant",
    fill_value: float = np.nan,
    left: float | None = None,
    right: float | None = None,
) -> np.ndarray:
    """Evaluate one signal at ``target``, extrapolating out-of-domain samples.

    ``method`` controls only samples outside the source domain: ``"constant"``
    uses edge values, ``"linear"`` extends edge slopes and ``"fill"`` uses
    ``fill_value``. This is a pure numeric helper; spectral metadata is handled
    by ``color.spectra``.
    """
    x_arr, y_arr, target_arr = validate_samples(x, y, target)
    if method not in {"constant", "linear", "fill"}:
        raise ValueError(f"unsupported extrapolator {method!r}")

    result = interpolate_1d(
        x_arr,
        y_arr,
        target_arr,
        method=interpolator,
        bounds_error=False,
        fill_value=fill_value,
    )

    left_mask = target_arr < x_arr[0]
    right_mask = target_arr > x_arr[-1]
    if method == "constant":
        result[left_mask] = y_arr[0]
        result[right_mask] = y_arr[-1]
    elif method == "linear":
        if x_arr.size < 2:
            raise ValueError("linear extrapolation requires at least 2 samples")
        left_slope = (y_arr[1] - y_arr[0]) / (x_arr[1] - x_arr[0])
        right_slope = (y_arr[-1] - y_arr[-2]) / (x_arr[-1] - x_arr[-2])
        result[left_mask] = y_arr[0] + (target_arr[left_mask] - x_arr[0]) * left_slope
        result[right_mask] = y_arr[-1] + (
            target_arr[right_mask] - x_arr[-1]
        ) * right_slope
    elif method == "fill":
        result[left_mask | right_mask] = fill_value

    if left is not None:
        result[left_mask] = left
    if right is not None:
        result[right_mask] = right

    return result
