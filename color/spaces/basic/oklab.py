"""Oklab and Oklch colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ..node import ColorSpaceNode

MATRIX_XYZ_TO_LMS = np.array(
    [
        [0.8189330101, 0.3618667424, -0.1288597137],
        [0.0329845436, 0.9293118715, 0.0361456387],
        [0.0482003018, 0.2643662691, 0.6338517070],
    ],
    dtype=np.float64,
)
MATRIX_LMS_TO_OKLAB = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ],
    dtype=np.float64,
)
MATRIX_OKLAB_TO_LMS = np.array(
    [
        [1.0, 0.3963377774, 0.2158037573],
        [1.0, -0.1055613458, -0.0638541728],
        [1.0, -0.0894841775, -1.2914855480],
    ],
    dtype=np.float64,
)
MATRIX_LMS_TO_XYZ = np.array(
    [
        [1.2270138511, -0.5577999807, 0.2812561490],
        [-0.0405801784, 1.1122568696, -0.0716766787],
        [-0.0763812845, -0.4214819784, 1.5861632204],
    ],
    dtype=np.float64,
)
for _matrix in (
    MATRIX_XYZ_TO_LMS,
    MATRIX_LMS_TO_OKLAB,
    MATRIX_OKLAB_TO_LMS,
    MATRIX_LMS_TO_XYZ,
):
    _matrix.setflags(write=False)


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def XYZ_to_Oklab(XYZ: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE XYZ values to Oklab values."""
    xyz = _as_last_axis_triplets(XYZ, name="XYZ") / 100.0
    LMS = xyz @ MATRIX_XYZ_TO_LMS.T
    return np.cbrt(LMS) @ MATRIX_LMS_TO_OKLAB.T


def Oklab_to_XYZ(Oklab: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert Oklab values to CIE XYZ values."""
    oklab = _as_last_axis_triplets(Oklab, name="Oklab")
    LMS_cbrt = oklab @ MATRIX_OKLAB_TO_LMS.T
    return 100.0 * ((LMS_cbrt**3) @ MATRIX_LMS_TO_XYZ.T)


def Oklab_to_Oklch(Oklab: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert Oklab values to cylindrical Oklch values."""
    oklab = _as_last_axis_triplets(Oklab, name="Oklab")
    C = np.hypot(oklab[..., 1], oklab[..., 2])
    h = np.mod(np.degrees(np.arctan2(oklab[..., 2], oklab[..., 1])), 360.0)
    return np.stack((oklab[..., 0], C, h), axis=-1)


def Oklch_to_Oklab(Oklch: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert cylindrical Oklch values to Oklab values."""
    oklch = _as_last_axis_triplets(Oklch, name="Oklch")
    h = np.radians(oklch[..., 2])
    a = oklch[..., 1] * np.cos(h)
    b = oklch[..., 1] * np.sin(h)
    return np.stack((oklch[..., 0], a, b), axis=-1)


SPACE_NODES = (
    ColorSpaceNode(
        name="Oklab",
        aliases=("OKLab",),
        to_XYZ=Oklab_to_XYZ,
        from_XYZ=XYZ_to_Oklab,
        family="Oklab",
    ),
    ColorSpaceNode(
        name="Oklch",
        aliases=("OKLCH", "OKLCh"),
        parent="Oklab",
        to_parent=Oklch_to_Oklab,
        from_parent=Oklab_to_Oklch,
        family="Oklab",
    ),
)


__all__ = [
    "MATRIX_XYZ_TO_LMS",
    "MATRIX_LMS_TO_OKLAB",
    "MATRIX_OKLAB_TO_LMS",
    "MATRIX_LMS_TO_XYZ",
    "XYZ_to_Oklab",
    "Oklab_to_XYZ",
    "Oklab_to_Oklch",
    "Oklch_to_Oklab",
    "SPACE_NODES",
]
