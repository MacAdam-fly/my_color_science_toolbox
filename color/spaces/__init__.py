"""Colour-space conversion helpers."""

from __future__ import annotations

from ._cam_ucs import (
    Coefficients_UCS_Luo2006,
)

from .cam02_ucs import (
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
    XYZ_to_CAM02LCD,
    XYZ_to_CAM02SCD,
    XYZ_to_CAM02UCS,
)
from .cam16_ucs import (
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
    XYZ_to_CAM16LCD,
    XYZ_to_CAM16SCD,
    XYZ_to_CAM16UCS,
)
from .conversion import convert_color
from .lab import (
    DEFAULT_WHITEPOINT_XYZ,
    KAPPA,
    EPSILON,
    Lab_to_LCHab,
    Lab_to_XYZ,
    LCHab_to_Lab,
    XYZ_to_Lab,
)
from .luv import LCHuv_to_Luv, Luv_to_LCHuv, Luv_to_XYZ, XYZ_to_Luv
from .oklab import Oklab_to_Oklch, Oklab_to_XYZ, Oklch_to_Oklab, XYZ_to_Oklab
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
from .xyy import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ, xyY_to_xy

# Generic colour-space graph.
__all__ = [
    "ColorSpaceNode",  # colour-space conversion graph node
    "SPACE_REGISTRY",  # registered generic colour-space nodes
    "get_colourspace_node",  # resolve a generic colour-space node by name or alias
    "list_colourspace_nodes",  # list registered generic colour-space nodes
    "SpaceSpec",  # colour-space instance with endpoint parameters
    "convert_color",  # convert between registered colour-space nodes
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
    "XYZ_to_Oklab",  # convert XYZ values to Oklab
    "Oklab_to_XYZ",  # convert Oklab values to XYZ
    "Oklab_to_Oklch",  # convert Oklab values to Oklch
    "Oklch_to_Oklab",  # convert Oklch values to Oklab
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
