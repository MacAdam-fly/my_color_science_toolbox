"""High-level CCT and Duv analysis objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .conversions import xy_to_uv1960
from .dispatch import CCT_Duv_to_xy, uv_to_CCT


@dataclass(frozen=True)
class TemperatureAnalysis:
    """Complete correlated colour temperature analysis result."""

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
    """Return a semantic CCT and Duv analysis result from CIE xy coordinates."""
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
