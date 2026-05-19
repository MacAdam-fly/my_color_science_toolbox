"""Correlated colour temperature helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


_CIE_D_MIN_CCT = 4000.0
_CIE_D_MAX_CCT = 25000.0
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


def _as_finite_array(value: float | Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array."""
    arr = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _as_last_axis_pairs(
    value: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Return *value* as a finite float array with two values on the last axis."""
    arr = _as_finite_array(value, name=name)
    if arr.shape == () or arr.shape[-1] != 2:
        raise ValueError(f"{name} must have 2 values on the last axis")
    return arr


def _scalar_or_array(value: np.ndarray) -> float | np.ndarray:
    """Return a Python float for scalar arrays, otherwise the array itself."""
    if value.shape == ():
        return float(value)
    return value


def CCT_to_mired(CCT: float | Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Convert correlated colour temperature in kelvins to mired."""
    cct = _as_finite_array(CCT, name="CCT")
    if np.any(cct == 0):
        raise ValueError("CCT must be non-zero")
    return _scalar_or_array(1.0e6 / cct)


def mired_to_CCT(mired: float | Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Convert mired to correlated colour temperature in kelvins."""
    value = _as_finite_array(mired, name="mired")
    if np.any(value == 0):
        raise ValueError("mired must be non-zero")
    return _scalar_or_array(1.0e6 / value)


def xy_to_CCT_McCamy1992(xy: Sequence[float] | np.ndarray) -> float | np.ndarray:
    """Return CCT from CIE xy coordinates using the McCamy (1992) approximation."""
    xy_arr = _as_last_axis_pairs(xy, name="xy")
    x = xy_arr[..., 0]
    y = xy_arr[..., 1]
    denominator = y - 0.1858
    if np.any(denominator == 0):
        raise ValueError("xy produces a zero denominator for McCamy 1992")
    n = (x - 0.3320) / denominator
    cct = -449.0 * n**3 + 3525.0 * n**2 - 6823.3 * n + 5520.33
    return _scalar_or_array(cct)


def CCT_to_xy_CIE_D(CCT: float | Sequence[float] | np.ndarray) -> np.ndarray:
    """Return CIE D-series daylight locus xy coordinates from CCT."""
    cct = _as_finite_array(CCT, name="CCT")
    if np.any((cct < _CIE_D_MIN_CCT) | (cct > _CIE_D_MAX_CCT)):
        raise ValueError("CCT must be in the [4000, 25000] interval for CIE D")

    cct_2 = cct**2
    cct_3 = cct**3
    x = np.where(
        cct <= 7000.0,
        -4.6070e9 / cct_3 + 2.9678e6 / cct_2 + 0.09911e3 / cct + 0.244063,
        -2.0064e9 / cct_3 + 1.9018e6 / cct_2 + 0.24748e3 / cct + 0.237040,
    )
    y = -3.0 * x**2 + 2.870 * x - 0.275
    return np.stack([x, y], axis=-1)


def xy_to_CCT(
    xy: Sequence[float] | np.ndarray,
    *,
    method: str = "mccamy1992",
) -> float | np.ndarray:
    """Return CCT from CIE xy coordinates using a named method."""
    method_normalized = method.lower().replace(" ", "").replace("_", "").replace("-", "")
    if method_normalized != "mccamy1992":
        raise ValueError("method must be 'mccamy1992'")
    return xy_to_CCT_McCamy1992(xy)


def CCT_to_xy(
    CCT: float | Sequence[float] | np.ndarray,
    *,
    method: str = "cie_d",
) -> np.ndarray:
    """Return CIE xy coordinates from CCT using a named method."""
    method_normalized = method.lower().replace(" ", "").replace("_", "").replace("-", "")
    if method_normalized not in {"cied", "daylight"}:
        raise ValueError("method must be 'cie_d'")
    return CCT_to_xy_CIE_D(CCT)


def xy_to_uv1960(xy: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE xy chromaticity coordinates to CIE 1960 UCS uv."""
    xy_arr = _as_last_axis_pairs(xy, name="xy")
    x = xy_arr[..., 0]
    y = xy_arr[..., 1]
    denominator = -2.0 * x + 12.0 * y + 3.0
    if np.any(denominator == 0):
        raise ValueError("xy produces a zero denominator for CIE 1960 uv")
    u = 4.0 * x / denominator
    v = 6.0 * y / denominator
    return np.stack([u, v], axis=-1)


def XYZ_to_uv1960(XYZ: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to CIE 1960 UCS uv."""
    xyz = _as_finite_array(XYZ, name="XYZ")
    if xyz.shape == () or xyz.shape[-1] != 3:
        raise ValueError("XYZ must have 3 values on the last axis")
    X = xyz[..., 0]
    Y = xyz[..., 1]
    Z = xyz[..., 2]
    denominator = X + 15.0 * Y + 3.0 * Z
    if np.any(denominator == 0):
        raise ValueError("XYZ produces a zero denominator for CIE 1960 uv")
    u = 4.0 * X / denominator
    v = 6.0 * Y / denominator
    return np.stack([u, v], axis=-1)


def uv1960_to_xy(uv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE 1960 UCS uv coordinates to CIE xy chromaticity coordinates."""
    uv_arr = _as_last_axis_pairs(uv, name="uv")
    u = uv_arr[..., 0]
    v = uv_arr[..., 1]
    denominator = 2.0 * u - 8.0 * v + 4.0
    if np.any(denominator == 0):
        raise ValueError("uv produces a zero denominator for CIE xy")
    x = 3.0 * u / denominator
    y = 2.0 * v / denominator
    return np.stack([x, y], axis=-1)


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
    uv_arr = _as_last_axis_pairs(uv, name="uv")
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
    cct_duv = _as_last_axis_pairs(CCT_Duv, name="CCT_Duv")
    result = [
        _CCT_to_uv_Robertson1968_single(item) for item in cct_duv.reshape(-1, 2)
    ]
    return np.reshape(result, cct_duv.shape)


def uv_to_CCT(
    uv: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CCT and Duv from CIE 1960 UCS uv using a named method."""
    method_normalized = method.lower().replace(" ", "").replace("_", "").replace("-", "")
    if method_normalized != "robertson1968":
        raise ValueError("method must be 'robertson1968'")
    return uv_to_CCT_Robertson1968(uv)


def CCT_to_uv(
    CCT_Duv: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CIE 1960 UCS uv from CCT and Duv using a named method."""
    method_normalized = method.lower().replace(" ", "").replace("_", "").replace("-", "")
    if method_normalized != "robertson1968":
        raise ValueError("method must be 'robertson1968'")
    return CCT_to_uv_Robertson1968(CCT_Duv)


def xy_to_CCT_Duv(
    xy: Sequence[float] | np.ndarray,
    *,
    method: str = "robertson1968",
) -> np.ndarray:
    """Return CCT and Duv from CIE xy coordinates using a named method."""
    return uv_to_CCT(xy_to_uv1960(xy), method=method)


__all__ = [
    "CCT_to_mired",
    "mired_to_CCT",
    "xy_to_CCT_McCamy1992",
    "CCT_to_xy_CIE_D",
    "xy_to_CCT",
    "CCT_to_xy",
    "xy_to_uv1960",
    "XYZ_to_uv1960",
    "uv1960_to_xy",
    "uv_to_CCT_Robertson1968",
    "CCT_to_uv_Robertson1968",
    "uv_to_CCT",
    "CCT_to_uv",
    "xy_to_CCT_Duv",
]
