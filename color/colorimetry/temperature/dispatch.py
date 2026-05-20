"""Named-method dispatchers for CCT and Duv helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._helpers import normalize_method
from .conversions import uv1960_to_xy, xy_to_uv1960
from .ohno2013 import CCT_to_uv_Ohno2013, uv_to_CCT_Ohno2013
from .robertson1968 import CCT_to_uv_Robertson1968, uv_to_CCT_Robertson1968


def uv_to_CCT(
    uv: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CCT and Duv from CIE 1960 UCS uv using a named method."""
    method_normalized = normalize_method(method)
    if method_normalized == "robertson1968":
        return uv_to_CCT_Robertson1968(uv)
    if method_normalized == "ohno2013":
        return uv_to_CCT_Ohno2013(uv)
    raise ValueError("method must be 'robertson1968' or 'ohno2013'")


def CCT_to_uv(
    CCT_Duv: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CIE 1960 UCS uv from CCT and Duv using a named method."""
    method_normalized = normalize_method(method)
    if method_normalized == "robertson1968":
        return CCT_to_uv_Robertson1968(CCT_Duv)
    if method_normalized == "ohno2013":
        return CCT_to_uv_Ohno2013(CCT_Duv)
    raise ValueError("method must be 'robertson1968' or 'ohno2013'")


def xy_to_CCT_Duv(
    xy: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CCT and Duv from CIE xy coordinates using a named method."""
    return uv_to_CCT(xy_to_uv1960(xy), method=method)


def CCT_Duv_to_xy(
    CCT_Duv: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CIE xy coordinates from CCT and Duv using a named method."""
    return uv1960_to_xy(CCT_to_uv(CCT_Duv, method=method))


__all__ = [
    "uv_to_CCT",
    "CCT_to_uv",
    "xy_to_CCT_Duv",
    "CCT_Duv_to_xy",
]
