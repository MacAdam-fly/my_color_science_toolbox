"""RGB and XYZ conversion helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .colourspace import RGBColorSpace
from .registry import get_RGB_colourspace
from .transfer import decode_transfer, encode_transfer


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def RGB_to_XYZ(
    RGB: Sequence[float] | np.ndarray,
    *,
    colourspace: str | RGBColorSpace = "sRGB",
    apply_decoding: bool = True,
) -> np.ndarray:
    """Convert RGB values to CIE XYZ tristimulus values."""
    rgb_space = get_RGB_colourspace(colourspace)
    rgb = _as_last_axis_triplets(RGB, name="RGB")
    linear = decode_transfer(rgb, rgb_space.transfer) if apply_decoding else rgb
    return linear @ rgb_space.matrix_RGB_to_XYZ.T


def XYZ_to_RGB(
    XYZ: Sequence[float] | np.ndarray,
    *,
    colourspace: str | RGBColorSpace = "sRGB",
    apply_encoding: bool = True,
) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to RGB values."""
    rgb_space = get_RGB_colourspace(colourspace)
    xyz = _as_last_axis_triplets(XYZ, name="XYZ")
    linear = xyz @ rgb_space.matrix_XYZ_to_RGB.T
    return encode_transfer(linear, rgb_space.transfer) if apply_encoding else linear


def sRGB_to_XYZ(
    RGB: Sequence[float] | np.ndarray,
    *,
    apply_decoding: bool = True,
) -> np.ndarray:
    """Convert sRGB values to CIE XYZ tristimulus values."""
    return RGB_to_XYZ(RGB, colourspace="sRGB", apply_decoding=apply_decoding)


def XYZ_to_sRGB(
    XYZ: Sequence[float] | np.ndarray,
    *,
    apply_encoding: bool = True,
) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to sRGB values."""
    return XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=apply_encoding)


__all__ = [
    "RGB_to_XYZ",
    "XYZ_to_RGB",
    "sRGB_to_XYZ",
    "XYZ_to_sRGB",
]
