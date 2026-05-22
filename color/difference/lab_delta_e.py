"""Standard Lab colour-difference formulas."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._utils import as_float_result, as_triplet_array, broadcast_triplets


JND_CIE1976 = 2.3


def _as_lab_array(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite Lab array with three values on the last axis."""
    return as_triplet_array(value, name=name)


def _broadcast_lab(
    Lab_1: Sequence[float] | np.ndarray,
    Lab_2: Sequence[float] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and broadcast two Lab arrays."""
    return broadcast_triplets(Lab_1, Lab_2, name_1="Lab_1", name_2="Lab_2")


def _split_lab(
    Lab_1: Sequence[float] | np.ndarray,
    Lab_2: Sequence[float] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return broadcast Lab channels."""
    lab_1, lab_2 = _broadcast_lab(Lab_1, Lab_2)
    return (
        lab_1[..., 0],
        lab_1[..., 1],
        lab_1[..., 2],
        lab_2[..., 0],
        lab_2[..., 1],
        lab_2[..., 2],
    )


def delta_E_CIE1976(
    Lab_1: Sequence[float] | np.ndarray,
    Lab_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the CIE 1976 Delta E colour difference for Lab coordinates."""
    lab_1, lab_2 = _broadcast_lab(Lab_1, Lab_2)
    return as_float_result(np.linalg.norm(lab_1 - lab_2, axis=-1))


def delta_E_CIE1994(
    Lab_1: Sequence[float] | np.ndarray,
    Lab_2: Sequence[float] | np.ndarray,
    textiles: bool = False,
) -> np.ndarray | np.float64:
    """Return the CIE 1994 Delta E colour difference for Lab coordinates."""
    L_1, a_1, b_1, L_2, a_2, b_2 = _split_lab(Lab_1, Lab_2)

    k_1 = 0.048 if textiles else 0.045
    k_2 = 0.014 if textiles else 0.015
    k_L = 2.0 if textiles else 1.0
    k_C = 1.0
    k_H = 1.0

    C_1 = np.hypot(a_1, b_1)
    C_2 = np.hypot(a_2, b_2)

    S_L = 1.0
    S_C = 1.0 + k_1 * C_1
    S_H = 1.0 + k_2 * C_1

    delta_L = L_1 - L_2
    delta_C = C_1 - C_2
    delta_a = a_1 - a_2
    delta_b = b_1 - b_2
    delta_H_2 = np.maximum(delta_a**2 + delta_b**2 - delta_C**2, 0.0)

    d_E = np.sqrt(
        (delta_L / (k_L * S_L)) ** 2
        + (delta_C / (k_C * S_C)) ** 2
        + (np.sqrt(delta_H_2) / (k_H * S_H)) ** 2
    )
    return as_float_result(d_E)


def delta_E_CIE2000(
    Lab_1: Sequence[float] | np.ndarray,
    Lab_2: Sequence[float] | np.ndarray,
    textiles: bool = False,
) -> np.ndarray | np.float64:
    """Return the CIEDE2000 colour difference for Lab coordinates."""
    L_1, a_1, b_1, L_2, a_2, b_2 = _split_lab(Lab_1, Lab_2)

    k_L = 2.0 if textiles else 1.0
    k_C = 1.0
    k_H = 1.0

    C_1_ab = np.hypot(a_1, b_1)
    C_2_ab = np.hypot(a_2, b_2)
    C_bar_ab = (C_1_ab + C_2_ab) / 2.0
    C_bar_ab_7 = C_bar_ab**7
    G = 0.5 * (1.0 - np.sqrt(C_bar_ab_7 / (C_bar_ab_7 + 25.0**7)))

    a_p_1 = (1.0 + G) * a_1
    a_p_2 = (1.0 + G) * a_2
    C_p_1 = np.hypot(a_p_1, b_1)
    C_p_2 = np.hypot(a_p_2, b_2)

    h_p_1 = np.where(
        np.logical_and(b_1 == 0.0, a_p_1 == 0.0),
        0.0,
        np.degrees(np.arctan2(b_1, a_p_1)) % 360.0,
    )
    h_p_2 = np.where(
        np.logical_and(b_2 == 0.0, a_p_2 == 0.0),
        0.0,
        np.degrees(np.arctan2(b_2, a_p_2)) % 360.0,
    )

    delta_L_p = L_2 - L_1
    delta_C_p = C_p_2 - C_p_1

    h_delta = h_p_2 - h_p_1
    C_p_product = C_p_1 * C_p_2
    delta_h_p = np.select(
        [
            C_p_product == 0.0,
            np.abs(h_delta) <= 180.0,
            h_delta > 180.0,
            h_delta < -180.0,
        ],
        [
            0.0,
            h_delta,
            h_delta - 360.0,
            h_delta + 360.0,
        ],
    )
    delta_H_p = 2.0 * np.sqrt(C_p_product) * np.sin(np.deg2rad(delta_h_p / 2.0))

    L_bar_p = (L_1 + L_2) / 2.0
    C_bar_p = (C_p_1 + C_p_2) / 2.0

    h_abs_delta = np.abs(h_p_1 - h_p_2)
    h_sum = h_p_1 + h_p_2
    h_bar_p = np.select(
        [
            C_p_product == 0.0,
            h_abs_delta <= 180.0,
            np.logical_and(h_abs_delta > 180.0, h_sum < 360.0),
            np.logical_and(h_abs_delta > 180.0, h_sum >= 360.0),
        ],
        [
            h_sum,
            h_sum / 2.0,
            (h_sum + 360.0) / 2.0,
            (h_sum - 360.0) / 2.0,
        ],
    )

    T = (
        1.0
        - 0.17 * np.cos(np.deg2rad(h_bar_p - 30.0))
        + 0.24 * np.cos(np.deg2rad(2.0 * h_bar_p))
        + 0.32 * np.cos(np.deg2rad(3.0 * h_bar_p + 6.0))
        - 0.20 * np.cos(np.deg2rad(4.0 * h_bar_p - 63.0))
    )
    delta_theta = 30.0 * np.exp(-(((h_bar_p - 275.0) / 25.0) ** 2))
    C_bar_p_7 = C_bar_p**7
    R_C = 2.0 * np.sqrt(C_bar_p_7 / (C_bar_p_7 + 25.0**7))

    L_bar_p_minus_50_2 = (L_bar_p - 50.0) ** 2
    S_L = 1.0 + (0.015 * L_bar_p_minus_50_2) / np.sqrt(20.0 + L_bar_p_minus_50_2)
    S_C = 1.0 + 0.045 * C_bar_p
    S_H = 1.0 + 0.015 * C_bar_p * T
    R_T = -np.sin(np.deg2rad(2.0 * delta_theta)) * R_C

    d_E = np.sqrt(
        (delta_L_p / (k_L * S_L)) ** 2
        + (delta_C_p / (k_C * S_C)) ** 2
        + (delta_H_p / (k_H * S_H)) ** 2
        + R_T * (delta_C_p / (k_C * S_C)) * (delta_H_p / (k_H * S_H))
    )
    return as_float_result(d_E)


def delta_E_CMC(
    Lab_1: Sequence[float] | np.ndarray,
    Lab_2: Sequence[float] | np.ndarray,
    l: float = 2.0,  # noqa: E741
    c: float = 1.0,
) -> np.ndarray | np.float64:
    """Return the CMC l:c colour difference for Lab coordinates."""
    if l <= 0 or c <= 0:
        raise ValueError("l and c must be positive")

    L_1, a_1, b_1, L_2, a_2, b_2 = _split_lab(Lab_1, Lab_2)

    C_1 = np.hypot(a_1, b_1)
    C_2 = np.hypot(a_2, b_2)
    S_L = np.where(L_1 < 16.0, 0.511, (0.040975 * L_1) / (1.0 + 0.01765 * L_1))
    S_C = 0.0638 * C_1 / (1.0 + 0.0131 * C_1) + 0.638
    h_1 = np.degrees(np.arctan2(b_1, a_1)) % 360.0
    T = np.where(
        np.logical_and(h_1 >= 164.0, h_1 <= 345.0),
        0.56 + np.abs(0.2 * np.cos(np.deg2rad(h_1 + 168.0))),
        0.36 + np.abs(0.4 * np.cos(np.deg2rad(h_1 + 35.0))),
    )
    C_1_4 = C_1**4
    F = np.sqrt(C_1_4 / (C_1_4 + 1900.0))
    S_H = S_C * (F * T + 1.0 - F)

    delta_L = L_1 - L_2
    delta_C = C_1 - C_2
    delta_a = a_1 - a_2
    delta_b = b_1 - b_2
    delta_H_2 = np.maximum(delta_a**2 + delta_b**2 - delta_C**2, 0.0)

    d_E = np.sqrt(
        (delta_L / (l * S_L)) ** 2
        + (delta_C / (c * S_C)) ** 2
        + delta_H_2 / (S_H**2)
    )
    return as_float_result(d_E)


__all__ = [
    "JND_CIE1976",
    "delta_E_CIE1976",
    "delta_E_CIE1994",
    "delta_E_CIE2000",
    "delta_E_CMC",
]
