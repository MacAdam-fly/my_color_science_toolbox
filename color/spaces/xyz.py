"""XYZ-adjacent utilities."""

from __future__ import annotations

import numpy as np

from ..core.context import ColorContext
from ..core.types import ArrayLike
from .registry import SpaceDefinition, register_space


def xyz_to_xyy(xyz: ArrayLike) -> np.ndarray:
    xyz = np.asarray(xyz, dtype=float)
    total = float(np.sum(xyz))
    if total == 0:
        return np.array([0.0, 0.0, 0.0], dtype=float)
    return np.array([xyz[0] / total, xyz[1] / total, xyz[1]], dtype=float)


def xyy_to_xyz(xyy: ArrayLike) -> np.ndarray:
    xyy = np.asarray(xyy, dtype=float)
    x, y, Y = xyy
    if y == 0:
        return np.array([0.0, float(Y), 0.0], dtype=float)
    return np.array([(x / y) * Y, Y, ((1 - x - y) / y) * Y], dtype=float)


def to_xyz(xyz: ArrayLike, context: ColorContext = None) -> np.ndarray:
    return np.asarray(xyz, dtype=float)


def from_xyz(xyz: ArrayLike, context: ColorContext = None) -> np.ndarray:
    return np.asarray(xyz, dtype=float)


register_space(
    SpaceDefinition(
        name="xyz",
        to_xyz=to_xyz,
        from_xyz=from_xyz,
        aliases=("cie_xyz",),
    )
)
