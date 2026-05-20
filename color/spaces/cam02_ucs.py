"""CAM02-UCS, CAM02-LCD and CAM02-SCD colour-space helpers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Sequence

import numpy as np

from color.appearance import (
    CIECAM02Specification,
    CIECAM02_to_XYZ,
    InductionFactors_CIECAM02,
    XYZ_to_CIECAM02,
)

from .node import ColorSpaceNode


@dataclass(frozen=True)
class Coefficients_UCS_Luo2006:
    """Luo et al. (2006) uniform colour-space coefficients."""

    K_L: float
    c_1: float
    c_2: float


COEFFICIENTS_UCS_LUO2006 = MappingProxyType(
    {
        "CAM02-UCS": Coefficients_UCS_Luo2006(K_L=1.0, c_1=0.007, c_2=0.0228),
        "CAM02-LCD": Coefficients_UCS_Luo2006(K_L=0.77, c_1=0.007, c_2=0.0053),
        "CAM02-SCD": Coefficients_UCS_Luo2006(K_L=1.24, c_1=0.007, c_2=0.0363),
    }
)


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _JMh_to_UCS_Luo2006(
    JMh: Sequence[float] | np.ndarray,
    coefficients: Coefficients_UCS_Luo2006,
) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to a Luo et al. 2006 CAM02 space."""
    jmh = _as_last_axis_triplets(JMh, name="JMh")
    J = jmh[..., 0]
    M = jmh[..., 1]
    h = np.radians(jmh[..., 2])

    J_p = ((1.0 + 100.0 * coefficients.c_1) * J) / (1.0 + coefficients.c_1 * J)
    M_p = np.log1p(coefficients.c_2 * M) / coefficients.c_2
    a_p = M_p * np.cos(h)
    b_p = M_p * np.sin(h)
    return np.stack((J_p, a_p, b_p), axis=-1)


def _UCS_Luo2006_to_JMh(
    Jpapbp: Sequence[float] | np.ndarray,
    coefficients: Coefficients_UCS_Luo2006,
) -> np.ndarray:
    """Convert a Luo et al. 2006 CAM02 space to CIECAM02 JMh correlates."""
    jab = _as_last_axis_triplets(Jpapbp, name="Jpapbp")
    J_p = jab[..., 0]
    a_p = jab[..., 1]
    b_p = jab[..., 2]

    denominator = 1.0 + 100.0 * coefficients.c_1 - coefficients.c_1 * J_p
    if np.any(np.abs(denominator) <= np.finfo(np.float64).eps):
        raise ValueError("CAM02 J' value leads to a singular J inverse")
    J = J_p / denominator
    M_p = np.hypot(a_p, b_p)
    M = np.expm1(coefficients.c_2 * M_p) / coefficients.c_2
    h = np.mod(np.degrees(np.arctan2(b_p, a_p)), 360.0)
    return np.stack((J, M, h), axis=-1)


def JMh_CIECAM02_to_CAM02UCS(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to CAM02-UCS J'a'b' coordinates."""
    return _JMh_to_UCS_Luo2006(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-UCS"])


def CAM02UCS_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-UCS J'a'b' coordinates to CIECAM02 JMh correlates."""
    return _UCS_Luo2006_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-UCS"])


def JMh_CIECAM02_to_CAM02LCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to CAM02-LCD J'a'b' coordinates."""
    return _JMh_to_UCS_Luo2006(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-LCD"])


def CAM02LCD_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-LCD J'a'b' coordinates to CIECAM02 JMh correlates."""
    return _UCS_Luo2006_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-LCD"])


def JMh_CIECAM02_to_CAM02SCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to CAM02-SCD J'a'b' coordinates."""
    return _JMh_to_UCS_Luo2006(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-SCD"])


def CAM02SCD_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-SCD J'a'b' coordinates to CIECAM02 JMh correlates."""
    return _UCS_Luo2006_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-SCD"])


def _XYZ_to_CAM02(
    XYZ: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to a CAM02 uniform colour space."""
    spec = XYZ_to_CIECAM02(
        XYZ,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )
    JMh = np.stack((spec.J, spec.M, spec.h), axis=-1)
    return converter(JMh)


def _CAM02_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert a CAM02 uniform colour space to XYZ values."""
    JMh = converter(Jpapbp)
    return CIECAM02_to_XYZ(
        CIECAM02Specification(J=JMh[..., 0], M=JMh[..., 1], h=JMh[..., 2]),
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM02UCS(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM02-UCS coordinates."""
    return _XYZ_to_CAM02(
        XYZ,
        JMh_CIECAM02_to_CAM02UCS,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM02UCS_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM02-UCS coordinates to XYZ values."""
    return _CAM02_to_XYZ(
        Jpapbp,
        CAM02UCS_to_JMh_CIECAM02,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM02LCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM02-LCD coordinates."""
    return _XYZ_to_CAM02(
        XYZ,
        JMh_CIECAM02_to_CAM02LCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM02LCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM02-LCD coordinates to XYZ values."""
    return _CAM02_to_XYZ(
        Jpapbp,
        CAM02LCD_to_JMh_CIECAM02,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM02SCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM02-SCD coordinates."""
    return _XYZ_to_CAM02(
        XYZ,
        JMh_CIECAM02_to_CAM02SCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM02SCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM02-SCD coordinates to XYZ values."""
    return _CAM02_to_XYZ(
        Jpapbp,
        CAM02SCD_to_JMh_CIECAM02,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


SPACE_NODES = (
    ColorSpaceNode(
        name="CAM02-UCS",
        aliases=("CAM02UCS", "CAM02 UCS"),
        to_XYZ=CAM02UCS_to_XYZ,
        from_XYZ=XYZ_to_CAM02UCS,
        family="CAM02",
    ),
    ColorSpaceNode(
        name="CAM02-LCD",
        aliases=("CAM02LCD", "CAM02 LCD"),
        to_XYZ=CAM02LCD_to_XYZ,
        from_XYZ=XYZ_to_CAM02LCD,
        family="CAM02",
    ),
    ColorSpaceNode(
        name="CAM02-SCD",
        aliases=("CAM02SCD", "CAM02 SCD"),
        to_XYZ=CAM02SCD_to_XYZ,
        from_XYZ=XYZ_to_CAM02SCD,
        family="CAM02",
    ),
)


__all__ = [
    "Coefficients_UCS_Luo2006",
    "COEFFICIENTS_UCS_LUO2006",
    "JMh_CIECAM02_to_CAM02UCS",
    "CAM02UCS_to_JMh_CIECAM02",
    "JMh_CIECAM02_to_CAM02LCD",
    "CAM02LCD_to_JMh_CIECAM02",
    "JMh_CIECAM02_to_CAM02SCD",
    "CAM02SCD_to_JMh_CIECAM02",
    "XYZ_to_CAM02UCS",
    "CAM02UCS_to_XYZ",
    "XYZ_to_CAM02LCD",
    "CAM02LCD_to_XYZ",
    "XYZ_to_CAM02SCD",
    "CAM02SCD_to_XYZ",
    "SPACE_NODES",
]
