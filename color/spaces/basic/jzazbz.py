"""Jzazbz colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_last_axis_triplets
from color.utils.scale import to_domain_1, to_domain_100

from ..node import ColorSpaceNode

JZAZBZ_B = 1.15
JZAZBZ_G = 0.66
JZAZBZ_D = -0.56
JZAZBZ_D0 = 1.6295499532821566e-11

ST2084_M1 = 2610.0 / 4096.0 / 4.0
ST2084_M2 = 1.7 * 2523.0 / 32.0
ST2084_C1 = 3424.0 / 4096.0
ST2084_C2 = 2413.0 / 4096.0 * 32.0
ST2084_C3 = 2392.0 / 4096.0 * 32.0
ST2084_PEAK_LUMINANCE = 10000.0

MATRIX_JZAZBZ_XYZ_TO_LMS = np.array(
    [
        [0.41478972, 0.579999, 0.0146480],
        [-0.2015100, 1.120649, 0.0531008],
        [-0.0166008, 0.264800, 0.6684799],
    ],
    dtype=np.float64,
)
MATRIX_JZAZBZ_LMS_TO_XYZ = np.linalg.inv(MATRIX_JZAZBZ_XYZ_TO_LMS)
MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ = np.array(
    [
        [0.500000, 0.500000, 0.000000],
        [3.524000, -4.066708, 0.542708],
        [0.199076, 1.096799, -1.295875],
    ],
    dtype=np.float64,
)
MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P = np.linalg.inv(MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ)

for _matrix in (
    MATRIX_JZAZBZ_XYZ_TO_LMS,
    MATRIX_JZAZBZ_LMS_TO_XYZ,
    MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ,
    MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P,
):
    _matrix.setflags(write=False)

def _eotf_inverse_ST2084(value: np.ndarray) -> np.ndarray:
    """Return ST 2084 inverse EOTF values for absolute luminance-like input."""
    with np.errstate(invalid="ignore", divide="ignore"):
        Y_p = (value / ST2084_PEAK_LUMINANCE) ** ST2084_M1
        return ((ST2084_C1 + ST2084_C2 * Y_p) / (1.0 + ST2084_C3 * Y_p)) ** ST2084_M2


def _eotf_ST2084(value: np.ndarray) -> np.ndarray:
    """Return ST 2084 EOTF values for PQ-encoded input."""
    with np.errstate(invalid="ignore", divide="ignore"):
        V_p = value ** (1.0 / ST2084_M2)
        numerator = np.maximum(V_p - ST2084_C1, 0.0)
        denominator = ST2084_C2 - ST2084_C3 * V_p
        return ST2084_PEAK_LUMINANCE * (numerator / denominator) ** (1.0 / ST2084_M1)


def _XYZ_to_Izazbz(XYZ: np.ndarray) -> np.ndarray:
    """Convert relative D65 XYZ values to the Izazbz intermediate space."""
    X = XYZ[..., 0]
    Y = XYZ[..., 1]
    Z = XYZ[..., 2]

    X_p = JZAZBZ_B * X - (JZAZBZ_B - 1.0) * Z
    Y_p = JZAZBZ_G * Y - (JZAZBZ_G - 1.0) * X
    XYZ_p = np.stack((X_p, Y_p, Z), axis=-1)

    LMS = XYZ_p @ MATRIX_JZAZBZ_XYZ_TO_LMS.T
    LMS_p = _eotf_inverse_ST2084(LMS)
    return LMS_p @ MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ.T


def _Izazbz_to_XYZ(Izazbz: np.ndarray) -> np.ndarray:
    """Convert the Izazbz intermediate space to relative D65 XYZ values."""
    LMS_p = Izazbz @ MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P.T
    LMS = _eotf_ST2084(LMS_p)
    XYZ_p = LMS @ MATRIX_JZAZBZ_LMS_TO_XYZ.T

    X_p = XYZ_p[..., 0]
    Y_p = XYZ_p[..., 1]
    Z = XYZ_p[..., 2]
    X = (X_p + (JZAZBZ_B - 1.0) * Z) / JZAZBZ_B
    Y = (Y_p + (JZAZBZ_G - 1.0) * X) / JZAZBZ_G
    return np.stack((X, Y, Z), axis=-1)


def XYZ_to_Jzazbz(XYZ_D65_referred: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert D65-referred CIE XYZ values on the Y=100 scale to Jzazbz values."""
    xyz = to_domain_1(
        as_last_axis_triplets(XYZ_D65_referred, name="XYZ_D65_referred"),
        source_scale="100",
    )
    Izazbz = _XYZ_to_Izazbz(xyz)
    I_z = Izazbz[..., 0]
    J_z = ((1.0 + JZAZBZ_D) * I_z) / (1.0 + JZAZBZ_D * I_z) - JZAZBZ_D0
    return np.stack((J_z, Izazbz[..., 1], Izazbz[..., 2]), axis=-1)


