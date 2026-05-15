"""CIE L*u*v* helpers backed by the existing implementation."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ..constants.illuminants import D65_XYZ
from ..core.context import ColorContext
from ..core.types import ArrayLike
from ..utils.color_conversion import LuvColorConverter
from .registry import SpaceDefinition, register_space


def _resolve_white_point(
    white_point: Optional[ArrayLike], context: Optional[ColorContext]
) -> ArrayLike:
    if white_point is not None:
        return white_point
    if context is not None and context.white_point is not None:
        return context.white_point
    return D65_XYZ


def _converter(
    white_point: Optional[ArrayLike] = None, context: Optional[ColorContext] = None
) -> LuvColorConverter:
    resolved_white = _resolve_white_point(white_point, context)
    return LuvColorConverter(reference_white=resolved_white)


def xyz_to_luv(
    xyz: ArrayLike,
    white_point: Optional[ArrayLike] = None,
    context: Optional[ColorContext] = None,
) -> np.ndarray:
    return _converter(white_point, context).XYZ_to_luv(xyz)


def luv_to_xyz(
    luv: ArrayLike,
    white_point: Optional[ArrayLike] = None,
    context: Optional[ColorContext] = None,
) -> np.ndarray:
    return _converter(white_point, context).luv_to_XYZ(luv)


def luv_to_lch_uv(luv: ArrayLike) -> np.ndarray:
    return LuvColorConverter.luv_to_lch(luv)


def lch_uv_to_luv(lch: ArrayLike) -> np.ndarray:
    return LuvColorConverter.lch_to_luv(lch)


register_space(
    SpaceDefinition(
        name="luv",
        to_xyz=luv_to_xyz,
        from_xyz=xyz_to_luv,
        aliases=("cie_luv",),
    )
)
