"""CAM02 appearance space adapters using context parameters."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ..core.context import ColorContext
from ..core.types import ArrayLike
from ..utils.CAM02 import Cam02
from .registry import SpaceDefinition, register_space
from .validation import require_any
from .xyz import xyz_to_xyy


def _resolve_white_xyy(context: ColorContext) -> Optional[np.ndarray]:
    if context.white_point_xyy is not None:
        return np.asarray(context.white_point_xyy, dtype=float)
    if context.white_point is not None:
        return xyz_to_xyy(context.white_point)
    return None


def _resolve_background_xyy(context: ColorContext) -> Optional[np.ndarray]:
    if context.background_xyy is not None:
        return np.asarray(context.background_xyy, dtype=float)
    if context.background_xyz is not None:
        return xyz_to_xyy(context.background_xyz)
    return None


def xyz_to_cam02(xyz: ArrayLike, context: Optional[ColorContext] = None) -> np.ndarray:
    if context is None:
        context = ColorContext()
    require_any(context, ("white_point", "white_point_xyy"), "cam02", "white_point")
    require_any(context, ("background_xyz", "background_xyy"), "cam02", "background")
    if context.adapting_luminance is None:
        raise ValueError("Missing adapting_luminance for cam02")

    white_xyy = _resolve_white_xyy(context)
    background_xyy = _resolve_background_xyy(context)
    if white_xyy is None or background_xyy is None:
        raise ValueError("Missing white_point or background for cam02")

    ref_white = context.reference_white_xyy
    xyY = xyz_to_xyy(np.asarray(xyz, dtype=float))
    cam = Cam02(
        context.adapting_luminance,
        xyY,
        white_xyy,
        background_xyy,
        xyY_wr=ref_white,
        surround=context.surround,
    )
    result = cam.cal()
    return np.array([result["Q"], result["M"], result["h"]], dtype=float)


def cam02_to_xyz(qmh: ArrayLike, context: Optional[ColorContext] = None) -> np.ndarray:
    if context is None:
        context = ColorContext()
    require_any(context, ("white_point", "white_point_xyy"), "cam02", "white_point")
    require_any(context, ("background_xyz", "background_xyy"), "cam02", "background")
    if context.adapting_luminance is None:
        raise ValueError("Missing adapting_luminance for cam02")

    white_xyy = _resolve_white_xyy(context)
    background_xyy = _resolve_background_xyy(context)
    if white_xyy is None or background_xyy is None:
        raise ValueError("Missing white_point or background for cam02")

    ref_white = context.reference_white_xyy
    sample_xyy = white_xyy
    cam = Cam02(
        context.adapting_luminance,
        sample_xyy,
        white_xyy,
        background_xyy,
        xyY_wr=ref_white,
        surround=context.surround,
    )
    return cam.inverse_cal(np.asarray(qmh, dtype=float))


register_space(
    SpaceDefinition(
        name="cam02",
        to_xyz=cam02_to_xyz,
        from_xyz=xyz_to_cam02,
        aliases=("ciecam02",),
        required_context=("adapting_luminance",),
    )
)
