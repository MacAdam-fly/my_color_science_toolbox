"""High-level CCT and Duv analysis objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .conversions import xy_to_uv1960
from .dispatch import CCT_Duv_to_xy, uv_to_CCT


@dataclass(frozen=True)
class TemperatureAnalysis:
    """Complete CCT and Duv analysis result.

    Parameters
    ----------
    CCT
        Correlated colour temperature in kelvins.
    Duv
        Signed distance from the Planckian locus in CIE 1960 UCS.
    xy
        CIE xy coordinates reconstructed from ``CCT`` and ``Duv`` by the same
        method.
    uv
        CIE 1960 UCS coordinates analysed by the method.
    method
        Method name used for the computation.
    locus
        Reference locus name. Currently ``"planckian"``.

    Returns
    -------
    TemperatureAnalysis
        Frozen dataclass returned by ``analyze_temperature``.

    Notes
    -----
    This object is semantic packaging around the lower-level
    ``xy_to_CCT_Duv`` / ``CCT_Duv_to_xy`` functions.

    Examples
    --------
    >>> result = analyze_temperature([0.3127, 0.3290])
    >>> result.locus
    'planckian'
    """

    CCT: float | np.ndarray
    Duv: float | np.ndarray
    xy: np.ndarray
    uv: np.ndarray
    method: str
    locus: str = "planckian"


def analyze_temperature(
    xy: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> TemperatureAnalysis:
    """Return a semantic CCT and Duv analysis result from CIE xy coordinates.

    Parameters
    ----------
    xy
        CIE xy coordinates with final-axis shape ``(..., 2)``.
    method
        CCT algorithm name. Supported values are ``"robertson1968"`` and
        ``"ohno2013"``.

    Returns
    -------
    TemperatureAnalysis
        Object containing ``CCT``, ``Duv``, reconstructed ``xy``, analysed
        ``uv`` and method metadata.

    Notes
    -----
    CCT and Duv are computed in CIE 1960 UCS relative to the Planckian locus.
    This is not the same as evaluating the CIE D-series daylight locus.

    Examples
    --------
    >>> result = analyze_temperature([0.3127, 0.3290])
    >>> result.uv.shape
    (2,)
    """
    uv = xy_to_uv1960(xy)
    cct_duv = uv_to_CCT(uv, method=method)
    CCT = cct_duv[..., 0]
    Duv = cct_duv[..., 1]
    return TemperatureAnalysis(
        CCT=float(CCT) if np.shape(CCT) == () else CCT,
        Duv=float(Duv) if np.shape(Duv) == () else Duv,
        xy=CCT_Duv_to_xy(cct_duv, method=method),
        uv=uv,
        method=method,
    )


__all__ = [
    "TemperatureAnalysis",
    "analyze_temperature",
]
