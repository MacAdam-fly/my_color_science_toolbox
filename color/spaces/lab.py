"""CIE Lab helpers backed by the existing implementation."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ..constants.illuminants import D65_XYZ
from ..core.context import ColorContext
from ..core.types import ArrayLike
from ..utils.color_conversion import LabColorConverter
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
) -> LabColorConverter:
    resolved_white = _resolve_white_point(white_point, context)
    return LabColorConverter(reference_white=resolved_white)


def xyz_to_lab(
    xyz: ArrayLike,
    white_point: Optional[ArrayLike] = None,
    context: Optional[ColorContext] = None,
) -> np.ndarray:
    return _converter(white_point, context).XYZ_to_lab(xyz)


def lab_to_xyz(
    lab: ArrayLike,
    white_point: Optional[ArrayLike] = None,
    context: Optional[ColorContext] = None,
) -> np.ndarray:
    return _converter(white_point, context).lab_to_XYZ(lab)


def lab_to_lch(lab: ArrayLike) -> np.ndarray:
    return LabColorConverter.lab_to_lch(lab)


def lch_to_lab(lch: ArrayLike) -> np.ndarray:
    return LabColorConverter.lch_to_lab(lch)


register_space(
    SpaceDefinition(
        name="lab",
        to_xyz=lab_to_xyz,
        from_xyz=xyz_to_lab,
        aliases=("cie_lab",),
    )
)
