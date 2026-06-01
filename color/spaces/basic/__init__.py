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
from .ipt import (
    IPT_hue_angle,
    IPT_to_XYZ,
    SPACE_NODES as IPT_SPACE_NODES,
    XYZ_to_IPT,
)
from .jzazbz import (
    JzCzhz_to_Jzazbz,
    Jzazbz_to_JzCzhz,
    Jzazbz_to_XYZ,
    SPACE_NODES as JZAZBZ_SPACE_NODES,
    XYZ_to_Jzazbz,
)
from .luv import (
    LCHuv_to_Luv,
    Lshuv_to_Luv,
    Luv_to_LCHuv,
    Luv_to_Lshuv,
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
    *IPT_SPACE_NODES,
    *JZAZBZ_SPACE_NODES,
)

__all__ = [
    "DEFAULT_WHITEPOINT_XYZ",  # default D65 reference whitepoint for Lab and Luv
    "EPSILON",  # CIE 1976 epsilon threshold
    "KAPPA",  # CIE 1976 kappa slope
]

__all__ += [
    "XYZ_to_xyY",  # convert XYZ values to xyY coordinates
    "xyY_to_XYZ",  # convert xyY coordinates to XYZ values
    "XYZ_to_xy",  # project XYZ values to xy chromaticity coordinates
    "xyY_to_xy",  # project xyY values to xy chromaticity coordinates
    "xy_to_uv1960",  # convert xy chromaticity coordinates to CIE 1960 uv
    "XYZ_to_uv1960",  # project XYZ values to CIE 1960 uv
    "uv1960_to_xy",  # convert CIE 1960 uv coordinates to xy
    "xy_to_upvp1976",  # convert xy chromaticity coordinates to CIE 1976 u'v'
    "XYZ_to_upvp1976",  # project XYZ values to CIE 1976 u'v'
    "upvp1976_to_xy",  # convert CIE 1976 u'v' coordinates to xy
]

__all__ += [
    "XYZ_to_Lab",  # convert XYZ values to CIE Lab
    "Lab_to_XYZ",  # convert CIE Lab values to XYZ
    "Lab_to_LCHab",  # convert CIE Lab values to LCHab
    "LCHab_to_Lab",  # convert LCHab values to CIE Lab
    "XYZ_to_Luv",  # convert XYZ values to CIE Luv
    "Luv_to_XYZ",  # convert CIE Luv values to XYZ
    "Luv_to_LCHuv",  # convert CIE Luv values to LCHuv
    "LCHuv_to_Luv",  # convert LCHuv values to CIE Luv
    "Luv_to_Lshuv",  # convert CIE Luv values to Lshuv
    "Lshuv_to_Luv",  # convert Lshuv values to CIE Luv
    "XYZ_to_UVW",  # convert XYZ values to CIE 1964 UVW
    "UVW_to_XYZ",  # convert CIE 1964 UVW values to XYZ
]

__all__ += [
    "XYZ_to_Oklab",  # convert D65-referred XYZ values to Oklab
    "Oklab_to_XYZ",  # convert Oklab values to D65-referred XYZ
    "Oklab_to_Oklch",  # convert Oklab values to Oklch
    "Oklch_to_Oklab",  # convert Oklch values to Oklab
    "XYZ_to_IPT",  # convert D65-referred XYZ values to IPT
    "IPT_to_XYZ",  # convert IPT values to D65-referred XYZ
    "IPT_hue_angle",  # compute IPT hue angle in degrees
    "XYZ_to_Jzazbz",  # convert D65-referred XYZ values to Jzazbz
    "Jzazbz_to_XYZ",  # convert Jzazbz values to D65-referred XYZ
    "Jzazbz_to_JzCzhz",  # convert Jzazbz values to cylindrical JzCzhz
    "JzCzhz_to_Jzazbz",  # convert cylindrical JzCzhz values to Jzazbz
]

__all__ += [
    "SPACE_NODES",  # colour-space registry nodes defined by basic spaces
]
