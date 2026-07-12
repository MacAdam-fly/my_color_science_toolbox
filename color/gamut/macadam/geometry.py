"""Shared geometry helpers for regular MacAdam LCHab boundaries."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from color.spaces.basic.lab import LCHab_to_Lab, Lab_to_XYZ


def lch_chroma_limits_in_slice(
    L: float,
    hue_values: np.ndarray,
    *,
    whitepoint_XYZ: np.ndarray,
    C_upper: float,
    iterations: int,
    is_inside: Callable[[np.ndarray], np.ndarray],
) -> np.ndarray:
    """Return the largest in-slice LCHab chroma at every requested hue.

    The caller owns the physical slice membership test.  This helper only
    samples radial LCHab directions and uses bisection to keep every returned
    point inside that slice, avoiding an unconstrained envelope interpolation.
    """
    if L <= 0.0 or L >= 100.0:
        return np.zeros_like(hue_values, dtype=np.float64)

    lower = np.zeros_like(hue_values, dtype=np.float64)
    upper = np.full_like(hue_values, C_upper, dtype=np.float64)
    hue = np.mod(hue_values, 360.0)

    for _ in range(iterations):
        chroma = 0.5 * (lower + upper)
        LCHab = np.column_stack((np.full_like(chroma, L), chroma, hue))
        XYZ = Lab_to_XYZ(
            LCHab_to_Lab(LCHab),
            whitepoint_XYZ=whitepoint_XYZ,
        )
        inside = np.asarray(is_inside(XYZ), dtype=bool)
        if inside.shape != chroma.shape:
            raise ValueError("is_inside must return one value per candidate")
        lower = np.where(inside, chroma, lower)
        upper = np.where(inside, upper, chroma)

    return lower
