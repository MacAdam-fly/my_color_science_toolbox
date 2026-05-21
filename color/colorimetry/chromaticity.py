"""Chromaticity helpers for XYZ and xyY values."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _as_last_axis_pairs(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array with two values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 2:
        raise ValueError(f"{name} must have 2 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _fallback_xy_array(
    fallback_xy: Sequence[float] | np.ndarray,
    target_shape: tuple[int, ...],
) -> np.ndarray:
    """Broadcast fallback xy coordinates to *target_shape*."""
    fallback = np.asarray(fallback_xy, dtype=np.float64)
    if fallback.shape != (2,):
        raise ValueError("fallback_xy must contain exactly two values")
    if not np.all(np.isfinite(fallback)):
        raise ValueError("fallback_xy must be finite")
    return np.broadcast_to(fallback, (*target_shape, 2))


def XYZ_to_xyY(
    XYZ: Sequence[float] | np.ndarray,
    *,
    fallback_xy: Sequence[float] | np.ndarray = (0.0, 0.0),
) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to CIE xyY.

    When ``X + Y + Z == 0``, ``fallback_xy`` is used for the chromaticity
    coordinates and the original ``Y`` value is preserved.
    """
    xyz = _as_last_axis_triplets(XYZ, name="XYZ")
    denominator = np.sum(xyz, axis=-1)
    fallback = _fallback_xy_array(fallback_xy, denominator.shape)

    xy = np.empty((*denominator.shape, 2), dtype=np.float64)
    nonzero = denominator != 0
    xy[..., :] = fallback
    np.divide(xyz[..., 0], denominator, out=xy[..., 0], where=nonzero)
    np.divide(xyz[..., 1], denominator, out=xy[..., 1], where=nonzero)

    return np.concatenate((xy, xyz[..., 1:2]), axis=-1)


def xyY_to_XYZ(xyY: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE xyY values to CIE XYZ tristimulus values."""
    xyy = _as_last_axis_triplets(xyY, name="xyY")
    x = xyy[..., 0]
    y = xyy[..., 1]
    Y = xyy[..., 2]

    XYZ = np.zeros_like(xyy, dtype=np.float64)
    nonzero = y != 0
    np.divide(x * Y, y, out=XYZ[..., 0], where=nonzero)
    XYZ[..., 1] = Y
    np.divide((1.0 - x - y) * Y, y, out=XYZ[..., 2], where=nonzero)
    return XYZ


def XYZ_to_xy(
    XYZ: Sequence[float] | np.ndarray,
    *,
    fallback_xy: Sequence[float] | np.ndarray = (0.0, 0.0),
) -> np.ndarray:
    """Return only the CIE xy chromaticity coordinates from XYZ values."""
    return XYZ_to_xyY(XYZ, fallback_xy=fallback_xy)[..., :2]


def xy_to_uv1960(xy: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE xy chromaticity coordinates to CIE 1960 UCS uv."""
    xy_arr = _as_last_axis_pairs(xy, name="xy")
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
    xyz = _as_last_axis_triplets(XYZ, name="XYZ")
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
    uv_arr = _as_last_axis_pairs(uv, name="uv")
    u = uv_arr[..., 0]
    v = uv_arr[..., 1]
    denominator = 2.0 * u - 8.0 * v + 4.0
    if np.any(denominator == 0):
        raise ValueError("uv produces a zero denominator for CIE xy")
    x = 3.0 * u / denominator
    y = 2.0 * v / denominator
    return np.stack([x, y], axis=-1)


def xy_to_upvp1976(xy: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE xy chromaticity coordinates to CIE 1976 UCS u'v'."""
    uv = xy_to_uv1960(xy)
    return np.stack([uv[..., 0], 1.5 * uv[..., 1]], axis=-1)


def XYZ_to_upvp1976(XYZ: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to CIE 1976 UCS u'v'."""
    xyz = _as_last_axis_triplets(XYZ, name="XYZ")
    X = xyz[..., 0]
    Y = xyz[..., 1]
    Z = xyz[..., 2]
    denominator = X + 15.0 * Y + 3.0 * Z
    if np.any(denominator == 0):
        raise ValueError("XYZ produces a zero denominator for CIE 1976 u'v'")
    u_p = 4.0 * X / denominator
    v_p = 9.0 * Y / denominator
    return np.stack([u_p, v_p], axis=-1)


def upvp1976_to_xy(upvp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE 1976 UCS u'v' coordinates to CIE xy chromaticity coordinates."""
    upvp_arr = _as_last_axis_pairs(upvp, name="upvp")
    u_p = upvp_arr[..., 0]
    v_p = upvp_arr[..., 1]
    denominator = 6.0 * u_p - 16.0 * v_p + 12.0
    if np.any(denominator == 0):
        raise ValueError("u'v' produces a zero denominator for CIE xy")
    x = 9.0 * u_p / denominator
    y = 4.0 * v_p / denominator
    return np.stack([x, y], axis=-1)


__all__ = [
    "XYZ_to_xyY",
    "xyY_to_XYZ",
    "XYZ_to_xy",
    "xy_to_uv1960",
    "XYZ_to_uv1960",
    "uv1960_to_xy",
    "xy_to_upvp1976",
    "XYZ_to_upvp1976",
    "upvp1976_to_xy",
]
