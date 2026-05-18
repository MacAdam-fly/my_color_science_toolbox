"""Chromaticity helpers for XYZ and xyY values."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
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
