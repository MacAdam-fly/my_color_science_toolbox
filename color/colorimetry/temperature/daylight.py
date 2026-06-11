"""CIE D-series daylight chromaticity helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._helpers import as_finite_array, normalize_method


_CIE_D_MIN_CCT = 4000.0
_CIE_D_MAX_CCT = 25000.0


def CCT_to_xy_CIE_D(CCT: float | Sequence[float] | np.ndarray) -> np.ndarray:
    """Return CIE D-series daylight-locus xy coordinates from CCT.

    Parameters
    ----------
    CCT
        Daylight correlated colour temperature in kelvins. The CIE D formula
        is valid in the ``[4000, 25000]`` K interval.

    Returns
    -------
    ndarray
        CIE xy coordinates with final-axis shape ``(..., 2)``.

    Notes
    -----
    This computes the CIE D-series daylight chromaticity locus. It does not
    generate a daylight SPD and it is not the Planckian locus used by Duv.

    Examples
    --------
    >>> CCT_to_xy_CIE_D(6504).shape
    (2,)
    """
    cct = as_finite_array(CCT, name="CCT")
    if np.any((cct < _CIE_D_MIN_CCT) | (cct > _CIE_D_MAX_CCT)):
        raise ValueError("CCT must be in the [4000, 25000] interval for CIE D")

    cct_2 = cct**2
    cct_3 = cct**3
    x = np.where(
        cct <= 7000.0,
        -4.6070e9 / cct_3 + 2.9678e6 / cct_2 + 0.09911e3 / cct + 0.244063,
        -2.0064e9 / cct_3 + 1.9018e6 / cct_2 + 0.24748e3 / cct + 0.237040,
    )
    y = -3.0 * x**2 + 2.870 * x - 0.275
    return np.stack([x, y], axis=-1)


def CCT_to_xy(
    CCT: float | Sequence[float] | np.ndarray,
    *,
    method: str = "cie_d",
) -> np.ndarray:
    """Return CIE xy coordinates from CCT using a named daylight method.

    Notes
    -----
    The current dispatcher supports the CIE D-series daylight locus. For
    Planckian CCT + Duv conversion, use ``CCT_to_uv`` or
    ``CCT_Duv_to_xy`` instead.
    """
    method_normalized = normalize_method(method)
    if method_normalized not in {"cied", "daylight"}:
        raise ValueError("method must be 'cie_d'")
    return CCT_to_xy_CIE_D(CCT)


__all__ = [
    "CCT_to_xy_CIE_D",
    "CCT_to_xy",
]
