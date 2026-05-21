"""CIE 1976 Lab and LCHab colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.constants import D65_XYZ

from ..node import ColorSpaceNode

EPSILON = 216.0 / 24389.0
KAPPA = 24389.0 / 27.0
DEFAULT_WHITEPOINT_XYZ = np.array(D65_XYZ, dtype=np.float64)
DEFAULT_WHITEPOINT_XYZ.setflags(write=False)


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _as_whitepoint(whitepoint_XYZ: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return a valid reference whitepoint XYZ triplet."""
    whitepoint = np.asarray(whitepoint_XYZ, dtype=np.float64)
    if whitepoint.shape != (3,):
        raise ValueError("whitepoint_XYZ must have shape (3,)")
    if not np.all(np.isfinite(whitepoint)):
        raise ValueError("whitepoint_XYZ must be finite")
    if np.any(whitepoint <= 0):
        raise ValueError("whitepoint_XYZ values must be positive")
    return whitepoint


def _f(t: np.ndarray) -> np.ndarray:
    """Return the CIE Lab forward helper function."""
    return np.where(t > EPSILON, np.cbrt(t), (KAPPA * t + 16.0) / 116.0)


def _f_inverse(t: np.ndarray) -> np.ndarray:
    """Return the CIE Lab inverse helper function."""
    t3 = t**3
    return np.where(t3 > EPSILON, t3, (116.0 * t - 16.0) / KAPPA)


def XYZ_to_Lab(
    XYZ: Sequence[float] | np.ndarray,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XYZ,
) -> np.ndarray:
    """Convert CIE XYZ values to CIE 1976 Lab values."""
    xyz = _as_last_axis_triplets(XYZ, name="XYZ")
    whitepoint = _as_whitepoint(whitepoint_XYZ)
    f_xyz = _f(xyz / whitepoint)

    L = 116.0 * f_xyz[..., 1] - 16.0
    a = 500.0 * (f_xyz[..., 0] - f_xyz[..., 1])
    b = 200.0 * (f_xyz[..., 1] - f_xyz[..., 2])
    return np.stack((L, a, b), axis=-1)


def Lab_to_XYZ(
    Lab: Sequence[float] | np.ndarray,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XYZ,
) -> np.ndarray:
    """Convert CIE 1976 Lab values to CIE XYZ values."""
    lab = _as_last_axis_triplets(Lab, name="Lab")
    whitepoint = _as_whitepoint(whitepoint_XYZ)

    f_y = (lab[..., 0] + 16.0) / 116.0
    f_x = lab[..., 1] / 500.0 + f_y
    f_z = f_y - lab[..., 2] / 200.0

    relative = np.stack(
        (_f_inverse(f_x), _f_inverse(f_y), _f_inverse(f_z)),
        axis=-1,
    )
    return relative * whitepoint


def Lab_to_LCHab(Lab: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE 1976 Lab values to cylindrical LCHab values."""
    lab = _as_last_axis_triplets(Lab, name="Lab")
    C = np.hypot(lab[..., 1], lab[..., 2])
    h = np.mod(np.degrees(np.arctan2(lab[..., 2], lab[..., 1])), 360.0)
    return np.stack((lab[..., 0], C, h), axis=-1)


def LCHab_to_Lab(LCHab: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert cylindrical LCHab values to CIE 1976 Lab values."""
    lch = _as_last_axis_triplets(LCHab, name="LCHab")
    h = np.radians(lch[..., 2])
    a = lch[..., 1] * np.cos(h)
    b = lch[..., 1] * np.sin(h)
    return np.stack((lch[..., 0], a, b), axis=-1)


SPACE_NODES = (
    ColorSpaceNode(
        name="Lab",
        aliases=("CIE Lab", "CIELAB"),
        to_XYZ=Lab_to_XYZ,
        from_XYZ=XYZ_to_Lab,
        family="Lab",
    ),
    ColorSpaceNode(
        name="LCHab",
        aliases=("CIE LCHab", "CIELCHab", "LChab"),
        parent="Lab",
        to_parent=LCHab_to_Lab,
        from_parent=Lab_to_LCHab,
        family="Lab",
    ),
)


__all__ = [
    "EPSILON",
    "KAPPA",
    "DEFAULT_WHITEPOINT_XYZ",
    "XYZ_to_Lab",
    "Lab_to_XYZ",
    "Lab_to_LCHab",
    "LCHab_to_Lab",
    "SPACE_NODES",
]
