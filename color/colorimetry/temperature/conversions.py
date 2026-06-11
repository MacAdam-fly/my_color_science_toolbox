"""Basic temperature and unit conversion helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ..chromaticity import XYZ_to_uv1960, uv1960_to_xy, xy_to_uv1960
from ._helpers import as_finite_array, scalar_or_array


def CCT_to_mired(CCT: float | Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Convert correlated colour temperature in kelvins to mired.

    Parameters
    ----------
    CCT
        Correlated colour temperature in kelvins. Scalars and arrays are
        supported.

    Returns
    -------
    float or ndarray
        Mired values, computed as ``1e6 / CCT``.

    Notes
    -----
    Zero CCT is invalid because the conversion is reciprocal.

    Examples
    --------
    >>> CCT_to_mired(5000)
    200.0
    """
    cct = as_finite_array(CCT, name="CCT")
    if np.any(cct == 0):
        raise ValueError("CCT must be non-zero")
    return scalar_or_array(1.0e6 / cct)


def mired_to_CCT(mired: float | Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Convert mired to correlated colour temperature in kelvins.

    Parameters
    ----------
    mired
        Micro reciprocal degree values. Scalars and arrays are supported.

    Returns
    -------
    float or ndarray
        Correlated colour temperature in kelvins.

    Notes
    -----
    Zero mired is invalid because the conversion is reciprocal.

    Examples
    --------
    >>> mired_to_CCT(200)
    5000.0
    """
    value = as_finite_array(mired, name="mired")
    if np.any(value == 0):
        raise ValueError("mired must be non-zero")
    return scalar_or_array(1.0e6 / value)


__all__ = [
    "CCT_to_mired",
    "mired_to_CCT",
    "xy_to_uv1960",
    "XYZ_to_uv1960",
    "uv1960_to_xy",
]
