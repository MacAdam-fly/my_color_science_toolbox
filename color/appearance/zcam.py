"""ZCAM colour appearance model.

ZCAM is exposed through the project public ``XYZ`` convention, but its
formulae carry stronger HDR/PQ and absolute-luminance semantics than the
CIECAM-family models. Keep ``XYZ``, ``XYZ_w``, ``Y_b`` and ``L_A`` on a
consistent scale instead of freely normalising individual inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

import numpy as np

from color.adaptation import chromatic_adaptation_Zhai2018
from color.constants import D65_XYZ
from color.spaces.basic.jzazbz import (
    JZAZBZ_B,
    JZAZBZ_G,
    MATRIX_JZAZBZ_LMS_TO_XYZ,
    MATRIX_JZAZBZ_XYZ_TO_LMS,
    _eotf_ST2084,
    _eotf_inverse_ST2084,
)

from .ciecam02 import (
    _as_last_axis_three,
    _as_positive_scalar,
    _as_whitepoint,
    _hue_angle,
    _maybe_scalar,
    _safe_divide,
)
from .ciecam16 import _degree_of_adaptation


MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ_SAFDAR2021 = np.array(
    [
        [0.0, 1.0, 0.0],
        [3.524000, -4.066708, 0.542708],
        [0.199076, 1.096799, -1.295875],
    ],
    dtype=np.float64,
)
MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P_SAFDAR2021 = np.linalg.inv(
    MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ_SAFDAR2021
)
JZAZBZ_D0_SAFDAR2021 = 3.7035226210190005e-11
TVS_D65 = np.array([0.9504559270516716, 1.0, 1.0890577507598784], dtype=np.float64)
TVS_D65_DOMAIN_100 = TVS_D65 * 100.0
E_XYZ_DOMAIN_100 = np.full(3, 100.0, dtype=np.float64)

for _array in (
    MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ_SAFDAR2021,
    MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P_SAFDAR2021,
    TVS_D65,
    TVS_D65_DOMAIN_100,
    E_XYZ_DOMAIN_100,
):
    _array.setflags(write=False)


@dataclass(frozen=True)
class InductionFactors_ZCAM:
    """Surround induction factors for ZCAM."""

    F_s: float
    F: float
    c: float
    N_c: float


VIEWING_CONDITIONS_ZCAM = MappingProxyType(
    {
        "Average": InductionFactors_ZCAM(F_s=0.69, F=1.0, c=0.69, N_c=1.0),
        "Dim": InductionFactors_ZCAM(F_s=0.59, F=0.9, c=0.59, N_c=0.9),
        "Dark": InductionFactors_ZCAM(F_s=0.525, F=0.8, c=0.525, N_c=0.8),
    }
)


@dataclass(frozen=True)
class ZCAMViewingConditions:
    """Viewing conditions required by ZCAM."""

    XYZ_w: Any = field(default_factory=lambda: D65_XYZ.copy())
    L_A: float = 64 / np.pi * 0.2
    Y_b: float = 20.0
    surround: str | InductionFactors_ZCAM = "Average"
    discount_illuminant: bool = False


@dataclass(frozen=True)
class ZCAMSpecification:
    """ZCAM appearance correlates.

    Forward calculations fill ``J, C, h, s, Q, M, H, V, K, W`` and leave
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
    V: Any = None
    K: Any = None
    W: Any = None


def _resolve_surround(value: str | InductionFactors_ZCAM) -> InductionFactors_ZCAM:
    if isinstance(value, InductionFactors_ZCAM):
        return value
    if isinstance(value, str):
        for name, factors in VIEWING_CONDITIONS_ZCAM.items():
            if value.lower() == name.lower():
                return factors
    raise ValueError(
        "surround must be one of 'Average', 'Dim', 'Dark' or an "
        "InductionFactors_ZCAM instance."
    )


def _resolve_viewing_conditions(
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_ZCAM | None = None,
    discount_illuminant: bool | None = None,
) -> tuple[np.ndarray, float, float, InductionFactors_ZCAM, bool]:
    if isinstance(XYZ_w, ZCAMViewingConditions):
        conditions = XYZ_w
        XYZ_w = conditions.XYZ_w
        L_A = conditions.L_A if L_A is None else L_A
        Y_b = conditions.Y_b if Y_b is None else Y_b
        surround = conditions.surround if surround is None else surround
        if discount_illuminant is None:
            discount_illuminant = conditions.discount_illuminant

    default = ZCAMViewingConditions()
    XYZ_w_array = _as_whitepoint(D65_XYZ if XYZ_w is None else XYZ_w)
    L_A_scalar = _as_positive_scalar(default.L_A if L_A is None else L_A, "L_A")
    Y_b_scalar = _as_positive_scalar(default.Y_b if Y_b is None else Y_b, "Y_b")
    factors = _resolve_surround(default.surround if surround is None else surround)
    discount = default.discount_illuminant if discount_illuminant is None else bool(discount_illuminant)
    return XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount


