"""Appearance-uniform colour-difference formulas."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.spaces.appearance import (
    COEFFICIENTS_UCS_LI2017,
    COEFFICIENTS_UCS_LUO2006,
    Coefficients_UCS_Luo2006,
)

from ._utils import as_float_result, broadcast_triplets


def delta_E_UCS_Luo2006(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
    coefficients: Coefficients_UCS_Luo2006,
) -> np.ndarray | np.float64:
    """Return Luo/Li UCS family Delta E for J'a'b' coordinates."""
    if not np.isfinite(coefficients.K_L) or coefficients.K_L <= 0:
        raise ValueError("coefficients.K_L must be positive and finite")

    jab_1, jab_2 = broadcast_triplets(
        Jpapbp_1,
        Jpapbp_2,
        name_1="Jpapbp_1",
        name_2="Jpapbp_2",
    )
    d_E = np.sqrt(
        ((jab_1[..., 0] - jab_2[..., 0]) / coefficients.K_L) ** 2
        + (jab_1[..., 1] - jab_2[..., 1]) ** 2
        + (jab_1[..., 2] - jab_2[..., 2]) ** 2
    )
    return as_float_result(d_E)


def delta_E_CAM02UCS(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CAM02-UCS colour difference for J'a'b' coordinates.

    Inputs must already be CAM02-UCS coordinates computed with the same
    viewing conditions.
    """
    return delta_E_UCS_Luo2006(
        Jpapbp_1,
        Jpapbp_2,
        COEFFICIENTS_UCS_LUO2006["CAM02-UCS"],
    )


def delta_E_CAM02LCD(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CAM02-LCD colour difference for J'a'b' coordinates."""
    return delta_E_UCS_Luo2006(
        Jpapbp_1,
        Jpapbp_2,
        COEFFICIENTS_UCS_LUO2006["CAM02-LCD"],
    )


def delta_E_CAM02SCD(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CAM02-SCD colour difference for J'a'b' coordinates."""
    return delta_E_UCS_Luo2006(
        Jpapbp_1,
        Jpapbp_2,
        COEFFICIENTS_UCS_LUO2006["CAM02-SCD"],
    )


def delta_E_CAM16UCS(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CAM16-UCS colour difference for J'a'b' coordinates.

    Inputs must already be CAM16-UCS coordinates computed with the same
    viewing conditions.
    """
    return delta_E_UCS_Luo2006(
        Jpapbp_1,
        Jpapbp_2,
        COEFFICIENTS_UCS_LI2017["CAM16-UCS"],
    )


def delta_E_CAM16LCD(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CAM16-LCD colour difference for J'a'b' coordinates."""
    return delta_E_UCS_Luo2006(
        Jpapbp_1,
        Jpapbp_2,
        COEFFICIENTS_UCS_LI2017["CAM16-LCD"],
    )


def delta_E_CAM16SCD(
    Jpapbp_1: Sequence[float] | np.ndarray,
    Jpapbp_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CAM16-SCD colour difference for J'a'b' coordinates."""
    return delta_E_UCS_Luo2006(
        Jpapbp_1,
        Jpapbp_2,
        COEFFICIENTS_UCS_LI2017["CAM16-SCD"],
    )


__all__ = [
    "delta_E_CAM02UCS",
    "delta_E_CAM02LCD",
    "delta_E_CAM02SCD",
    "delta_E_CAM16UCS",
    "delta_E_CAM16LCD",
    "delta_E_CAM16SCD",
]
