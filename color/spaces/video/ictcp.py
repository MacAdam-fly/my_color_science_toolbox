"""ICtCp video colour encoding helpers.

The public functions here are explicit video/HDR encoding helpers. They are
not registered as generic ``convert_color`` route nodes.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_last_axis_triplets

from .transfer import eotf_ST2084, eotf_inverse_ST2084


MATRIX_ICTCP_RGB_TO_LMS = (
    np.array(
        [
            [1688.0, 2146.0, 262.0],
            [683.0, 2951.0, 462.0],
            [99.0, 309.0, 3688.0],
        ],
        dtype=np.float64,
    )
    / 4096.0
)
"""BT.2020 linear RGB to LMS matrix used by ICtCp."""

MATRIX_ICTCP_LMS_TO_RGB = np.linalg.inv(MATRIX_ICTCP_RGB_TO_LMS)
"""Inverse ICtCp LMS to BT.2020 linear RGB matrix."""

MATRIX_ICTCP_LMS_P_TO_ICTCP = (
    np.array(
        [
            [2048.0, 2048.0, 0.0],
            [6610.0, -13613.0, 7003.0],
            [17933.0, -17390.0, -543.0],
        ],
        dtype=np.float64,
    )
    / 4096.0
)
"""PQ-encoded LMS to ICtCp matrix."""

MATRIX_ICTCP_ICTCP_TO_LMS_P = np.linalg.inv(MATRIX_ICTCP_LMS_P_TO_ICTCP)
"""Inverse ICtCp to PQ-encoded LMS matrix."""

for _matrix in (
    MATRIX_ICTCP_RGB_TO_LMS,
    MATRIX_ICTCP_LMS_TO_RGB,
    MATRIX_ICTCP_LMS_P_TO_ICTCP,
    MATRIX_ICTCP_ICTCP_TO_LMS_P,
):
    _matrix.setflags(write=False)


def RGB_BT2020_to_ICtCp(
    RGB: Sequence[float] | np.ndarray,
    *,
    L_p: float = 10000.0,
) -> np.ndarray:
    """Encode BT.2020 linear RGB values to ICtCp using the PQ path.

    Parameters
    ----------
    RGB
        BT.2020 linear-light RGB values with final axis ``(R, G, B)``. The
        values carry the HDR signal scale expected by the PQ transform.
    L_p
        ST 2084 peak luminance in cd/m2. The BT.2100 practical value is
        ``10000``.

    Returns
    -------
    numpy.ndarray
        ICtCp values with final axis ``(I, Ct, Cp)``.
    """

    rgb = as_last_axis_triplets(RGB, name="RGB")
    lms = rgb @ MATRIX_ICTCP_RGB_TO_LMS.T
    lms_p = eotf_inverse_ST2084(lms, L_p=L_p)
    return lms_p @ MATRIX_ICTCP_LMS_P_TO_ICTCP.T


def ICtCp_to_RGB_BT2020(
    ICtCp: Sequence[float] | np.ndarray,
    *,
    L_p: float = 10000.0,
) -> np.ndarray:
    """Decode ICtCp values to BT.2020 linear RGB using the PQ path."""

    ictcp = as_last_axis_triplets(ICtCp, name="ICtCp")
    lms_p = ictcp @ MATRIX_ICTCP_ICTCP_TO_LMS_P.T
    lms = eotf_ST2084(lms_p, L_p=L_p)
    return lms @ MATRIX_ICTCP_LMS_TO_RGB.T


__all__ = [
    "MATRIX_ICTCP_RGB_TO_LMS",
    "MATRIX_ICTCP_LMS_TO_RGB",
    "MATRIX_ICTCP_LMS_P_TO_ICTCP",
    "MATRIX_ICTCP_ICTCP_TO_LMS_P",
    "RGB_BT2020_to_ICtCp",
    "ICtCp_to_RGB_BT2020",
]
