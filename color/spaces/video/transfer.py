"""Video transfer functions.

These helpers expose explicit video/HDR signal curves. They are not RGB
colour-space transfer functions and are not registered in the generic
colour-space conversion graph.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_float_array


ST2084_M1 = 2610.0 / 4096.0 / 4.0
ST2084_M2 = 2523.0 / 4096.0 * 128.0
ST2084_C1 = 3424.0 / 4096.0
ST2084_C2 = 2413.0 / 4096.0 * 32.0
ST2084_C3 = 2392.0 / 4096.0 * 32.0
ST2084_PEAK_LUMINANCE = 10000.0

ARIBSTDB67_A = 0.17883277
ARIBSTDB67_B = 0.28466892
ARIBSTDB67_C = 0.55991073
ARIBSTDB67_REFERENCE_WHITE_LEVEL = 0.5


def _as_positive_scalar(value: float, name: str) -> float:
    scalar = float(value)
    if not np.isfinite(scalar) or scalar <= 0:
        raise ValueError(f"{name} must be a finite positive scalar.")
    return scalar


def _require_non_negative(value: np.ndarray, name: str) -> None:
    if np.any(value < 0):
        raise ValueError(f"{name} must be non-negative.")


def eotf_ST2084(
    N: Sequence[float] | np.ndarray,
    *,
    L_p: float = ST2084_PEAK_LUMINANCE,
) -> np.ndarray:
    """Apply the SMPTE ST 2084 / PQ EOTF.

    Parameters
    ----------
    N
        PQ-encoded signal values.
    L_p
        Peak luminance in cd/m2. The BT.2100 practical value is ``10000``.
    """

    value = as_float_array(N, name="N")
    _require_non_negative(value, "N")
    peak = _as_positive_scalar(L_p, "L_p")
    with np.errstate(invalid="ignore", divide="ignore"):
        V_p = value ** (1.0 / ST2084_M2)
        numerator = np.maximum(V_p - ST2084_C1, 0.0)
        denominator = ST2084_C2 - ST2084_C3 * V_p
        return peak * (numerator / denominator) ** (1.0 / ST2084_M1)


def eotf_inverse_ST2084(
    C: Sequence[float] | np.ndarray,
    *,
    L_p: float = ST2084_PEAK_LUMINANCE,
) -> np.ndarray:
    """Apply the inverse SMPTE ST 2084 / PQ EOTF."""

    value = as_float_array(C, name="C")
    _require_non_negative(value, "C")
    peak = _as_positive_scalar(L_p, "L_p")
    with np.errstate(invalid="ignore", divide="ignore"):
        Y_p = (value / peak) ** ST2084_M1
        return ((ST2084_C1 + ST2084_C2 * Y_p) / (1.0 + ST2084_C3 * Y_p)) ** ST2084_M2


def oetf_ARIBSTDB67(
    E: Sequence[float] | np.ndarray,
    *,
    r: float = ARIBSTDB67_REFERENCE_WHITE_LEVEL,
) -> np.ndarray:
    """Apply the ARIB STD-B67 / HLG opto-electronic transfer function."""

    value = as_float_array(E, name="E")
    _require_non_negative(value, "E")
    reference_white = _as_positive_scalar(r, "r")
    result = np.empty_like(value, dtype=np.float64)

    low = value <= 1.0
    result[low] = reference_white * np.sqrt(value[low])
    result[~low] = ARIBSTDB67_A * np.log(value[~low] - ARIBSTDB67_B) + ARIBSTDB67_C
    return result


def oetf_inverse_ARIBSTDB67(
    E_p: Sequence[float] | np.ndarray,
    *,
    r: float = ARIBSTDB67_REFERENCE_WHITE_LEVEL,
) -> np.ndarray:
    """Apply the inverse ARIB STD-B67 / HLG opto-electronic transfer function."""

    value = as_float_array(E_p, name="E_p")
    _require_non_negative(value, "E_p")
    reference_white = _as_positive_scalar(r, "r")
    result = np.empty_like(value, dtype=np.float64)

    low = value <= reference_white
    result[low] = (value[low] / reference_white) ** 2
    result[~low] = np.exp((value[~low] - ARIBSTDB67_C) / ARIBSTDB67_A) + ARIBSTDB67_B
    return result


__all__ = [
    "ST2084_M1",
    "ST2084_M2",
    "ST2084_C1",
    "ST2084_C2",
    "ST2084_C3",
    "ST2084_PEAK_LUMINANCE",
    "ARIBSTDB67_A",
    "ARIBSTDB67_B",
    "ARIBSTDB67_C",
    "ARIBSTDB67_REFERENCE_WHITE_LEVEL",
    "eotf_ST2084",
    "eotf_inverse_ST2084",
    "oetf_ARIBSTDB67",
    "oetf_inverse_ARIBSTDB67",
]
