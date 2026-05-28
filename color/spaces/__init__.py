"""Colour-space conversion helpers."""

from __future__ import annotations

from .appearance import (
    CAM02LCD_to_JMh_CIECAM02,
    CAM02LCD_to_XYZ,
    CAM02SCD_to_JMh_CIECAM02,
    CAM02SCD_to_XYZ,
    CAM02UCS_to_JMh_CIECAM02,
    CAM02UCS_to_XYZ,
    COEFFICIENTS_UCS_LUO2006,
    JMh_CIECAM02_to_CAM02LCD,
    JMh_CIECAM02_to_CAM02SCD,
    JMh_CIECAM02_to_CAM02UCS,
    CAM16LCD_to_JMh_CIECAM16,
    CAM16LCD_to_XYZ,
    CAM16SCD_to_JMh_CIECAM16,
    CAM16SCD_to_XYZ,
    CAM16UCS_to_JMh_CIECAM16,
    CAM16UCS_to_XYZ,
    COEFFICIENTS_UCS_LI2017,
    JMh_CIECAM16_to_CAM16LCD,
    JMh_CIECAM16_to_CAM16SCD,
    JMh_CIECAM16_to_CAM16UCS,
    Coefficients_UCS_Luo2006,
    XYZ_to_CAM02LCD,
    XYZ_to_CAM02SCD,
    XYZ_to_CAM02UCS,
    XYZ_to_CAM16LCD,
    XYZ_to_CAM16SCD,
    XYZ_to_CAM16UCS,
)
from .basic import (
    DEFAULT_WHITEPOINT_XYZ,
    EPSILON,
    KAPPA,
    IPT_hue_angle,
    IPT_to_XYZ,
    JzCzhz_to_Jzazbz,
    Jzazbz_to_JzCzhz,
    Jzazbz_to_XYZ,
    Lab_to_LCHab,
    Lab_to_XYZ,
    LCHab_to_Lab,
    LCHuv_to_Luv,
    Lshuv_to_Luv,
    Luv_to_LCHuv,
    Luv_to_Lshuv,
    Luv_to_XYZ,
    Oklab_to_Oklch,
    Oklab_to_XYZ,
    Oklch_to_Oklab,
    UVW_to_XYZ,
    XYZ_to_Lab,
    XYZ_to_Luv,
    XYZ_to_Oklab,
    XYZ_to_UVW,
    XYZ_to_IPT,
    XYZ_to_Jzazbz,
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
from .conversion import convert_color
from .conversion import (
    ConversionPath,
    ConversionPathEdge,
    ConversionPathNode,
    describe_conversion_path,
)
from .plotting import plot_conversion_graph, plot_conversion_path
from .registry import (
    ColorSpaceNode,
    SPACE_REGISTRY,
    get_colourspace_node,
    list_colourspace_nodes,
)
from .rgb import (
    RGBColorSpace,
    RGB_COLORSPACES,
    RGB_COLOURSPACE_DEFINITIONS,
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    XYZ_to_sRGB,
    get_RGB_colourspace,
    list_RGB_colourspaces,
    sRGB_to_XYZ,
)
from .spec import SpaceSpec

# Generic colour-space graph.
__all__ = [
    "ColorSpaceNode",  # colour-space conversion graph node
    "SPACE_REGISTRY",  # registered generic colour-space nodes
    "get_colourspace_node",  # resolve a generic colour-space node by name or alias
    "list_colourspace_nodes",  # list registered generic colour-space nodes
    "SpaceSpec",  # colour-space instance with endpoint parameters
    "convert_color",  # convert between registered colour-space nodes
    "ConversionPathNode",  # described colour-space conversion path node
    "ConversionPathEdge",  # described colour-space conversion path edge
    "ConversionPath",  # described colour-space conversion route
    "describe_conversion_path",  # describe the route convert_color would use
    "plot_conversion_path",  # plot a described colour-space conversion route
    "plot_conversion_graph",  # plot the registered colour-space conversion graph
]

# Reference whitepoint and CIE 1976 constants.
__all__ += [
    "DEFAULT_WHITEPOINT_XYZ",  # default D65 reference whitepoint for Lab and Luv
    "EPSILON",  # CIE 1976 epsilon threshold
    "KAPPA",  # CIE 1976 kappa slope
]

# RGB colour spaces.
__all__ += [
    "RGBColorSpace",  # RGB colour-space definition object
    "RGB_COLOURSPACE_DEFINITIONS",  # RGB colour-space standard definitions
    "RGB_COLORSPACES",  # registered RGB colour spaces
    "get_RGB_colourspace",  # resolve an RGB colour space by name or alias
    "list_RGB_colourspaces",  # list registered RGB colour-space names
    "RGB_to_XYZ",  # convert RGB values to XYZ
    "XYZ_to_RGB",  # convert XYZ values to RGB
    "RGB_to_RGB",  # convert between RGB colour spaces
    "sRGB_to_XYZ",  # convert sRGB values to XYZ
    "XYZ_to_sRGB",  # convert XYZ values to sRGB
]

# CIE xyY colour space and xy chromaticity projection.
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

# Perceptual colour spaces and cylindrical derivatives.
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
    "XYZ_to_Oklab",  # convert XYZ values to Oklab
    "Oklab_to_XYZ",  # convert Oklab values to XYZ
    "Oklab_to_Oklch",  # convert Oklab values to Oklch
    "Oklch_to_Oklab",  # convert Oklch values to Oklab
    "XYZ_to_IPT",  # convert XYZ values to IPT
    "IPT_to_XYZ",  # convert IPT values to XYZ
    "IPT_hue_angle",  # compute IPT hue angle in degrees
    "XYZ_to_Jzazbz",  # convert XYZ values to Jzazbz
    "Jzazbz_to_XYZ",  # convert Jzazbz values to XYZ
    "Jzazbz_to_JzCzhz",  # convert Jzazbz values to cylindrical JzCzhz
    "JzCzhz_to_Jzazbz",  # convert cylindrical JzCzhz values to Jzazbz
]

