"""IPT colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_last_axis_triplets
from color.utils.scale import to_domain_1, to_domain_100

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

def _spow(value: np.ndarray, exponent: float) -> np.ndarray:
    """Return sign-preserving power for IPT nonlinear response compression."""
    return np.sign(value) * np.abs(value) ** exponent


def XYZ_to_IPT(XYZ_D65_referred: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert D65-referred CIE XYZ values on the Y=100 scale to IPT values.

    IPT is implemented as a D65-referred space in this package. Adapt non-D65
    XYZ values explicitly before calling this function or before routing to IPT
    with ``convert_color``.

    Parameters
    ----------
    XYZ_D65_referred
        D65-referred XYZ values with final axis ``(X, Y, Z)`` on the Y=100
        scale.

    Returns
    -------
    numpy.ndarray
        IPT values with final axis ``(I, P, T)``.

    Notes
    -----
    The IPT nonlinearity uses a sign-preserving power so intermediate
    out-of-gamut values can remain finite.

    Examples
    --------
    >>> XYZ_to_IPT([19.01, 20.0, 21.78]).shape
    (3,)
    """
    xyz = to_domain_1(
        as_last_axis_triplets(XYZ_D65_referred, name="XYZ_D65_referred"),
        source_scale="100",
    )
    LMS = xyz @ MATRIX_IPT_XYZ_TO_LMS.T
    LMS_p = _spow(LMS, 0.43)
    return LMS_p @ MATRIX_IPT_LMS_P_TO_IPT.T


def IPT_to_XYZ(IPT: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert IPT values to D65-referred CIE XYZ values on the Y=100 scale.

    The inverse returns XYZ in the project D65 reference domain. It does not
    adapt the result to any other whitepoint.

    Parameters
    ----------
    IPT
        IPT values with final axis ``(I, P, T)``.

    Returns
    -------
    numpy.ndarray
        D65-referred XYZ values on the Y=100 scale.

    Notes
    -----
    Use explicit chromatic adaptation after this function if another reference
    whitepoint is required.

    Examples
    --------
    >>> IPT_to_XYZ([0.5, 0.02, 0.01]).shape
    (3,)
    """
    ipt = as_last_axis_triplets(IPT, name="IPT")
    LMS_p = ipt @ MATRIX_IPT_IPT_TO_LMS_P.T
    LMS = _spow(LMS_p, 1.0 / 0.43)
    return to_domain_100(LMS @ MATRIX_IPT_LMS_TO_XYZ.T, source_scale="1")


def IPT_hue_angle(IPT: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return the IPT hue angle in degrees in the [0, 360) interval.

    Notes
    -----
    The hue is computed from the ``P`` and ``T`` opponent axes. The return shape
    is the broadcast input shape with the final IPT axis removed.
    """
    ipt = as_last_axis_triplets(IPT, name="IPT")
    return np.mod(np.degrees(np.arctan2(ipt[..., 2], ipt[..., 1])), 360.0)


SPACE_NODES = (
    ColorSpaceNode(
        name="IPT",
        aliases=("Fairchild IPT",),
        to_XYZ=IPT_to_XYZ,
        from_XYZ=XYZ_to_IPT,
        family="IPT",
        requires_D65_referred_XYZ=True,
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