def _as_correlate(value: Any, name: str) -> np.ndarray:
    if value is None:
        raise ValueError(f"ZCAMSpecification.{name} is required.")
    array = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"ZCAMSpecification.{name} must contain only finite values.")
    return array


def _XYZ_to_Izazbz_Safdar2021(XYZ: np.ndarray) -> np.ndarray:
    X = XYZ[..., 0]
    Y = XYZ[..., 1]
    Z = XYZ[..., 2]

    X_p = JZAZBZ_B * X - (JZAZBZ_B - 1.0) * Z
    Y_p = JZAZBZ_G * Y - (JZAZBZ_G - 1.0) * X
    XYZ_p = np.stack((X_p, Y_p, Z), axis=-1)

    LMS = XYZ_p @ MATRIX_JZAZBZ_XYZ_TO_LMS.T
    LMS_p = _eotf_inverse_ST2084(LMS)
    Izazbz = LMS_p @ MATRIX_JZAZBZ_LMS_P_TO_IZAZBZ_SAFDAR2021.T
    Izazbz[..., 0] -= JZAZBZ_D0_SAFDAR2021
    return Izazbz


def _Izazbz_to_XYZ_Safdar2021(Izazbz: np.ndarray) -> np.ndarray:
    izazbz = np.array(Izazbz, dtype=np.float64, copy=True)
    izazbz[..., 0] += JZAZBZ_D0_SAFDAR2021
    LMS_p = izazbz @ MATRIX_JZAZBZ_IZAZBZ_TO_LMS_P_SAFDAR2021.T
    LMS = _eotf_ST2084(LMS_p)
    XYZ_p = LMS @ MATRIX_JZAZBZ_LMS_TO_XYZ.T

    X_p = XYZ_p[..., 0]
    Y_p = XYZ_p[..., 1]
    Z = XYZ_p[..., 2]
    X = (X_p + (JZAZBZ_B - 1.0) * Z) / JZAZBZ_B
    Y = (Y_p + (JZAZBZ_G - 1.0) * X) / JZAZBZ_G
    return np.stack((X, Y, Z), axis=-1)


def _hue_quadrature(h: np.ndarray) -> np.ndarray:
    h = np.asarray(h, dtype=np.float64)
    h_i = np.array([33.44, 89.29, 146.30, 238.36, 393.44], dtype=np.float64)
    e_i = np.array([0.68, 0.64, 1.52, 0.77, 0.68], dtype=np.float64)
    H_i = np.array([0.0, 100.0, 200.0, 300.0, 400.0], dtype=np.float64)

    h_work = np.where(h <= h_i[0], h + 360.0, h)
    h_safe = np.where(np.isnan(h_work), 0.0, h_work)
    index = np.searchsorted(h_i, h_safe, side="left") - 1
    index = np.clip(index, 0, 3)

    h0 = h_i[index]
    h1 = h_i[index + 1]
    e0 = e_i[index]
    e1 = e_i[index + 1]
    H0 = H_i[index]
    numerator = 100.0 * (h_safe - h0) / e0
    denominator = (h_safe - h0) / e0 + (h1 - h_safe) / e1
    return H0 + _safe_divide(numerator, denominator)


def _viewing_factors(
    Y_b: float,
    Y_w: float,
    L_A: float,
) -> tuple[float, float]:
    F_b = np.sqrt(Y_b / Y_w)
    F_L = 0.171 * L_A ** (1.0 / 3.0) * (1.0 - np.exp((-48.0 / 9.0) * L_A))
    return float(F_b), float(F_L)


def _zcam_adaptation(
    XYZ: np.ndarray,
    source_white: np.ndarray,
    target_white: np.ndarray,
    D: float,
) -> np.ndarray:
    return chromatic_adaptation_Zhai2018(
        XYZ,
        source_white,
        target_white,
        D_source=D,
        D_target=D,
        baseline_white_XYZ=E_XYZ_DOMAIN_100,
        transform="CAT02",
    )


