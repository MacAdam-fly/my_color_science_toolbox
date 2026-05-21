"""Basic colour spaces that do not depend on appearance models."""

from __future__ import annotations

from .lab import (
    DEFAULT_WHITEPOINT_XYZ,
    EPSILON,
    KAPPA,
    Lab_to_LCHab,
    Lab_to_XYZ,
    LCHab_to_Lab,
    SPACE_NODES as LAB_SPACE_NODES,
    XYZ_to_Lab,
)
from .luv import (
    LCHuv_to_Luv,
    Luv_to_LCHuv,
    Luv_to_XYZ,
    SPACE_NODES as LUV_SPACE_NODES,
    XYZ_to_Luv,
)
from .oklab import (
    Oklab_to_Oklch,
    Oklab_to_XYZ,
    Oklch_to_Oklab,
    SPACE_NODES as OKLAB_SPACE_NODES,
    XYZ_to_Oklab,
)
from .uvw import SPACE_NODES as UVW_SPACE_NODES, UVW_to_XYZ, XYZ_to_UVW
from .xyy import (
    SPACE_NODES as XYY_SPACE_NODES,
    XYZ_to_upvp1976,
    XYZ_to_uv1960,
    XYZ_to_xy,
    XYZ_to_xyY,
    upvp1976_to_xy,
    uv1960_to_xy,
    xyY_to_XYZ,
    xyY_to_xy,
    xy_to_upvp1976,
    xy_to_uv1960,
)

SPACE_NODES = (
    *XYY_SPACE_NODES,
    *LAB_SPACE_NODES,
    *LUV_SPACE_NODES,
    *UVW_SPACE_NODES,
    *OKLAB_SPACE_NODES,
)

__all__ = [
    "DEFAULT_WHITEPOINT_XYZ",
    "EPSILON",
    "KAPPA",
    "XYZ_to_xyY",
    "xyY_to_XYZ",
    "XYZ_to_xy",
    "xyY_to_xy",
    "xy_to_uv1960",
    "XYZ_to_uv1960",
    "uv1960_to_xy",
    "xy_to_upvp1976",
    "XYZ_to_upvp1976",
    "upvp1976_to_xy",
    "XYZ_to_Lab",
    "Lab_to_XYZ",
    "Lab_to_LCHab",
    "LCHab_to_Lab",
    "XYZ_to_Luv",
    "Luv_to_XYZ",
    "Luv_to_LCHuv",
    "LCHuv_to_Luv",
    "XYZ_to_UVW",
    "UVW_to_XYZ",
    "XYZ_to_Oklab",
    "Oklab_to_XYZ",
    "Oklab_to_Oklch",
    "Oklch_to_Oklab",
    "SPACE_NODES",
]
