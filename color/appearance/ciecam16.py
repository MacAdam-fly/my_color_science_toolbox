"""CIECAM16 colour appearance model.

This module uses the CIECAM16 reference domain: stimulus and whitepoint ``XYZ``
values are expected on the ``Y=100`` scale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np

from color.constants import CAT_CAT16, D65_XYZ

from .ciecam02 import (
    EPSILON,
    _achromatic_response,
    _as_correlate,
    _as_last_axis_three,
    _as_positive_scalar,
    _as_whitepoint,
    _compressed_response_from_opponents,
    _dot_last,
    _eccentricity_factor,
    _hue_angle,
    _hue_quadrature,
    _maybe_scalar,
    _opponent_dimensions_forward,
    _opponent_dimensions_inverse,
    _response_compression_forward,
    _response_compression_inverse,
    _safe_divide,
    _temporary_magnitude,
    _viewing_parameters,
)


CAT_INVERSE_CAT16 = np.linalg.inv(CAT_CAT16)
CAT_INVERSE_CAT16.setflags(write=False)
MATRIX_16 = CAT_CAT16
MATRIX_INVERSE_16 = CAT_INVERSE_CAT16


@dataclass(frozen=True)
class InductionFactors_CIECAM16:
    """Surround induction factors for CIECAM16."""

    F: float
    c: float
    N_c: float


VIEWING_CONDITIONS_CIECAM16 = MappingProxyType(
    {
        "Average": InductionFactors_CIECAM16(F=1.0, c=0.69, N_c=1.0),
        "Dim": InductionFactors_CIECAM16(F=0.9, c=0.59, N_c=0.9),
        "Dark": InductionFactors_CIECAM16(F=0.8, c=0.525, N_c=0.8),
    }
)


@dataclass(frozen=True)
class CIECAM16ViewingConditions:
    """Viewing conditions required by CIECAM16."""

    XYZ_w: Any = field(default_factory=lambda: D65_XYZ.copy())
    L_A: float = 64 / np.pi * 0.2
    Y_b: float = 20.0
    surround: str | InductionFactors_CIECAM16 = "Average"
    discount_illuminant: bool = False


@dataclass(frozen=True)
class CIECAM16Specification:
    """CIECAM16 appearance correlates."""

    J: Any = None
    C: Any = None
    h: Any = None
    s: Any = None
    Q: Any = None
    M: Any = None
    H: Any = None
    HC: Any = None


def _resolve_surround(value: str | InductionFactors_CIECAM16) -> InductionFactors_CIECAM16:
    if isinstance(value, InductionFactors_CIECAM16):
        return value
    if isinstance(value, str):
        for name, factors in VIEWING_CONDITIONS_CIECAM16.items():
            if value.lower() == name.lower():
                return factors
    raise ValueError(
        "surround must be one of 'Average', 'Dim', 'Dark' or an "
        "InductionFactors_CIECAM16 instance."
    )


def _resolve_viewing_conditions(
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> tuple[np.ndarray, float, float, InductionFactors_CIECAM16, bool]:
    if isinstance(XYZ_w, CIECAM16ViewingConditions):
        conditions = XYZ_w
        XYZ_w = conditions.XYZ_w
        L_A = conditions.L_A if L_A is None else L_A
        Y_b = conditions.Y_b if Y_b is None else Y_b
        surround = conditions.surround if surround is None else surround
        if discount_illuminant is None:
            discount_illuminant = conditions.discount_illuminant

    default = CIECAM16ViewingConditions()
    XYZ_w_array = _as_whitepoint(D65_XYZ if XYZ_w is None else XYZ_w)
    L_A_scalar = _as_positive_scalar(default.L_A if L_A is None else L_A, "L_A")
    Y_b_scalar = _as_positive_scalar(default.Y_b if Y_b is None else Y_b, "Y_b")
    factors = _resolve_surround(default.surround if surround is None else surround)
    discount = default.discount_illuminant if discount_illuminant is None else bool(discount_illuminant)
    return XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount


def _degree_of_adaptation(F: float, L_A: float, discount_illuminant: bool) -> float:
    if discount_illuminant:
        return 1.0
    D = F * (1.0 - (1.0 / 3.6) * np.exp((-L_A - 42.0) / 92.0))
    return float(np.clip(D, 0.0, 1.0))


def _adaptation_factor(RGB_w: np.ndarray, Y_w: float, D: float) -> np.ndarray:
    return D * Y_w / RGB_w + 1.0 - D


def XYZ_to_CIECAM16(
    XYZ: Any,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> CIECAM16Specification:
    """Convert XYZ tristimulus values to CIECAM16 appearance correlates."""

    XYZ_array, scalar_input = _as_last_axis_three(XYZ, "XYZ")
    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )

    Y_w = float(XYZ_w_array[1])
    n, F_L, N_bb, N_cb, z = _viewing_parameters(Y_b_scalar, Y_w, L_A_scalar)
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)

    RGB_w = CAT_CAT16 @ XYZ_w_array
    D_RGB = _adaptation_factor(RGB_w, Y_w, D)
    RGB_wc = D_RGB * RGB_w
    RGB_aw = _response_compression_forward(RGB_wc, F_L)
    A_w = float(_achromatic_response(RGB_aw, N_bb))

    RGB = _dot_last(XYZ_array, CAT_CAT16)
    RGB_c = D_RGB * RGB
    RGB_a = _response_compression_forward(RGB_c, F_L)

    a, b = _opponent_dimensions_forward(RGB_a)
    h = _hue_angle(a, b)
    H = _hue_quadrature(h)
    e_t = _eccentricity_factor(h)
    A = _achromatic_response(RGB_a, N_bb)

    J = 100.0 * (A / A_w) ** (factors.c * z)
    Q = (4.0 / factors.c) * np.sqrt(J / 100.0) * (A_w + 4.0) * F_L**0.25
    t = _temporary_magnitude(factors.N_c, N_cb, e_t, a, b, RGB_a)
    C = t**0.9 * np.sqrt(J / 100.0) * (1.64 - 0.29**n) ** 0.73
    M = C * F_L**0.25
    s = 100.0 * np.sqrt(_safe_divide(M, Q))

    return CIECAM16Specification(
        J=_maybe_scalar(J, scalar_input),
        C=_maybe_scalar(C, scalar_input),
        h=_maybe_scalar(h, scalar_input),
        s=_maybe_scalar(s, scalar_input),
        Q=_maybe_scalar(Q, scalar_input),
        M=_maybe_scalar(M, scalar_input),
        H=_maybe_scalar(H, scalar_input),
        HC=None,
    )


def CIECAM16_to_XYZ(
    specification: CIECAM16Specification,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CIECAM16 appearance correlates back to XYZ tristimulus values."""

    if not isinstance(specification, CIECAM16Specification):
        raise ValueError("specification must be a CIECAM16Specification instance.")

    J = _as_correlate(specification.J, "J")
    h = _as_correlate(specification.h, "h")
    if specification.C is None and specification.M is None:
        raise ValueError("CIECAM16Specification.C or CIECAM16Specification.M is required.")

    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )
    Y_w = float(XYZ_w_array[1])
    n, F_L, N_bb, N_cb, z = _viewing_parameters(Y_b_scalar, Y_w, L_A_scalar)
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)

    if specification.C is not None:
        C = _as_correlate(specification.C, "C")
    else:
        M = _as_correlate(specification.M, "M")
        C = M / F_L**0.25

    J, h, C = np.broadcast_arrays(J, h, C)
    scalar_input = J.shape == ()
    if np.any(J < 0) or np.any(C < 0):
        raise ValueError("CIECAM16Specification.J and C must be non-negative.")

    RGB_w = CAT_CAT16 @ XYZ_w_array
    D_RGB = _adaptation_factor(RGB_w, Y_w, D)
    RGB_wc = D_RGB * RGB_w
    RGB_aw = _response_compression_forward(RGB_wc, F_L)
    A_w = float(_achromatic_response(RGB_aw, N_bb))

    A = A_w * (J / 100.0) ** (1.0 / (factors.c * z))
    denominator = np.sqrt(np.maximum(J, EPSILON) / 100.0) * (1.64 - 0.29**n) ** 0.73
    t = (C / denominator) ** (1.0 / 0.9)
    e_t = _eccentricity_factor(h)
    P_1 = _safe_divide((50000.0 / 13.0) * factors.N_c * N_cb * e_t, t)
    P_2 = A / N_bb + 0.305
    P_3 = np.ones_like(P_1) * (21.0 / 20.0)
    P_n = np.stack([P_1, P_2, P_3], axis=-1)

    a, b = _opponent_dimensions_inverse(P_n, h)
    a = np.where(C <= EPSILON, 0.0, a)
    b = np.where(C <= EPSILON, 0.0, b)

    RGB_a = _compressed_response_from_opponents(P_2, a, b)
    RGB_c = _response_compression_inverse(RGB_a, F_L)
    RGB = RGB_c / D_RGB
    XYZ = _dot_last(RGB, CAT_INVERSE_CAT16)

    if scalar_input:
        return np.asarray(XYZ, dtype=np.float64).reshape(3)
    return np.asarray(XYZ, dtype=np.float64)


__all__ = [
    "CAT_CAT16",
    "CAT_INVERSE_CAT16",
    "MATRIX_16",
    "MATRIX_INVERSE_16",
    "InductionFactors_CIECAM16",
    "VIEWING_CONDITIONS_CIECAM16",
    "CIECAM16ViewingConditions",
    "CIECAM16Specification",
    "XYZ_to_CIECAM16",
    "CIECAM16_to_XYZ",
]
