"""CIE 1964 U*V*W* colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.colorimetry.chromaticity import (
    XYZ_to_xy,
    uv1960_to_xy,
    xyY_to_XYZ,
    xy_to_uv1960,
)
from color.constants import D65_XYZ
from color.utils.arrays import as_last_axis_pairs, as_last_axis_triplets

from ..node import ColorSpaceNode


def _resolve_whitepoint_xy(
    whitepoint_XYZ: Sequence[float] | np.ndarray | None,
    whitepoint_xy: Sequence[float] | np.ndarray | None,
) -> np.ndarray:
    """Resolve a UVW reference whitepoint as CIE xy coordinates."""
    if whitepoint_XYZ is not None and whitepoint_xy is not None:
        raise ValueError("whitepoint_XYZ and whitepoint_xy cannot both be provided")
    if whitepoint_xy is not None:
        return as_last_axis_pairs(whitepoint_xy, name="whitepoint_xy")

    whitepoint = D65_XYZ if whitepoint_XYZ is None else whitepoint_XYZ
    return XYZ_to_xy(as_last_axis_triplets(whitepoint, name="whitepoint_XYZ"))


def XYZ_to_UVW(
    XYZ: Sequence[float] | np.ndarray,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray | None = None,
    whitepoint_xy: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to CIE 1964 U*V*W* coordinates."""
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    xy_n = _resolve_whitepoint_xy(whitepoint_XYZ, whitepoint_xy)

    uv = xy_to_uv1960(XYZ_to_xy(xyz))
    uv_n = xy_to_uv1960(xy_n)
    W = 25.0 * np.cbrt(xyz[..., 1]) - 17.0
    U = 13.0 * W * (uv[..., 0] - uv_n[..., 0])
    V = 13.0 * W * (uv[..., 1] - uv_n[..., 1])
    return np.stack([U, V, W], axis=-1)


def UVW_to_XYZ(
    UVW: Sequence[float] | np.ndarray,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray | None = None,
    whitepoint_xy: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Convert CIE 1964 U*V*W* coordinates to CIE XYZ tristimulus values."""
    uvw = as_last_axis_triplets(UVW, name="UVW")
    xy_n = _resolve_whitepoint_xy(whitepoint_XYZ, whitepoint_xy)
    uv_n = xy_to_uv1960(xy_n)

    U = uvw[..., 0]
    V = uvw[..., 1]
    W = uvw[..., 2]
    Y = ((W + 17.0) / 25.0) ** 3

    u = np.broadcast_to(uv_n[..., 0], W.shape).astype(np.float64, copy=True)
    v = np.broadcast_to(uv_n[..., 1], W.shape).astype(np.float64, copy=True)
    nonzero_W = W != 0
    np.divide(U, 13.0 * W, out=u, where=nonzero_W)
    np.divide(V, 13.0 * W, out=v, where=nonzero_W)
    u += np.where(nonzero_W, uv_n[..., 0], 0.0)
    v += np.where(nonzero_W, uv_n[..., 1], 0.0)

    xy = uv1960_to_xy(np.stack([u, v], axis=-1))
    return xyY_to_XYZ(np.concatenate([xy, Y[..., np.newaxis]], axis=-1))


SPACE_NODES = (
    ColorSpaceNode(
        name="UVW",
        aliases=("CIE UVW", "CIE 1964 UVW", "CIEUVW"),
        to_XYZ=UVW_to_XYZ,
        from_XYZ=XYZ_to_UVW,
        family="UVW",
    ),
)


__all__ = [
    "XYZ_to_UVW",
    "UVW_to_XYZ",
    "SPACE_NODES",
]
