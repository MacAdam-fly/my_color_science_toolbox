"""IPT colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ..node import ColorSpaceNode

MATRIX_IPT_XYZ_TO_LMS = np.array(
    [
        [0.4002, 0.7075, -0.0807],
        [-0.2280, 1.1500, 0.0612],
        [0.0000, 0.0000, 0.9184],
    ],
    dtype=np.float64,
)
MATRIX_IPT_LMS_TO_XYZ = np.linalg.inv(MATRIX_IPT_XYZ_TO_LMS)
MATRIX_IPT_LMS_P_TO_IPT = np.array(
    [
        [0.4000, 0.4000, 0.2000],
        [4.4550, -4.8510, 0.3960],
        [0.8056, 0.3572, -1.1628],
    ],
    dtype=np.float64,
)
MATRIX_IPT_IPT_TO_LMS_P = np.linalg.inv(MATRIX_IPT_LMS_P_TO_IPT)

for _matrix in (
    MATRIX_IPT_XYZ_TO_LMS,
    MATRIX_IPT_LMS_TO_XYZ,
    MATRIX_IPT_LMS_P_TO_IPT,
    MATRIX_IPT_IPT_TO_LMS_P,
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


def _spow(value: np.ndarray, exponent: float) -> np.ndarray:
    """Return sign-preserving power for IPT nonlinear response compression."""
    return np.sign(value) * np.abs(value) ** exponent


def XYZ_to_IPT(XYZ_D65_referred: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert D65-referred CIE XYZ values on the Y=100 scale to IPT values."""
    xyz = _as_last_axis_triplets(
        XYZ_D65_referred,
        name="XYZ_D65_referred",
    ) / 100.0
    LMS = xyz @ MATRIX_IPT_XYZ_TO_LMS.T
    LMS_p = _spow(LMS, 0.43)
    return LMS_p @ MATRIX_IPT_LMS_P_TO_IPT.T


def IPT_to_XYZ(IPT: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert IPT values to D65-referred CIE XYZ values on the Y=100 scale."""
    ipt = _as_last_axis_triplets(IPT, name="IPT")
    LMS_p = ipt @ MATRIX_IPT_IPT_TO_LMS_P.T
    LMS = _spow(LMS_p, 1.0 / 0.43)
    return 100.0 * (LMS @ MATRIX_IPT_LMS_TO_XYZ.T)


def IPT_hue_angle(IPT: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return the IPT hue angle in degrees in the [0, 360) interval."""
    ipt = _as_last_axis_triplets(IPT, name="IPT")
    return np.mod(np.degrees(np.arctan2(ipt[..., 2], ipt[..., 1])), 360.0)


SPACE_NODES = (
    ColorSpaceNode(
        name="IPT",
        aliases=("Fairchild IPT",),
        to_XYZ=IPT_to_XYZ,
        from_XYZ=XYZ_to_IPT,
        family="IPT",
    ),
)


__all__ = [
    "MATRIX_IPT_XYZ_TO_LMS",
    "MATRIX_IPT_LMS_TO_XYZ",
    "MATRIX_IPT_LMS_P_TO_IPT",
    "MATRIX_IPT_IPT_TO_LMS_P",
    "XYZ_to_IPT",
    "IPT_to_XYZ",
    "IPT_hue_angle",
    "SPACE_NODES",
]
