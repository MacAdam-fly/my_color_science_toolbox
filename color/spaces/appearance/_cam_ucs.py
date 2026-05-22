"""Shared helpers for CAM uniform colour spaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from color.utils.arrays import as_last_axis_triplets


@dataclass(frozen=True)
class Coefficients_UCS_Luo2006:
    """Uniform colour-space coefficients used by CAM02/CAM16 UCS families."""

    K_L: float
    c_1: float
    c_2: float


def JMh_to_UCS(
    JMh: Sequence[float] | np.ndarray,
    coefficients: Coefficients_UCS_Luo2006,
) -> np.ndarray:
    """Convert JMh correlates to J'a'b' coordinates."""
    jmh = as_last_axis_triplets(JMh, name="JMh")
    J = jmh[..., 0]
    M = jmh[..., 1]
    h = np.radians(jmh[..., 2])

    J_p = ((1.0 + 100.0 * coefficients.c_1) * J) / (1.0 + coefficients.c_1 * J)
    M_p = np.log1p(coefficients.c_2 * M) / coefficients.c_2
    a_p = M_p * np.cos(h)
    b_p = M_p * np.sin(h)
    return np.stack((J_p, a_p, b_p), axis=-1)


def UCS_to_JMh(
    Jpapbp: Sequence[float] | np.ndarray,
    coefficients: Coefficients_UCS_Luo2006,
) -> np.ndarray:
    """Convert J'a'b' coordinates to JMh correlates."""
    jab = as_last_axis_triplets(Jpapbp, name="Jpapbp")
    J_p = jab[..., 0]
    a_p = jab[..., 1]
    b_p = jab[..., 2]

    denominator = 1.0 + 100.0 * coefficients.c_1 - coefficients.c_1 * J_p
    if np.any(np.abs(denominator) <= np.finfo(np.float64).eps):
        raise ValueError("J' value leads to a singular J inverse")
    J = J_p / denominator
    M_p = np.hypot(a_p, b_p)
    M = np.expm1(coefficients.c_2 * M_p) / coefficients.c_2
    h = np.mod(np.degrees(np.arctan2(b_p, a_p)), 360.0)
    return np.stack((J, M, h), axis=-1)


__all__ = [
    "Coefficients_UCS_Luo2006",
    "as_last_axis_triplets",
    "JMh_to_UCS",
    "UCS_to_JMh",
]