# CAM02 uniform colour spaces.
__all__ += [
    "Coefficients_UCS_Luo2006",  # Luo et al. 2006 CAM02 uniform-space coefficients
    "COEFFICIENTS_UCS_LUO2006",  # registered CAM02-UCS / LCD / SCD coefficient presets
    "JMh_CIECAM02_to_CAM02UCS",  # convert CIECAM02 JMh correlates to CAM02-UCS
    "CAM02UCS_to_JMh_CIECAM02",  # convert CAM02-UCS coordinates to CIECAM02 JMh
    "JMh_CIECAM02_to_CAM02LCD",  # convert CIECAM02 JMh correlates to CAM02-LCD
    "CAM02LCD_to_JMh_CIECAM02",  # convert CAM02-LCD coordinates to CIECAM02 JMh
    "JMh_CIECAM02_to_CAM02SCD",  # convert CIECAM02 JMh correlates to CAM02-SCD
    "CAM02SCD_to_JMh_CIECAM02",  # convert CAM02-SCD coordinates to CIECAM02 JMh
    "XYZ_to_CAM02UCS",  # convert XYZ values to CAM02-UCS
    "CAM02UCS_to_XYZ",  # convert CAM02-UCS values to XYZ
    "XYZ_to_CAM02LCD",  # convert XYZ values to CAM02-LCD
    "CAM02LCD_to_XYZ",  # convert CAM02-LCD values to XYZ
    "XYZ_to_CAM02SCD",  # convert XYZ values to CAM02-SCD
    "CAM02SCD_to_XYZ",  # convert CAM02-SCD values to XYZ
]

# CAM16 uniform colour spaces.
__all__ += [
    "COEFFICIENTS_UCS_LI2017",  # registered CAM16-UCS / LCD / SCD coefficient presets
    "JMh_CIECAM16_to_CAM16UCS",  # convert CIECAM16 JMh correlates to CAM16-UCS
    "CAM16UCS_to_JMh_CIECAM16",  # convert CAM16-UCS coordinates to CIECAM16 JMh
    "JMh_CIECAM16_to_CAM16LCD",  # convert CIECAM16 JMh correlates to CAM16-LCD
    "CAM16LCD_to_JMh_CIECAM16",  # convert CAM16-LCD coordinates to CIECAM16 JMh
    "JMh_CIECAM16_to_CAM16SCD",  # convert CIECAM16 JMh correlates to CAM16-SCD
    "CAM16SCD_to_JMh_CIECAM16",  # convert CAM16-SCD coordinates to CIECAM16 JMh
    "XYZ_to_CAM16UCS",  # convert XYZ values to CAM16-UCS
    "CAM16UCS_to_XYZ",  # convert CAM16-UCS values to XYZ
    "XYZ_to_CAM16LCD",  # convert XYZ values to CAM16-LCD
    "CAM16LCD_to_XYZ",  # convert CAM16-LCD values to XYZ
    "XYZ_to_CAM16SCD",  # convert XYZ values to CAM16-SCD
    "CAM16SCD_to_XYZ",  # convert CAM16-SCD values to XYZ
]
