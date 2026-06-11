"""McCamy (1992) correlated colour temperature approximation."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._helpers import as_last_axis_pairs, normalize_method, scalar_or_array


def xy_to_CCT_McCamy1992(xy: Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Return CCT from CIE xy using the McCamy (1992) approximation.

    Parameters
    ----------
    xy
        CIE xy coordinates with final-axis shape ``(..., 2)``.

    Returns
    -------
    float or ndarray
        Approximate CCT in kelvins.

    Notes
    -----
    McCamy 1992 is an empirical ``xy -> CCT`` approximation. It does not
    compute Duv and does not provide a reliable inverse mapping.

    Examples
    --------
    >>> round(xy_to_CCT_McCamy1992([0.3127, 0.3290]))
    6505
    """
    xy_arr = as_last_axis_pairs(xy, name="xy")
    x = xy_arr[..., 0]
    y = xy_arr[..., 1]
    denominator = y - 0.1858
    if np.any(denominator == 0):
        raise ValueError("xy produces a zero denominator for McCamy 1992")
    n = (x - 0.3320) / denominator
    cct = -449.0 * n**3 + 3525.0 * n**2 - 6823.3 * n + 5520.33
    return scalar_or_array(cct)


def xy_to_CCT(
    xy: Sequence[float] | np.ndarray,
    *,
    method: str = "mccamy1992",
) -> float | np.ndarray:
    """Return approximate CCT from CIE xy using a named method.

    Parameters
    ----------
    xy
        CIE xy coordinates with final-axis shape ``(..., 2)``.
    method
        Approximation method. Currently only ``"mccamy1992"`` is supported.

    Returns
    -------
    float or ndarray
        Approximate CCT in kelvins.

    Notes
    -----
    This dispatcher currently exposes McCamy 1992. For CCT + Duv in
    CIE 1960 UCS, use ``xy_to_CCT_Duv``.

    Examples
    --------
    >>> round(xy_to_CCT([0.3127, 0.3290]))
    6505
    """
    method_normalized = normalize_method(method)
    if method_normalized != "mccamy1992":
        raise ValueError("method must be 'mccamy1992'")
    return xy_to_CCT_McCamy1992(xy)


__all__ = [
    "xy_to_CCT_McCamy1992",
    "xy_to_CCT",
]
