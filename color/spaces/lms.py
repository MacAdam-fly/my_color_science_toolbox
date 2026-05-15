"""LMS helpers backed by the existing implementation."""

from __future__ import annotations

import numpy as np

from ..core.context import ColorContext
from ..core.types import ArrayLike
from ..utils.color_conversion import LMS2006Converter
from .registry import SpaceDefinition, register_space


def lms_to_xyz(
    lms: ArrayLike, fov: int = 10, context: ColorContext = None
) -> np.ndarray:
    if context is not None and context.fov is not None and fov is None:
        fov = context.fov
    return LMS2006Converter(fov=fov).lms_to_xyz(np.asarray(lms, dtype=float))


def xyz_to_lms(
    xyz: ArrayLike, fov: int = 10, context: ColorContext = None
) -> np.ndarray:
    if context is not None and context.fov is not None and fov is None:
        fov = context.fov
    return LMS2006Converter(fov=fov).xyz_to_lms(np.asarray(xyz, dtype=float))


register_space(
    SpaceDefinition(
        name="lms",
        to_xyz=lms_to_xyz,
        from_xyz=xyz_to_lms,
    )
)
