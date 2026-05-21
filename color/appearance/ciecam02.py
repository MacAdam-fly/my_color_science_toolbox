"""CIECAM02 colour appearance model.

This module uses the CIECAM02 reference domain: stimulus and whitepoint
``XYZ`` values are expected on the ``Y=100`` scale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np

from color.constants import CAT_CAT02, D65_XYZ


MATRIX_XYZ_TO_HPE = np.array(
    [
        [0.38971, 0.68898, -0.07868],
        [-0.22981, 1.18340, 0.04641],
        [0.0, 0.0, 1.0],
    ],
    dtype=np.float64,
)
MATRIX_HPE_TO_XYZ = np.linalg.inv(MATRIX_XYZ_TO_HPE)
CAT_INVERSE_CAT02 = np.linalg.inv(CAT_CAT02)
MATRIX_CAT02_TO_HPE = MATRIX_XYZ_TO_HPE @ CAT_INVERSE_CAT02
MATRIX_HPE_TO_CAT02 = CAT_CAT02 @ MATRIX_HPE_TO_XYZ

EPSILON = np.finfo(np.float64).eps


@dataclass(frozen=True)
class InductionFactors_CIECAM02:
    """Surround induction factors for CIECAM02."""

    F: float
    c: float
    N_c: float


VIEWING_CONDITIONS_CIECAM02 = MappingProxyType(
    {
        "Average": InductionFactors_CIECAM02(F=1.0, c=0.69, N_c=1.0),
        "Dim": InductionFactors_CIECAM02(F=0.9, c=0.59, N_c=0.95),
        "Dark": InductionFactors_CIECAM02(F=0.8, c=0.525, N_c=0.8),
    }
)


@dataclass(frozen=True)
class CIECAM02ViewingConditions:
    """Viewing conditions required by CIECAM02."""

    XYZ_w: Any = field(default_factory=lambda: D65_XYZ.copy())
    L_A: float = 64 / np.pi * 0.2
    Y_b: float = 20.0
    surround: str | InductionFactors_CIECAM02 = "Average"
    discount_illuminant: bool = False


@dataclass(frozen=True)
class CIECAM02Specification:
    """CIECAM02 appearance correlates."""

    J: Any = None
    C: Any = None
    h: Any = None
    s: Any = None
    Q: Any = None
    M: Any = None
    H: Any = None
    HC: Any = None


def _as_last_axis_three(values: Any, name: str) -> tuple[np.ndarray, bool]:
    array = np.asarray(values, dtype=np.float64)
    if array.shape == (3,):
        scalar_input = True
    elif array.ndim >= 1 and array.shape[-1] == 3:
        scalar_input = False
    else:
        raise ValueError(f"{name} must have shape (3,) or (..., 3).")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values.")
    return array, scalar_input


def _as_whitepoint(values: Any) -> np.ndarray:
    if values is None:
        values = D65_XYZ
    white = np.asarray(values, dtype=np.float64)
    if white.shape != (3,):
        raise ValueError("XYZ_w must have shape (3,).")
    if not np.all(np.isfinite(white)) or np.any(white <= 0):
        raise ValueError("XYZ_w must contain finite positive tristimulus values.")
    return white


def _as_positive_scalar(value: Any, name: str) -> float:
    scalar = float(value)
    if not np.isfinite(scalar) or scalar <= 0:
        raise ValueError(f"{name} must be a finite positive scalar.")
    return scalar


def _resolve_surround(value: str | InductionFactors_CIECAM02) -> InductionFactors_CIECAM02:
    if isinstance(value, InductionFactors_CIECAM02):
        return value
    if isinstance(value, str):
        for name, factors in VIEWING_CONDITIONS_CIECAM02.items():
            if value.lower() == name.lower():
                return factors
    raise ValueError(
        "surround must be one of 'Average', 'Dim', 'Dark' or an "
        "InductionFactors_CIECAM02 instance."
    )


def _resolve_viewing_conditions(
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> tuple[np.ndarray, float, float, InductionFactors_CIECAM02, bool]:
    if isinstance(XYZ_w, CIECAM02ViewingConditions):
        conditions = XYZ_w
        XYZ_w = conditions.XYZ_w
        L_A = conditions.L_A if L_A is None else L_A
        Y_b = conditions.Y_b if Y_b is None else Y_b
        surround = conditions.surround if surround is None else surround
        if discount_illuminant is None:
            discount_illuminant = conditions.discount_illuminant

    default = CIECAM02ViewingConditions()
    XYZ_w_array = _as_whitepoint(D65_XYZ if XYZ_w is None else XYZ_w)
    L_A_scalar = _as_positive_scalar(default.L_A if L_A is None else L_A, "L_A")
    Y_b_scalar = _as_positive_scalar(default.Y_b if Y_b is None else Y_b, "Y_b")
    factors = _resolve_surround(default.surround if surround is None else surround)
    discount = default.discount_illuminant if discount_illuminant is None else bool(discount_illuminant)
    return XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount


def _dot_last(values: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return np.asarray(values, dtype=np.float64) @ matrix.T


def _safe_divide(numerator: Any, denominator: Any, default: float = 0.0) -> np.ndarray:
    numerator_array = np.asarray(numerator, dtype=np.float64)
    denominator_array = np.asarray(denominator, dtype=np.float64)
    return np.divide(
        numerator_array,
        denominator_array,
        out=np.full(np.broadcast_shapes(numerator_array.shape, denominator_array.shape), default),
        where=np.abs(denominator_array) > EPSILON,
    )


def _maybe_scalar(values: Any, scalar_input: bool) -> Any:
    array = np.asarray(values)
    if scalar_input and array.shape == ():
        return float(array)
    return array


def _viewing_parameters(Y_b: float, Y_w: float, L_A: float) -> tuple[float, float, float, float, float]:
    n = Y_b / Y_w
    k = 1.0 / (5.0 * L_A + 1.0)
    k4 = k**4
    F_L = 0.2 * k4 * (5.0 * L_A) + 0.1 * (1.0 - k4) ** 2 * (5.0 * L_A) ** (1.0 / 3.0)
    N_bb = N_cb = 0.725 * (1.0 / n) ** 0.2
    z = 1.48 + np.sqrt(n)
    return n, F_L, N_bb, N_cb, z


def _degree_of_adaptation(F: float, L_A: float, discount_illuminant: bool) -> float:
    if discount_illuminant:
        return 1.0
    D = F * (1.0 - (1.0 / 3.6) * np.exp((-L_A - 42.0) / 92.0))
    return float(np.clip(D, 0.0, 1.0))


def _full_chromatic_adaptation_forward(
    RGB: np.ndarray, RGB_w: np.ndarray, Y_w: float, D: float
) -> np.ndarray:
    return (Y_w * D / RGB_w + 1.0 - D) * RGB


def _full_chromatic_adaptation_inverse(
    RGB: np.ndarray, RGB_w: np.ndarray, Y_w: float, D: float
) -> np.ndarray:
    return RGB / (Y_w * D / RGB_w + 1.0 - D)


def _response_compression_forward(RGB: np.ndarray, F_L: float) -> np.ndarray:
    F_L_RGB = (F_L * np.abs(RGB) / 100.0) ** 0.42
    return 400.0 * np.sign(RGB) * F_L_RGB / (27.13 + F_L_RGB) + 0.1


def _response_compression_inverse(RGB_a: np.ndarray, F_L: float) -> np.ndarray:
    magnitude = np.abs(RGB_a - 0.1)
    return (
        np.sign(RGB_a - 0.1)
        * 100.0
        / F_L
        * ((27.13 * magnitude) / (400.0 - magnitude)) ** (1.0 / 0.42)
    )


def _opponent_dimensions_forward(RGB_a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    R_a, G_a, B_a = np.moveaxis(RGB_a, -1, 0)
    a = R_a - 12.0 * G_a / 11.0 + B_a / 11.0
    b = (R_a + G_a - 2.0 * B_a) / 9.0
    return a, b


def _hue_angle(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.degrees(np.arctan2(b, a)) % 360.0


def _hue_quadrature(h: np.ndarray) -> np.ndarray:
    h = np.asarray(h, dtype=np.float64)
    h_i = np.array([20.14, 90.0, 164.25, 237.53, 380.14], dtype=np.float64)
    e_i = np.array([0.8, 0.7, 1.0, 1.2, 0.8], dtype=np.float64)
    H_i = np.array([0.0, 100.0, 200.0, 300.0, 400.0], dtype=np.float64)

    h_safe = np.where(np.isnan(h), 0.0, h)
    index = np.searchsorted(h_i, h_safe, side="left") - 1
    index = np.clip(index, 0, 3)
    h0 = h_i[index]
    h1 = h_i[index + 1]
    e0 = e_i[index]
    e1 = e_i[index + 1]
    H0 = H_i[index]

    denominator = (h_safe - h0) / e0 + (h1 - h_safe) / e1
    H = H0 + _safe_divide(100.0 * (h_safe - h0) / e0, denominator)

    low_denominator = h_safe / 0.856 + (20.14 - h_safe) / 0.8
    low = 385.9 + _safe_divide(14.1 * h_safe / 0.856, low_denominator)
    H = np.where(h_safe < 20.14, low, H)

    high_denominator = (h_safe - h0) / e0 + (360.0 - h_safe) / 0.856
    high = H0 + _safe_divide(85.9 * (h_safe - h0) / e0, high_denominator)
    H = np.where(h_safe >= 237.53, high, H)
    return H


def _eccentricity_factor(h: np.ndarray) -> np.ndarray:
    return 0.25 * (np.cos(2.0 + h * np.pi / 180.0) + 3.8)


def _achromatic_response(RGB_a: np.ndarray, N_bb: float) -> np.ndarray:
    R_a, G_a, B_a = np.moveaxis(RGB_a, -1, 0)
    return (2.0 * R_a + G_a + B_a / 20.0 - 0.305) * N_bb


def _temporary_magnitude(
    N_c: float,
    N_cb: float,
    e_t: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    RGB_a: np.ndarray,
) -> np.ndarray:
    R_a, G_a, B_a = np.moveaxis(RGB_a, -1, 0)
    return (50000.0 / 13.0 * N_c * N_cb) * _safe_divide(
        e_t * np.sqrt(a**2 + b**2), R_a + G_a + 21.0 * B_a / 20.0
    )


def _opponent_dimensions_inverse(P_n: np.ndarray, h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    P_1, P_2, P_3 = np.moveaxis(P_n, -1, 0)
    hr = np.radians(h)
    sin_hr = np.sin(hr)
    cos_hr = np.cos(hr)
    cos_div_sin = _safe_divide(cos_hr, sin_hr)
    sin_div_cos = _safe_divide(sin_hr, cos_hr)
    P_4 = _safe_divide(P_1, sin_hr)
    P_5 = _safe_divide(P_1, cos_hr)
    n = P_2 * (2.0 + P_3) * (460.0 / 1403.0)

    use_sin = np.abs(sin_hr) >= np.abs(cos_hr)
    b_sin = n / (
        P_4
        + (2.0 + P_3) * (220.0 / 1403.0) * cos_div_sin
        - (27.0 / 1403.0)
        + P_3 * (6300.0 / 1403.0)
    )
    a_sin = b_sin * cos_div_sin

    a_cos = n / (
        P_5
        + (2.0 + P_3) * (220.0 / 1403.0)
        - ((27.0 / 1403.0) - P_3 * (6300.0 / 1403.0)) * sin_div_cos
    )
    b_cos = a_cos * sin_div_cos
    return np.where(use_sin, a_sin, a_cos), np.where(use_sin, b_sin, b_cos)


def _compressed_response_from_opponents(P_2: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    stacked = np.stack([P_2, a, b], axis=-1)
    matrix = np.array(
        [
            [460.0, 451.0, 288.0],
            [460.0, -891.0, -261.0],
            [460.0, -220.0, -6300.0],
        ],
        dtype=np.float64,
    )
    return _dot_last(stacked, matrix) / 1403.0


def XYZ_to_CIECAM02(
    XYZ: Any,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> CIECAM02Specification:
    """Convert XYZ tristimulus values to CIECAM02 appearance correlates."""

    XYZ_array, scalar_input = _as_last_axis_three(XYZ, "XYZ")
    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )

    Y_w = float(XYZ_w_array[1])
    n, F_L, N_bb, N_cb, z = _viewing_parameters(Y_b_scalar, Y_w, L_A_scalar)
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)

    RGB = _dot_last(XYZ_array, CAT_CAT02)
    RGB_w = CAT_CAT02 @ XYZ_w_array
    RGB_c = _full_chromatic_adaptation_forward(RGB, RGB_w, Y_w, D)
    RGB_wc = _full_chromatic_adaptation_forward(RGB_w, RGB_w, Y_w, D)

    RGB_p = _dot_last(RGB_c, MATRIX_CAT02_TO_HPE)
    RGB_pw = MATRIX_CAT02_TO_HPE @ RGB_wc
    RGB_a = _response_compression_forward(RGB_p, F_L)
    RGB_aw = _response_compression_forward(RGB_pw, F_L)

    a, b = _opponent_dimensions_forward(RGB_a)
    h = _hue_angle(a, b)
    H = _hue_quadrature(h)
    e_t = _eccentricity_factor(h)

    A = _achromatic_response(RGB_a, N_bb)
    A_w = float(_achromatic_response(RGB_aw, N_bb))
    J = 100.0 * (A / A_w) ** (factors.c * z)
    Q = (4.0 / factors.c) * np.sqrt(J / 100.0) * (A_w + 4.0) * F_L**0.25
    t = _temporary_magnitude(factors.N_c, N_cb, e_t, a, b, RGB_a)
    C = t**0.9 * np.sqrt(J / 100.0) * (1.64 - 0.29**n) ** 0.73
    M = C * F_L**0.25
    s = 100.0 * np.sqrt(_safe_divide(M, Q))

    return CIECAM02Specification(
        J=_maybe_scalar(J, scalar_input),
        C=_maybe_scalar(C, scalar_input),
        h=_maybe_scalar(h, scalar_input),
        s=_maybe_scalar(s, scalar_input),
        Q=_maybe_scalar(Q, scalar_input),
        M=_maybe_scalar(M, scalar_input),
        H=_maybe_scalar(H, scalar_input),
        HC=None,
    )


def _as_correlate(value: Any, name: str) -> np.ndarray:
    if value is None:
        raise ValueError(f"CIECAM02Specification.{name} is required.")
    array = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"CIECAM02Specification.{name} must contain only finite values.")
    return array


def CIECAM02_to_XYZ(
    specification: CIECAM02Specification,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CIECAM02 appearance correlates back to XYZ tristimulus values."""

    if not isinstance(specification, CIECAM02Specification):
        raise ValueError("specification must be a CIECAM02Specification instance.")

    J = _as_correlate(specification.J, "J")
    h = _as_correlate(specification.h, "h")
    if specification.C is None and specification.M is None:
        raise ValueError("CIECAM02Specification.C or CIECAM02Specification.M is required.")

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
        raise ValueError("CIECAM02Specification.J and C must be non-negative.")

    RGB_w = CAT_CAT02 @ XYZ_w_array
    RGB_wc = _full_chromatic_adaptation_forward(RGB_w, RGB_w, Y_w, D)
    RGB_pw = MATRIX_CAT02_TO_HPE @ RGB_wc
    RGB_aw = _response_compression_forward(RGB_pw, F_L)
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
    RGB_p = _response_compression_inverse(RGB_a, F_L)
    RGB_c = _dot_last(RGB_p, MATRIX_HPE_TO_CAT02)
    RGB = _full_chromatic_adaptation_inverse(RGB_c, RGB_w, Y_w, D)
    XYZ = _dot_last(RGB, CAT_INVERSE_CAT02)

    if scalar_input:
        return np.asarray(XYZ, dtype=np.float64).reshape(3)
    return np.asarray(XYZ, dtype=np.float64)
