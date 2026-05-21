"""CAM16-UCS, CAM16-LCD and CAM16-SCD colour-space helpers."""

from __future__ import annotations

from types import MappingProxyType
from typing import Sequence

import numpy as np

from color.appearance import (
    CIECAM16Specification,
    CIECAM16_to_XYZ,
    InductionFactors_CIECAM16,
    XYZ_to_CIECAM16,
)

from ._cam_ucs import Coefficients_UCS_Luo2006, JMh_to_UCS, UCS_to_JMh
from .node import ColorSpaceNode


COEFFICIENTS_UCS_LI2017 = MappingProxyType(
    {
        "CAM16-UCS": Coefficients_UCS_Luo2006(K_L=1.0, c_1=0.007, c_2=0.0228),
        "CAM16-LCD": Coefficients_UCS_Luo2006(K_L=0.77, c_1=0.007, c_2=0.0053),
        "CAM16-SCD": Coefficients_UCS_Luo2006(K_L=1.24, c_1=0.007, c_2=0.0363),
    }
)


def JMh_CIECAM16_to_CAM16UCS(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM16 JMh correlates to CAM16-UCS J'a'b' coordinates."""
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LI2017["CAM16-UCS"])


def CAM16UCS_to_JMh_CIECAM16(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM16-UCS J'a'b' coordinates to CIECAM16 JMh correlates."""
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LI2017["CAM16-UCS"])


def JMh_CIECAM16_to_CAM16LCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM16 JMh correlates to CAM16-LCD J'a'b' coordinates."""
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LI2017["CAM16-LCD"])


def CAM16LCD_to_JMh_CIECAM16(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM16-LCD J'a'b' coordinates to CIECAM16 JMh correlates."""
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LI2017["CAM16-LCD"])


def JMh_CIECAM16_to_CAM16SCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM16 JMh correlates to CAM16-SCD J'a'b' coordinates."""
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LI2017["CAM16-SCD"])


def CAM16SCD_to_JMh_CIECAM16(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM16-SCD J'a'b' coordinates to CIECAM16 JMh correlates."""
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LI2017["CAM16-SCD"])


def _XYZ_to_CAM16(
    XYZ: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to a CAM16 uniform colour space."""
    spec = XYZ_to_CIECAM16(
        XYZ,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )
    JMh = np.stack((spec.J, spec.M, spec.h), axis=-1)
    return converter(JMh)


def _CAM16_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert a CAM16 uniform colour space to XYZ values."""
    JMh = converter(Jpapbp)
    return CIECAM16_to_XYZ(
        CIECAM16Specification(J=JMh[..., 0], M=JMh[..., 1], h=JMh[..., 2]),
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM16UCS(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM16-UCS coordinates."""
    return _XYZ_to_CAM16(
        XYZ,
        JMh_CIECAM16_to_CAM16UCS,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM16UCS_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM16-UCS coordinates to XYZ values."""
    return _CAM16_to_XYZ(
        Jpapbp,
        CAM16UCS_to_JMh_CIECAM16,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM16LCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM16-LCD coordinates."""
    return _XYZ_to_CAM16(
        XYZ,
        JMh_CIECAM16_to_CAM16LCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM16LCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM16-LCD coordinates to XYZ values."""
    return _CAM16_to_XYZ(
        Jpapbp,
        CAM16LCD_to_JMh_CIECAM16,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM16SCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM16-SCD coordinates."""
    return _XYZ_to_CAM16(
        XYZ,
        JMh_CIECAM16_to_CAM16SCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM16SCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM16-SCD coordinates to XYZ values."""
    return _CAM16_to_XYZ(
        Jpapbp,
        CAM16SCD_to_JMh_CIECAM16,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


SPACE_NODES = (
    ColorSpaceNode(
        name="CAM16-UCS",
        aliases=("CAM16UCS", "CAM16 UCS"),
        to_XYZ=CAM16UCS_to_XYZ,
        from_XYZ=XYZ_to_CAM16UCS,
        family="CAM16",
    ),
    ColorSpaceNode(
        name="CAM16-LCD",
        aliases=("CAM16LCD", "CAM16 LCD"),
        to_XYZ=CAM16LCD_to_XYZ,
        from_XYZ=XYZ_to_CAM16LCD,
        family="CAM16",
    ),
    ColorSpaceNode(
        name="CAM16-SCD",
        aliases=("CAM16SCD", "CAM16 SCD"),
        to_XYZ=CAM16SCD_to_XYZ,
        from_XYZ=XYZ_to_CAM16SCD,
        family="CAM16",
    ),
)


__all__ = [
    "COEFFICIENTS_UCS_LI2017",
    "JMh_CIECAM16_to_CAM16UCS",
    "CAM16UCS_to_JMh_CIECAM16",
    "JMh_CIECAM16_to_CAM16LCD",
    "CAM16LCD_to_JMh_CIECAM16",
    "JMh_CIECAM16_to_CAM16SCD",
    "CAM16SCD_to_JMh_CIECAM16",
    "XYZ_to_CAM16UCS",
    "CAM16UCS_to_XYZ",
    "XYZ_to_CAM16LCD",
    "CAM16LCD_to_XYZ",
    "XYZ_to_CAM16SCD",
    "CAM16SCD_to_XYZ",
    "SPACE_NODES",
]
