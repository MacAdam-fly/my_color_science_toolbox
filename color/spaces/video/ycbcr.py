"""YCbCr video colour encoding helpers.

YCbCr operates on non-linear R'G'B' code values. These helpers expose explicit
video signal conversion APIs and are not registered in the generic colour-space
router.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Sequence

import numpy as np

from color.utils.arrays import as_last_axis_triplets
from color.utils.names import canonical_method_name


WEIGHTS_YCBCR = MappingProxyType(
    {
        "ITU-R BT.601": np.array([0.2990, 0.1140], dtype=np.float64),
        "ITU-R BT.709": np.array([0.2126, 0.0722], dtype=np.float64),
        "ITU-R BT.2020": np.array([0.2627, 0.0593], dtype=np.float64),
        "SMPTE-240M": np.array([0.2122, 0.0865], dtype=np.float64),
    }
)
"""Luma weighting presets as ``(K_r, K_b)``."""

_WEIGHT_ALIASES = {
    "bt601": "ITU-R BT.601",
    "iturbt601": "ITU-R BT.601",
    "601": "ITU-R BT.601",
    "bt709": "ITU-R BT.709",
    "iturbt709": "ITU-R BT.709",
    "709": "ITU-R BT.709",
    "bt2020": "ITU-R BT.2020",
    "iturbt2020": "ITU-R BT.2020",
    "rec2020": "ITU-R BT.2020",
    "2020": "ITU-R BT.2020",
    "smpte240m": "SMPTE-240M",
    "240m": "SMPTE-240M",
}

for _weights in WEIGHTS_YCBCR.values():
    _weights.setflags(write=False)


def _as_bits(bits: int) -> int:
    bits_int = int(bits)
    if bits_int <= 0:
        raise ValueError("bit depth must be a positive integer.")
    return bits_int


def _as_range(value: Sequence[float] | np.ndarray, *, size: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.shape != (size,):
        raise ValueError(f"{name} must have shape ({size},).")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values.")
    return array


def _resolve_weights(
    standard: str | Sequence[float] | np.ndarray = "ITU-R BT.709",
) -> np.ndarray:
    if isinstance(standard, str):
        key = canonical_method_name(standard)
        try:
            return WEIGHTS_YCBCR[_WEIGHT_ALIASES[key]]
        except KeyError as exc:
            names = ", ".join(WEIGHTS_YCBCR)
            raise ValueError(f"unknown YCbCr standard {standard!r}; expected one of: {names}") from exc

    weights = np.asarray(standard, dtype=np.float64)
    if weights.shape != (2,):
        raise ValueError("YCbCr weights must have shape (2,) as (K_r, K_b).")
    if not np.all(np.isfinite(weights)):
        raise ValueError("YCbCr weights must contain only finite values.")
    K_r, K_b = weights
    if K_r <= 0 or K_b <= 0 or K_r + K_b >= 1:
        raise ValueError("YCbCr weights must satisfy K_r > 0, K_b > 0 and K_r + K_b < 1.")
    return weights


def round_BT2100(values: Sequence[float] | np.ndarray) -> np.ndarray:
    """Round values using the ITU-R BT.2100 half-up rule."""

    array = np.asarray(values, dtype=np.float64)
    return np.sign(array) * np.floor(np.abs(array) + 0.5)


def code_value_range(bits: int = 10, is_legal: bool = False, is_int: bool = False) -> np.ndarray:
    """Return RGB code value range for bit-depth and legal/full range mode."""

    bits_int = _as_bits(bits)
    if is_legal:
        values = np.array([16.0, 235.0], dtype=np.float64) * 2 ** (bits_int - 8)
    else:
        values = np.array([0.0, 2**bits_int - 1.0], dtype=np.float64)
    if not is_int:
        values = values / (2**bits_int - 1.0)
    return values


def ranges_YCbCr(bits: int = 8, is_legal: bool = False, is_int: bool = False) -> np.ndarray:
    """Return ``Y_min, Y_max, C_min, C_max`` for a YCbCr representation."""

    bits_int = _as_bits(bits)
    if is_legal:
        values = np.array([16.0, 235.0, 16.0, 240.0], dtype=np.float64) * 2 ** (bits_int - 8)
    else:
        values = np.array([0.0, 2**bits_int - 1.0, 0.0, 2**bits_int - 1.0], dtype=np.float64)

    if not is_int:
        values = values / (2**bits_int - 1.0)

    if is_int and not is_legal:
        values[2] = 0.5
        values[3] = 2**bits_int - 0.5
    elif not is_int and not is_legal:
        values[2] = -0.5
        values[3] = 0.5

    return values


def matrix_YCbCr(
    standard: str | Sequence[float] | np.ndarray = "ITU-R BT.709",
    *,
    bits: int = 8,
    is_legal: bool = False,
    is_int: bool = False,
) -> np.ndarray:
    """Return the YCbCr-to-RGB matrix for the given coding parameters."""

    K_r, K_b = _resolve_weights(standard)
    Y_min, Y_max, C_min, C_max = ranges_YCbCr(bits, is_legal, is_int)

    Y = np.array([K_r, 1.0 - K_r - K_b, K_b], dtype=np.float64)
    Cb = 0.5 * (np.array([0.0, 0.0, 1.0], dtype=np.float64) - Y) / (1.0 - K_b)
    Cr = 0.5 * (np.array([1.0, 0.0, 0.0], dtype=np.float64) - Y) / (1.0 - K_r)
    Y *= Y_max - Y_min
    Cb *= C_max - C_min
    Cr *= C_max - C_min
    return np.linalg.inv(np.vstack([Y, Cb, Cr]))


def offset_YCbCr(bits: int = 8, is_legal: bool = False, is_int: bool = False) -> np.ndarray:
    """Return the RGB-to-YCbCr offset for the given coding parameters."""

    Y_min, _Y_max, C_min, C_max = ranges_YCbCr(bits, is_legal, is_int)
    return np.array([Y_min, (C_min + C_max) / 2.0, (C_min + C_max) / 2.0], dtype=np.float64)


def RGB_to_YCbCr(
    RGB: Sequence[float] | np.ndarray,
    *,
    standard: str | Sequence[float] | np.ndarray = "ITU-R BT.709",
    in_bits: int = 10,
    in_legal: bool = False,
    in_int: bool = False,
    out_bits: int = 8,
    out_legal: bool = True,
    out_int: bool = False,
    clamp_int: bool = True,
    in_range: Sequence[float] | np.ndarray | None = None,
    out_range: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Convert non-linear R'G'B' values to YCbCr code values."""

    rgb = as_last_axis_triplets(RGB, name="RGB")
    K_r, K_b = _resolve_weights(standard)
    rgb_min, rgb_max = (
        _as_range(in_range, size=2, name="in_range")
        if in_range is not None
        else code_value_range(in_bits, in_legal, in_int)
    )
    Y_min, Y_max, C_min, C_max = (
        _as_range(out_range, size=4, name="out_range")
        if out_range is not None
        else ranges_YCbCr(out_bits, out_legal, out_int)
    )

    rgb_float = (rgb - rgb_min) / (rgb_max - rgb_min)
    R, G, B = np.moveaxis(rgb_float, -1, 0)
    Y = K_r * R + (1.0 - K_r - K_b) * G + K_b * B
    Cb = 0.5 * (B - Y) / (1.0 - K_b)
    Cr = 0.5 * (R - Y) / (1.0 - K_r)

    Y = Y * (Y_max - Y_min) + Y_min
    Cb = Cb * (C_max - C_min) + (C_max + C_min) / 2.0
    Cr = Cr * (C_max - C_min) + (C_max + C_min) / 2.0
    YCbCr = np.stack([Y, Cb, Cr], axis=-1)

    if out_int:
        if clamp_int:
            YCbCr = np.clip(YCbCr, 0.0, 2**_as_bits(out_bits) - 1.0)
        return round_BT2100(YCbCr).astype(np.int64)
    return np.asarray(YCbCr, dtype=np.float64)


