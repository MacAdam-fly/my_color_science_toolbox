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
    """Return CCT and Duv from CIE 1960 UCS uv using a named method.

    Parameters
    ----------
    uv
        CIE 1960 UCS coordinates with final-axis shape ``(..., 2)``.
    method
        CCT algorithm name. Supported values are ``"robertson1968"`` and
        ``"ohno2013"``.

    Returns
    -------
    ndarray
        Array with final-axis ``(CCT, Duv)``.

    Notes
    -----
    ``Duv`` is the signed distance from the Planckian locus in CIE 1960 UCS.
    Robertson is faster; Ohno uses a denser Planckian table and is usually the
    more precise path.

    Examples
    --------
    >>> uv_to_CCT([0.1978, 0.3122]).shape
    (2,)
    """
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
    """Return CIE 1960 UCS uv from CCT and Duv using a named method.

    Parameters
    ----------
    CCT_Duv
        Values with final-axis ``(CCT, Duv)``.
    method
        CCT algorithm name. Supported values are ``"robertson1968"`` and
        ``"ohno2013"``.

    Returns
    -------
    ndarray
        CIE 1960 UCS ``uv`` coordinates.

    Notes
    -----
    The result is built relative to the Planckian locus, not the CIE D-series
    daylight locus.

    Examples
    --------
    >>> CCT_to_uv([6500.0, 0.0]).shape
    (2,)
    """
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
    """Return CCT and Duv from CIE xy coordinates using a named method.

    Parameters
    ----------
    xy
        CIE xy coordinates with final-axis shape ``(..., 2)``.
    method
        CCT + Duv method passed to ``uv_to_CCT``.

    Returns
    -------
    ndarray
        Values with final-axis ``(CCT, Duv)``.

    Notes
    -----
    This is a convenience wrapper: ``xy`` is first converted to CIE 1960
    ``uv``, then analysed with ``uv_to_CCT``.

    Examples
    --------
    >>> xy_to_CCT_Duv([0.3127, 0.3290]).shape
    (2,)
    """
    return uv_to_CCT(xy_to_uv1960(xy), method=method)


def CCT_Duv_to_xy(
    CCT_Duv: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CIE xy coordinates from CCT and Duv using a named method.

    Parameters
    ----------
    CCT_Duv
        Values with final-axis ``(CCT, Duv)``.
    method
        CCT + Duv method passed to ``CCT_to_uv``.

    Returns
    -------
    ndarray
        CIE xy coordinates with final-axis shape ``(..., 2)``.

    Notes
    -----
    This is a convenience wrapper around ``CCT_to_uv`` followed by
    ``uv1960_to_xy``.

    Examples
    --------
    >>> CCT_Duv_to_xy([6500.0, 0.0]).shape
    (2,)
    """
    return uv1960_to_xy(CCT_to_uv(CCT_Duv, method=method))


__all__ = [
    "uv_to_CCT",
    "CCT_to_uv",
    "xy_to_CCT_Duv",
    "CCT_Duv_to_xy",
]
