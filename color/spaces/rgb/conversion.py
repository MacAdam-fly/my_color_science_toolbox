"""RGB and XYZ conversion helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.adaptation import chromatic_adaptation_XYZ

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


def _white_xy_to_XYZ(white_xy: np.ndarray) -> np.ndarray:
    """Return a Y=100 XYZ whitepoint from xy chromaticity coordinates."""
    x, y = np.asarray(white_xy, dtype=np.float64)
    if y <= 0:
        raise ValueError("RGB colour-space whitepoint y must be positive")
    return np.array([100.0 * x / y, 100.0, 100.0 * (1.0 - x - y) / y], dtype=np.float64)


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


def RGB_to_RGB(
    RGB: Sequence[float] | np.ndarray,
    source: str | RGBColorSpace,
    target: str | RGBColorSpace,
    *,
    apply_decoding: bool = True,
    apply_encoding: bool = True,
    chromatic_adaptation: str | None = None,
) -> np.ndarray:
    """Convert RGB values from one RGB colour space to another.

    By default, this is a stimulus-matching conversion through XYZ. If
    *chromatic_adaptation* is provided, source-white XYZ values are adapted to
    the target RGB colour-space white before encoding into the target space.
    """
    source_space = get_RGB_colourspace(source)
    target_space = get_RGB_colourspace(target)

    XYZ = RGB_to_XYZ(
        RGB,
        colourspace=source_space,
        apply_decoding=apply_decoding,
    )
    if chromatic_adaptation is not None:
        XYZ = chromatic_adaptation_XYZ(
            XYZ,
            source_white_XYZ=_white_xy_to_XYZ(source_space.white_xy),
            target_white_XYZ=_white_xy_to_XYZ(target_space.white_xy),
            transform=chromatic_adaptation,
        )

    return XYZ_to_RGB(
        XYZ,
        colourspace=target_space,
        apply_encoding=apply_encoding,
    )


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
    "RGB_to_RGB",
    "sRGB_to_XYZ",
    "XYZ_to_sRGB",
]