def YCbCr_to_RGB(
    YCbCr: Sequence[float] | np.ndarray,
    *,
    standard: str | Sequence[float] | np.ndarray = "ITU-R BT.709",
    in_bits: int = 8,
    in_legal: bool = True,
    in_int: bool = False,
    out_bits: int = 10,
    out_legal: bool = False,
    out_int: bool = False,
    clamp_int: bool = True,
    in_range: Sequence[float] | np.ndarray | None = None,
    out_range: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Convert YCbCr code values to non-linear R'G'B' values."""

    ycbcr = as_last_axis_triplets(YCbCr, name="YCbCr")
    K_r, K_b = _resolve_weights(standard)
    Y_min, Y_max, C_min, C_max = (
        _as_range(in_range, size=4, name="in_range")
        if in_range is not None
        else ranges_YCbCr(in_bits, in_legal, in_int)
    )
    rgb_min, rgb_max = (
        _as_range(out_range, size=2, name="out_range")
        if out_range is not None
        else code_value_range(out_bits, out_legal, out_int)
    )

    Y, Cb, Cr = np.moveaxis(ycbcr, -1, 0)
    Y = (Y - Y_min) / (Y_max - Y_min)
    Cb = (Cb - (C_max + C_min) / 2.0) / (C_max - C_min)
    Cr = (Cr - (C_max + C_min) / 2.0) / (C_max - C_min)

    R = Y + (2.0 - 2.0 * K_r) * Cr
    B = Y + (2.0 - 2.0 * K_b) * Cb
    G = (Y - K_r * R - K_b * B) / (1.0 - K_r - K_b)
    RGB = np.stack([R, G, B], axis=-1)
    RGB = RGB * (rgb_max - rgb_min) + rgb_min

    if out_int:
        if clamp_int:
            RGB = np.clip(RGB, 0.0, 2**_as_bits(out_bits) - 1.0)
        return round_BT2100(RGB).astype(np.int64)
    return np.asarray(RGB, dtype=np.float64)


__all__ = [
    "WEIGHTS_YCBCR",
    "round_BT2100",
    "code_value_range",
    "ranges_YCbCr",
    "matrix_YCbCr",
    "offset_YCbCr",
    "RGB_to_YCbCr",
    "YCbCr_to_RGB",
]
