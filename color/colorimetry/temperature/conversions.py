"""Basic temperature and CIE 1960 UCS conversion helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._helpers import as_finite_array, as_last_axis_pairs, scalar_or_array


def CCT_to_mired(CCT: float | Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Convert correlated colour temperature in kelvins to mired."""
    cct = as_finite_array(CCT, name="CCT")
    if np.any(cct == 0):
        raise ValueError("CCT must be non-zero")
    return scalar_or_array(1.0e6 / cct)


def mired_to_CCT(mired: float | Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Convert mired to correlated colour temperature in kelvins."""
    value = as_finite_array(mired, name="mired")
    if np.any(value == 0):
        raise ValueError("mired must be non-zero")
    return scalar_or_array(1.0e6 / value)


def xy_to_uv1960(xy: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE xy chromaticity coordinates to CIE 1960 UCS uv."""
    xy_arr = as_last_axis_pairs(xy, name="xy")
    x = xy_arr[..., 0]
    y = xy_arr[..., 1]
    denominator = -2.0 * x + 12.0 * y + 3.0
    if np.any(denominator == 0):
        raise ValueError("xy produces a zero denominator for CIE 1960 uv")
    u = 4.0 * x / denominator
    v = 6.0 * y / denominator
    return np.stack([u, v], axis=-1)


def XYZ_to_uv1960(XYZ: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to CIE 1960 UCS uv."""
    xyz = as_finite_array(XYZ, name="XYZ")
    if xyz.shape == () or xyz.shape[-1] != 3:
        raise ValueError("XYZ must have 3 values on the last axis")
    X = xyz[..., 0]
    Y = xyz[..., 1]
    Z = xyz[..., 2]
    denominator = X + 15.0 * Y + 3.0 * Z
    if np.any(denominator == 0):
        raise ValueError("XYZ produces a zero denominator for CIE 1960 uv")
    u = 4.0 * X / denominator
    v = 6.0 * Y / denominator
    return np.stack([u, v], axis=-1)


def uv1960_to_xy(uv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE 1960 UCS uv coordinates to CIE xy chromaticity coordinates."""
    uv_arr = as_last_axis_pairs(uv, name="uv")
    u = uv_arr[..., 0]
    v = uv_arr[..., 1]
    denominator = 2.0 * u - 8.0 * v + 4.0
    if np.any(denominator == 0):
        raise ValueError("uv produces a zero denominator for CIE xy")
    x = 3.0 * u / denominator
    y = 2.0 * v / denominator
    return np.stack([x, y], axis=-1)


__all__ = [
    "CCT_to_mired",
    "mired_to_CCT",
    "xy_to_uv1960",
    "XYZ_to_uv1960",
    "uv1960_to_xy",
]
