"""CIE xyY colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.colorimetry.chromaticity import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ

from .node import ColorSpaceNode


def xyY_to_xy(xyY: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return only the CIE xy chromaticity coordinates from xyY values."""
    xyy = np.asarray(xyY, dtype=np.float64)
    if xyy.shape == () or xyy.shape[-1] != 3:
        raise ValueError("xyY must have 3 values on the last axis")
    return np.array(xyy[..., :2], copy=True)


SPACE_NODES = (
    ColorSpaceNode(
        name="xyY",
        aliases=("xyy", "ciexyy", "cie xyY"),
        to_XYZ=xyY_to_XYZ,
        from_XYZ=XYZ_to_xyY,
        family="xyY",
    ),
)


__all__ = [
    "XYZ_to_xyY",
    "xyY_to_XYZ",
    "XYZ_to_xy",
    "xyY_to_xy",
    "SPACE_NODES",
]
