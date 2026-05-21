"""CAM02-UCS, CAM02-LCD and CAM02-SCD colour-space helpers."""

from __future__ import annotations

from types import MappingProxyType
from typing import Sequence

import numpy as np

from color.appearance import (
    CIECAM02Specification,
    CIECAM02_to_XYZ,
    InductionFactors_CIECAM02,
    XYZ_to_CIECAM02,
)

from ._cam_ucs import Coefficients_UCS_Luo2006, JMh_to_UCS, UCS_to_JMh
from .node import ColorSpaceNode


COEFFICIENTS_UCS_LUO2006 = MappingProxyType(
    {
        "CAM02-UCS": Coefficients_UCS_Luo2006(K_L=1.0, c_1=0.007, c_2=0.0228),
        "CAM02-LCD": Coefficients_UCS_Luo2006(K_L=0.77, c_1=0.007, c_2=0.0053),
        "CAM02-SCD": Coefficients_UCS_Luo2006(K_L=1.24, c_1=0.007, c_2=0.0363),
    }
)


def JMh_CIECAM02_to_CAM02UCS(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to CAM02-UCS J'a'b' coordinates."""
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-UCS"])


def CAM02UCS_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-UCS J'a'b' coordinates to CIECAM02 JMh correlates."""
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-UCS"])


def JMh_CIECAM02_to_CAM02LCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to CAM02-LCD J'a'b' coordinates."""
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-LCD"])


def CAM02LCD_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-LCD J'a'b' coordinates to CIECAM02 JMh correlates."""
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-LCD"])


def JMh_CIECAM02_to_CAM02SCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 JMh correlates to CAM02-SCD J'a'b' coordinates."""
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-SCD"])


def CAM02SCD_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-SCD J'a'b' coordinates to CIECAM02 JMh correlates."""
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-SCD"])


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