def Jzazbz_to_XYZ(Jzazbz: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert Jzazbz values to D65-referred CIE XYZ values on the Y=100 scale."""
    jzazbz = as_last_axis_triplets(Jzazbz, name="Jzazbz")
    J_z = jzazbz[..., 0]
    I_z = (J_z + JZAZBZ_D0) / (
        1.0 + JZAZBZ_D - JZAZBZ_D * (J_z + JZAZBZ_D0)
    )
    Izazbz = np.stack((I_z, jzazbz[..., 1], jzazbz[..., 2]), axis=-1)
    return to_domain_100(_Izazbz_to_XYZ(Izazbz), source_scale="1")


def Jzazbz_to_JzCzhz(Jzazbz: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert Jzazbz values to cylindrical JzCzhz values."""
    jzazbz = as_last_axis_triplets(Jzazbz, name="Jzazbz")
    C_z = np.hypot(jzazbz[..., 1], jzazbz[..., 2])
    h_z = np.mod(np.degrees(np.arctan2(jzazbz[..., 2], jzazbz[..., 1])), 360.0)
    return np.stack((jzazbz[..., 0], C_z, h_z), axis=-1)


def JzCzhz_to_Jzazbz(JzCzhz: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert cylindrical JzCzhz values to Jzazbz values."""
    jzczhz = as_last_axis_triplets(JzCzhz, name="JzCzhz")
    h_z = np.radians(jzczhz[..., 2])
    a_z = jzczhz[..., 1] * np.cos(h_z)
    b_z = jzczhz[..., 1] * np.sin(h_z)
    return np.stack((jzczhz[..., 0], a_z, b_z), axis=-1)


SPACE_NODES = (
    ColorSpaceNode(
        name="Jzazbz",
        aliases=("JzAzBz", "Jz a_z b_z"),
        to_XYZ=Jzazbz_to_XYZ,
        from_XYZ=XYZ_to_Jzazbz,
        family="Jzazbz",
        requires_D65_referred_XYZ=True,
    ),
    ColorSpaceNode(
        name="JzCzhz",
        aliases=("JzCzHz", "JzCzH_z", "Jz C_z h_z"),
        parent="Jzazbz",
        to_parent=JzCzhz_to_Jzazbz,
        from_parent=Jzazbz_to_JzCzhz,
        family="Jzazbz",
    ),
)


__all__ = [
    "JZAZBZ_B",
    "JZAZBZ_G",
    "JZAZBZ_D",
    "JZAZBZ_D0",
    "MATRIX_JZAZBZ_XYZ_TO_LMS",
    "MATRIX_JZAZBZ_LMS_TO_XYZ",
    "MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ",
    "MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P",
    "XYZ_to_Jzazbz",
    "Jzazbz_to_XYZ",
    "Jzazbz_to_JzCzhz",
    "JzCzhz_to_Jzazbz",
    "SPACE_NODES",
]
