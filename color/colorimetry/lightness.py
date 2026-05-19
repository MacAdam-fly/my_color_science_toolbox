"""Lightness helpers for CIE 1976 Y and L* conversions."""

from __future__ import annotations

from typing import Sequence

import numpy as np


_EPSILON = 216.0 / 24389.0
_KAPPA = 24389.0 / 27.0


def _as_float_array(value: float | Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array."""
    arr = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def Y_to_Lstar(
    Y: float | Sequence[float] | np.ndarray,
    Y_n: float | Sequence[float] | np.ndarray = 100.0,
) -> float | np.ndarray:
    """Convert relative luminance component ``Y`` to CIE 1976 ``L*``."""
    Y_arr = _as_float_array(Y, name="Y")
    Y_n_arr = _as_float_array(Y_n, name="Y_n")
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
    """Convert CIE 1976 ``L*`` to relative luminance component ``Y``."""
    Lstar_arr = _as_float_array(Lstar, name="Lstar")
    Y_n_arr = _as_float_array(Y_n, name="Y_n")
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
