"""Lightness helpers for CIE 1976 Y and L* conversions."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_float_array


_EPSILON = 216.0 / 24389.0
_KAPPA = 24389.0 / 27.0


def Y_to_Lstar(
    Y: float | Sequence[float] | np.ndarray,
    Y_n: float | Sequence[float] | np.ndarray = 100.0,
) -> float | np.ndarray:
    """Convert relative luminance component ``Y`` to CIE 1976 ``L*``.

    Parameters
    ----------
    Y
        Relative luminance values. The project default reference domain uses
        ``Y_n=100``.
    Y_n
        Reference white luminance. Must be positive.

    Returns
    -------
    float or ndarray
        CIE 1976 lightness values.

    Notes
    -----
    ``Y`` is a relative luminance component, not an absolute luminance in
    ``cd/m^2``.

    Examples
    --------
    >>> round(Y_to_Lstar(18.0), 3)
    49.496
    """
    Y_arr = as_float_array(Y, name="Y")
    Y_n_arr = as_float_array(Y_n, name="Y_n")
    if np.any(Y_arr < 0):
        raise ValueError("Y must be non-negative")
    if np.any(Y_n_arr <= 0):
        raise ValueError("Y_n must be positive")

    ratio = Y_arr / Y_n_arr
    f = np.where(ratio > _EPSILON, np.cbrt(ratio), (_KAPPA * ratio + 16.0) / 116.0)
    Lstar = 116.0 * f - 16.0
    if Lstar.shape == ():
        return float(Lstar)
    return Lstar


def Lstar_to_Y(
    Lstar: float | Sequence[float] | np.ndarray,
    Y_n: float | Sequence[float] | np.ndarray = 100.0,
) -> float | np.ndarray:
    """Convert CIE 1976 ``L*`` to relative luminance component ``Y``.

    Parameters
    ----------
    Lstar
        CIE 1976 lightness values.
    Y_n
        Reference white luminance. Must be positive.

    Returns
    -------
    float or ndarray
        Relative luminance values on the same scale as ``Y_n``.

    Notes
    -----
    With the default ``Y_n=100``, ``Lstar=100`` maps to ``Y=100``.

    Examples
    --------
    >>> Lstar_to_Y(100.0)
    100.0
    """
    Lstar_arr = as_float_array(Lstar, name="Lstar")
    Y_n_arr = as_float_array(Y_n, name="Y_n")
    if np.any(Lstar_arr < 0):
        raise ValueError("Lstar must be non-negative")
    if np.any(Y_n_arr <= 0):
        raise ValueError("Y_n must be positive")

    f = (Lstar_arr + 16.0) / 116.0
    ratio = np.where(Lstar_arr > 8.0, f**3, Lstar_arr / _KAPPA)
    Y = ratio * Y_n_arr
    if Y.shape == ():
        return float(Y)
    return Y


__all__ = [
    "Y_to_Lstar",
    "Lstar_to_Y",
]
