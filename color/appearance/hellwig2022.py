"""Hellwig and Fairchild 2022 colour appearance model.

This module uses the Hellwig2022 reference domain: stimulus and whitepoint
``XYZ`` values are expected on the ``Y=100`` scale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np

from color.constants import CAT_CAT16, D65_XYZ

from .ciecam02 import (
    EPSILON,
    _as_last_axis_three,
    _as_positive_scalar,
    _as_whitepoint,
    _compressed_response_from_opponents,
    _dot_last,
    _hue_angle,
    _hue_quadrature,
    _maybe_scalar,
    _opponent_dimensions_forward,
    _response_compression_forward,
    _response_compression_inverse,
    _safe_divide,
    _viewing_parameters,
)
from .ciecam16 import CAT_INVERSE_CAT16, _adaptation_factor, _degree_of_adaptation


@dataclass(frozen=True)
class InductionFactors_Hellwig2022:
    """Surround induction factors for Hellwig2022."""

    F: float
    c: float
    N_c: float


VIEWING_CONDITIONS_HELLWIG2022 = MappingProxyType(
    {
        "Average": InductionFactors_Hellwig2022(F=1.0, c=0.69, N_c=1.0),
        "Dim": InductionFactors_Hellwig2022(F=0.9, c=0.59, N_c=0.9),
        "Dark": InductionFactors_Hellwig2022(F=0.8, c=0.525, N_c=0.8),
    }
)


@dataclass(frozen=True)
class Hellwig2022ViewingConditions:
    """Viewing conditions required by Hellwig2022.

    ``XYZ_w``, stimulus ``XYZ`` and ``Y_b`` must be expressed in the same
    reference-domain scale, normally ``Y=100``. ``L_A`` is an adapting
    luminance parameter and is not automatically scaled with ``XYZ_w``.
    """

    XYZ_w: Any = field(default_factory=lambda: D65_XYZ.copy())
    L_A: float = 64 / np.pi * 0.2
    Y_b: float = 20.0
    surround: str | InductionFactors_Hellwig2022 = "Average"
    discount_illuminant: bool = False


@dataclass(frozen=True)
class Hellwig2022Specification:
    """Hellwig2022 appearance correlates.

    Forward calculations fill ``J, C, h, s, Q, M, H, J_HK, Q_HK`` and leave
    ``HC`` as ``None``. Inverse calculations require ``J`` and ``h`` plus
    either ``C`` or ``M``.
    """

    J: Any = None
    C: Any = None
    h: Any = None
    s: Any = None
    Q: Any = None
    M: Any = None
    H: Any = None
    HC: Any = None
    J_HK: Any = None
    Q_HK: Any = None


def _resolve_surround(
    value: str | InductionFactors_Hellwig2022,
) -> InductionFactors_Hellwig2022:
    if isinstance(value, InductionFactors_Hellwig2022):
        return value
    if isinstance(value, str):
        for name, factors in VIEWING_CONDITIONS_HELLWIG2022.items():
            if value.lower() == name.lower():
                return factors
    raise ValueError(
        "surround must be one of 'Average', 'Dim', 'Dark' or an "
        "InductionFactors_Hellwig2022 instance."
    )


def _resolve_viewing_conditions(
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_Hellwig2022 | None = None,
    discount_illuminant: bool | None = None,
) -> tuple[np.ndarray, float, float, InductionFactors_Hellwig2022, bool]:
    if isinstance(XYZ_w, Hellwig2022ViewingConditions):
        conditions = XYZ_w
        XYZ_w = conditions.XYZ_w
        L_A = conditions.L_A if L_A is None else L_A
        Y_b = conditions.Y_b if Y_b is None else Y_b
        surround = conditions.surround if surround is None else surround
        if discount_illuminant is None:
            discount_illuminant = conditions.discount_illuminant

    default = Hellwig2022ViewingConditions()
    XYZ_w_array = _as_whitepoint(D65_XYZ if XYZ_w is None else XYZ_w)
    L_A_scalar = _as_positive_scalar(default.L_A if L_A is None else L_A, "L_A")
    Y_b_scalar = _as_positive_scalar(default.Y_b if Y_b is None else Y_b, "Y_b")
    factors = _resolve_surround(default.surround if surround is None else surround)
    discount = default.discount_illuminant if discount_illuminant is None else bool(discount_illuminant)
    return XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount


def _as_correlate(value: Any, name: str) -> np.ndarray:
    if value is None:
        raise ValueError(f"Hellwig2022Specification.{name} is required.")
    array = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"Hellwig2022Specification.{name} must contain only finite values.")
    return array


def _hellwig_viewing_parameters(Y_b: float, Y_w: float, L_A: float) -> tuple[float, float]:
    _n, F_L, _N_bb, _N_cb, z = _viewing_parameters(Y_b, Y_w, L_A)
    return F_L, z


def _achromatic_response(RGB_a: np.ndarray) -> np.ndarray:
    R_a, G_a, B_a = np.moveaxis(RGB_a, -1, 0)
    return 2.0 * R_a + G_a + 0.05 * B_a - 0.305


def _achromatic_response_inverse(A_w: float, J: np.ndarray, c: float, z: float) -> np.ndarray:
    return A_w * (J / 100.0) ** (1.0 / (c * z))


def _eccentricity_factor(h: np.ndarray) -> np.ndarray:
    h_r = np.radians(h)
    return (
        -0.0582 * np.cos(h_r)
        - 0.0258 * np.cos(2.0 * h_r)
        - 0.1347 * np.cos(3.0 * h_r)
        + 0.0289 * np.cos(4.0 * h_r)
        - 0.1475 * np.sin(h_r)
        - 0.0308 * np.sin(2.0 * h_r)
        + 0.0385 * np.sin(3.0 * h_r)
        + 0.0096 * np.sin(4.0 * h_r)
        + 1.0
    )


def _brightness_correlate(c: float, J: np.ndarray, A_w: float) -> np.ndarray:
    return (2.0 / c) * (J / 100.0) * A_w


def _colourfulness_correlate(
    N_c: float,
    e_t: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
) -> np.ndarray:
    return 43.0 * N_c * e_t * np.hypot(a, b)


def _chroma_correlate(M: np.ndarray, A_w: float) -> np.ndarray:
    return 35.0 * _safe_divide(M, A_w)


def _saturation_correlate(M: np.ndarray, Q: np.ndarray) -> np.ndarray:
    return 100.0 * _safe_divide(M, Q)


def _hue_angle_dependency(h: np.ndarray) -> np.ndarray:
    h_r = np.radians(h)
    return (
        -0.160 * np.cos(h_r)
        + 0.132 * np.cos(2.0 * h_r)
        - 0.405 * np.sin(h_r)
        + 0.080 * np.sin(2.0 * h_r)
        + 0.792
    )


def _opponent_dimensions_inverse(
    P_p_1: np.ndarray,
    h: np.ndarray,
    M: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    h_r = np.radians(h)
    gamma = _safe_divide(M, P_p_1)
    return gamma * np.cos(h_r), gamma * np.sin(h_r)


def XYZ_to_Hellwig2022(
    XYZ: Any,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_Hellwig2022 | None = None,
    discount_illuminant: bool | None = None,
    compute_H: bool = True,
) -> Hellwig2022Specification:
    """Convert XYZ tristimulus values to Hellwig2022 appearance correlates."""

    XYZ_array, scalar_input = _as_last_axis_three(XYZ, "XYZ")
    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )

    Y_w = float(XYZ_w_array[1])
    F_L, z = _hellwig_viewing_parameters(Y_b_scalar, Y_w, L_A_scalar)
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)

    RGB_w = CAT_CAT16 @ XYZ_w_array
    D_RGB = _adaptation_factor(RGB_w, Y_w, D)
    RGB_wc = D_RGB * RGB_w
    RGB_aw = _response_compression_forward(RGB_wc, F_L)
    A_w = float(_achromatic_response(RGB_aw))

    RGB = _dot_last(XYZ_array, CAT_CAT16)
    RGB_c = D_RGB * RGB
    RGB_a = _response_compression_forward(RGB_c, F_L)

    a, b = _opponent_dimensions_forward(RGB_a)
    h = _hue_angle(a, b)
    H = _hue_quadrature(h) if compute_H else np.full_like(h, np.nan, dtype=np.float64)
    e_t = _eccentricity_factor(h)
    A = _achromatic_response(RGB_a)

    J = 100.0 * (A / A_w) ** (factors.c * z)
    Q = _brightness_correlate(factors.c, J, A_w)
    M = _colourfulness_correlate(factors.N_c, e_t, a, b)
    C = _chroma_correlate(M, A_w)
    s = _saturation_correlate(M, Q)
    J_HK = J + _hue_angle_dependency(h) * C**0.587
    Q_HK = _brightness_correlate(factors.c, J_HK, A_w)

    return Hellwig2022Specification(
        J=_maybe_scalar(J, scalar_input),
        C=_maybe_scalar(C, scalar_input),
        h=_maybe_scalar(h, scalar_input),
        s=_maybe_scalar(s, scalar_input),
        Q=_maybe_scalar(Q, scalar_input),
        M=_maybe_scalar(M, scalar_input),
        H=_maybe_scalar(H, scalar_input),
        HC=None,
        J_HK=_maybe_scalar(J_HK, scalar_input),
        Q_HK=_maybe_scalar(Q_HK, scalar_input),
    )


def Hellwig2022_to_XYZ(
    specification: Hellwig2022Specification,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_Hellwig2022 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert Hellwig2022 appearance correlates back to XYZ values."""

    if not isinstance(specification, Hellwig2022Specification):
        raise ValueError("specification must be a Hellwig2022Specification instance.")

    J = _as_correlate(specification.J, "J")
    h = _as_correlate(specification.h, "h")
    if specification.C is None and specification.M is None:
        raise ValueError("Hellwig2022Specification.C or Hellwig2022Specification.M is required.")

    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )
    Y_w = float(XYZ_w_array[1])
    F_L, z = _hellwig_viewing_parameters(Y_b_scalar, Y_w, L_A_scalar)
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)

    RGB_w = CAT_CAT16 @ XYZ_w_array
    D_RGB = _adaptation_factor(RGB_w, Y_w, D)
    RGB_wc = D_RGB * RGB_w
    RGB_aw = _response_compression_forward(RGB_wc, F_L)
    A_w = float(_achromatic_response(RGB_aw))

    if specification.C is not None:
        C = _as_correlate(specification.C, "C")
        M = (C * A_w) / 35.0
    else:
        M = _as_correlate(specification.M, "M")
        C = _chroma_correlate(M, A_w)

    J, h, M, C = np.broadcast_arrays(J, h, M, C)
    scalar_input = J.shape == ()
    if np.any(J < 0) or np.any(M < 0) or np.any(C < 0):
        raise ValueError("Hellwig2022Specification.J and C/M must be non-negative.")

    e_t = _eccentricity_factor(h)
    A = _achromatic_response_inverse(A_w, J, factors.c, z)
    P_p_1 = 43.0 * factors.N_c * e_t
    P_p_2 = A
    a, b = _opponent_dimensions_inverse(P_p_1, h, M)
    a = np.where(M <= EPSILON, 0.0, a)
    b = np.where(M <= EPSILON, 0.0, b)

    RGB_a = _compressed_response_from_opponents(P_p_2, a, b)
    RGB_c = _response_compression_inverse(RGB_a + 0.1, F_L)
    RGB = RGB_c / D_RGB
    XYZ = _dot_last(RGB, CAT_INVERSE_CAT16)

    if scalar_input:
        return np.asarray(XYZ, dtype=np.float64).reshape(3)
    return np.asarray(XYZ, dtype=np.float64)


__all__ = [
    "InductionFactors_Hellwig2022",
    "VIEWING_CONDITIONS_HELLWIG2022",
    "Hellwig2022ViewingConditions",
    "Hellwig2022Specification",
    "XYZ_to_Hellwig2022",
    "Hellwig2022_to_XYZ",
]