def XYZ_to_ZCAM(
    XYZ: Any,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_ZCAM | None = None,
    discount_illuminant: bool | None = None,
    compute_H: bool = True,
) -> ZCAMSpecification:
    """Convert XYZ tristimulus values to ZCAM appearance correlates."""

    XYZ_array, scalar_input = _as_last_axis_three(XYZ, "XYZ")
    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )

    Y_w = float(XYZ_w_array[1])
    F_s = factors.F_s
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)
    F_b, F_L = _viewing_factors(Y_b_scalar, Y_w, L_A_scalar)

    XYZ_D65 = _zcam_adaptation(XYZ_array, XYZ_w_array, TVS_D65_DOMAIN_100, D)
    I_z, a_z, b_z = np.moveaxis(_XYZ_to_Izazbz_Safdar2021(XYZ_D65), -1, 0)
    I_z_w = float(_XYZ_to_Izazbz_Safdar2021(XYZ_w_array)[0])

    h = _hue_angle(a_z, b_z)
    H = _hue_quadrature(h) if compute_H else np.full_like(h, np.nan, dtype=np.float64)
    e_z = 1.015 + np.cos(np.radians(89.038 + h % 360.0))

    Q_z_p = (1.6 * F_s) / (F_b**0.12)
    Q_z_m = F_s**2.2 * F_b**0.5 * F_L**0.2
    Q = 2700.0 * I_z**Q_z_p * Q_z_m
    Q_w = 2700.0 * I_z_w**Q_z_p * Q_z_m
    J = 100.0 * _safe_divide(Q, Q_w)
    M = (
        100.0
        * (a_z**2 + b_z**2) ** 0.37
        * ((e_z**0.068 * F_L**0.2) / (F_b**0.1 * I_z_w**0.78))
    )
    C = 100.0 * _safe_divide(M, Q_w)
    s = 100.0 * F_L**0.6 * np.sqrt(_safe_divide(M, Q))
    V = np.sqrt((J - 58.0) ** 2 + 3.4 * C**2)
    K = 100.0 - 0.8 * np.sqrt(J**2 + 8.0 * C**2)
    W = 100.0 - np.sqrt((100.0 - J) ** 2 + C**2)

    return ZCAMSpecification(
        J=_maybe_scalar(J, scalar_input),
        C=_maybe_scalar(C, scalar_input),
        h=_maybe_scalar(h, scalar_input),
        s=_maybe_scalar(s, scalar_input),
        Q=_maybe_scalar(Q, scalar_input),
        M=_maybe_scalar(M, scalar_input),
        H=_maybe_scalar(H, scalar_input),
        HC=None,
        V=_maybe_scalar(V, scalar_input),
        K=_maybe_scalar(K, scalar_input),
        W=_maybe_scalar(W, scalar_input),
    )


def ZCAM_to_XYZ(
    specification: ZCAMSpecification,
    XYZ_w: Any = None,
    L_A: Any = None,
    Y_b: Any = None,
    surround: str | InductionFactors_ZCAM | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert ZCAM appearance correlates back to XYZ values."""

    if not isinstance(specification, ZCAMSpecification):
        raise ValueError("specification must be a ZCAMSpecification instance.")

    J = _as_correlate(specification.J, "J")
    h = _as_correlate(specification.h, "h")
    if specification.C is None and specification.M is None:
        raise ValueError("ZCAMSpecification.C or ZCAMSpecification.M is required.")

    XYZ_w_array, L_A_scalar, Y_b_scalar, factors, discount = _resolve_viewing_conditions(
        XYZ_w, L_A, Y_b, surround, discount_illuminant
    )
    Y_w = float(XYZ_w_array[1])
    F_s = factors.F_s
    D = _degree_of_adaptation(factors.F, L_A_scalar, discount)
    F_b, F_L = _viewing_factors(Y_b_scalar, Y_w, L_A_scalar)
    I_z_w = float(_XYZ_to_Izazbz_Safdar2021(XYZ_w_array)[0])

    Q_z_p = (1.6 * F_s) / (F_b**0.12)
    Q_z_m = F_s**2.2 * F_b**0.5 * F_L**0.2
    Q_w = 2700.0 * I_z_w**Q_z_p * Q_z_m
    I_z_p = F_b**0.12 / (1.6 * F_s)
    I_z_d = 2700.0 * 100.0 * Q_z_m

    if specification.C is not None:
        C = _as_correlate(specification.C, "C")
        M = (C * Q_w) / 100.0
    else:
        M = _as_correlate(specification.M, "M")
        C = 100.0 * _safe_divide(M, Q_w)

    J, h, M, C = np.broadcast_arrays(J, h, M, C)
    scalar_input = J.shape == ()
    if np.any(J < 0) or np.any(M < 0) or np.any(C < 0):
        raise ValueError("ZCAMSpecification.J and C/M must be non-negative.")

    I_z = ((J * Q_w) / I_z_d) ** I_z_p
    e_z = 1.015 + np.cos(np.radians(89.038 + h % 360.0))
    h_r = np.radians(h)
    C_z_p = (
        (M * I_z_w**0.78 * F_b**0.1)
        / (100.0 * e_z**0.068 * F_L**0.2)
    ) ** (50.0 / 37.0)
    a_z = C_z_p * np.cos(h_r)
    b_z = C_z_p * np.sin(h_r)

    XYZ_D65 = _Izazbz_to_XYZ_Safdar2021(np.stack((I_z, a_z, b_z), axis=-1))
    XYZ_result = _zcam_adaptation(XYZ_D65, TVS_D65_DOMAIN_100, XYZ_w_array, D)

    if scalar_input:
        return np.asarray(XYZ_result, dtype=np.float64).reshape(3)
    return np.asarray(XYZ_result, dtype=np.float64)


__all__ = [
    "InductionFactors_ZCAM",
    "VIEWING_CONDITIONS_ZCAM",
    "ZCAMViewingConditions",
    "ZCAMSpecification",
    "XYZ_to_ZCAM",
    "ZCAM_to_XYZ",
]
