"""Robertson (1968) CCT and Duv helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._helpers import as_last_axis_pairs
from .conversions import CCT_to_mired, mired_to_CCT


_ROBERTSON_ISOTEMPERATURE_LINES = (
    (0.0, 0.18006, 0.26352, -0.24341),
    (10.0, 0.18066, 0.26589, -0.25479),
    (20.0, 0.18133, 0.26846, -0.26876),
    (30.0, 0.18208, 0.27119, -0.28539),
    (40.0, 0.18293, 0.27407, -0.30470),
    (50.0, 0.18388, 0.27709, -0.32675),
    (60.0, 0.18494, 0.28021, -0.35156),
    (70.0, 0.18611, 0.28342, -0.37915),
    (80.0, 0.18740, 0.28668, -0.40955),
    (90.0, 0.18880, 0.28997, -0.44278),
    (100.0, 0.19032, 0.29326, -0.47888),
    (125.0, 0.19462, 0.30141, -0.58204),
    (150.0, 0.19962, 0.30921, -0.70471),
    (175.0, 0.20525, 0.31647, -0.84901),
    (200.0, 0.21142, 0.32312, -1.0182),
    (225.0, 0.21807, 0.32909, -1.2168),
    (250.0, 0.22511, 0.33439, -1.4512),
    (275.0, 0.23247, 0.33904, -1.7298),
    (300.0, 0.24010, 0.34308, -2.0637),
    (325.0, 0.24792, 0.34655, -2.4681),
    (350.0, 0.25591, 0.34951, -2.9641),
    (375.0, 0.26400, 0.35200, -3.5814),
    (400.0, 0.27218, 0.35407, -4.3633),
    (425.0, 0.28039, 0.35577, -5.3762),
    (450.0, 0.28863, 0.35714, -6.7262),
    (475.0, 0.29685, 0.35823, -8.5955),
    (500.0, 0.30505, 0.35907, -11.324),
    (525.0, 0.31320, 0.35968, -15.628),
    (550.0, 0.32129, 0.36011, -23.325),
    (575.0, 0.32931, 0.36038, -40.770),
    (600.0, 0.33724, 0.36051, -116.45),
)
_ROBERTSON_LINES = np.asarray(_ROBERTSON_ISOTEMPERATURE_LINES, dtype=np.float64)


def _uv_to_CCT_Robertson1968_single(uv: np.ndarray) -> np.ndarray:
    """Return Robertson 1968 CCT and Duv for one CIE 1960 UCS uv pair."""
    u, v = uv
    last_dt = 0.0
    last_du = 0.0
    last_dv = 0.0
    result = np.array([np.nan, np.nan], dtype=np.float64)

    for index in range(1, len(_ROBERTSON_LINES)):
        r, line_u, line_v, slope = _ROBERTSON_LINES[index]
        prev_r, prev_u, prev_v, _prev_slope = _ROBERTSON_LINES[index - 1]

        du = 1.0
        dv = slope
        length = np.hypot(du, dv)
        du /= length
        dv /= length

        uu = u - line_u
        vv = v - line_v
        dt = -uu * dv + vv * du

        if dt <= 0.0 or index == len(_ROBERTSON_LINES) - 1:
            if dt > 0.0:
                dt = 0.0
            dt = -dt
            f = 0.0 if index == 1 else dt / (last_dt + dt)
            cct = mired_to_CCT(prev_r * f + r * (1.0 - f))

            locus_u = prev_u * f + line_u * (1.0 - f)
            locus_v = prev_v * f + line_v * (1.0 - f)
            uu = u - locus_u
            vv = v - locus_v

            du = du * (1.0 - f) + last_du * f
            dv = dv * (1.0 - f) + last_dv * f
            length = np.hypot(du, dv)
            du /= length
            dv /= length

            d_uv = uu * du + vv * dv
            result = np.array([cct, -d_uv], dtype=np.float64)
            break

        last_dt = dt
        last_du = du
        last_dv = dv

    return result


def uv_to_CCT_Robertson1968(uv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return CCT and Duv from CIE 1960 UCS uv using Robertson (1968)."""
    uv_arr = as_last_axis_pairs(uv, name="uv")
    result = [_uv_to_CCT_Robertson1968_single(item) for item in uv_arr.reshape(-1, 2)]
    return np.reshape(result, uv_arr.shape)


def _CCT_to_uv_Robertson1968_single(CCT_Duv: np.ndarray) -> np.ndarray:
    """Return CIE 1960 UCS uv for one Robertson 1968 CCT and Duv pair."""
    cct, d_uv = CCT_Duv
    if cct == 0:
        raise ValueError("CCT must be non-zero")
    r = CCT_to_mired(cct)
    lines = _ROBERTSON_LINES
    min_r = lines[0, 0]
    max_r = lines[-1, 0]
    if r < min_r or r > max_r:
        raise ValueError(
            f"CCT is outside the Robertson 1968 range "
            f"[{mired_to_CCT(max_r)}, infinity)"
        )

    for index in range(len(lines) - 1):
        r0, u0, v0, slope0 = lines[index]
        r1, u1, v1, slope1 = lines[index + 1]
        if r < r1 or index == len(lines) - 2:
            f = (r1 - r) / (r1 - r0)
            u = u0 * f + u1 * (1.0 - f)
            v = v0 * f + v1 * (1.0 - f)

            du0, dv0 = 1.0, slope0
            du1, dv1 = 1.0, slope1
            length0 = np.hypot(du0, dv0)
            length1 = np.hypot(du1, dv1)
            du0, dv0 = du0 / length0, dv0 / length0
            du1, dv1 = du1 / length1, dv1 / length1

            du = du0 * f + du1 * (1.0 - f)
            dv = dv0 * f + dv1 * (1.0 - f)
            length = np.hypot(du, dv)
            du, dv = du / length, dv / length

            u += du * -d_uv
            v += dv * -d_uv
            return np.array([u, v], dtype=np.float64)

    raise ValueError("CCT is outside the Robertson 1968 range")


def CCT_to_uv_Robertson1968(CCT_Duv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return CIE 1960 UCS uv from CCT and Duv using Robertson (1968)."""
    cct_duv = as_last_axis_pairs(CCT_Duv, name="CCT_Duv")
    result = [
        _CCT_to_uv_Robertson1968_single(item) for item in cct_duv.reshape(-1, 2)
    ]
    return np.reshape(result, cct_duv.shape)


__all__ = [
    "uv_to_CCT_Robertson1968",
    "CCT_to_uv_Robertson1968",
]
