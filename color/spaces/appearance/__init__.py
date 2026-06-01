"""Uniform colour spaces built on colour appearance models."""

from __future__ import annotations

from ._cam_ucs import Coefficients_UCS_Luo2006
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
    SPACE_NODES as CAM02_SPACE_NODES,
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
    SPACE_NODES as CAM16_SPACE_NODES,
    XYZ_to_CAM16LCD,
    XYZ_to_CAM16SCD,
    XYZ_to_CAM16UCS,
)

SPACE_NODES = (*CAM02_SPACE_NODES, *CAM16_SPACE_NODES)

__all__ = [
    "Coefficients_UCS_Luo2006",  # coefficient container for CAM uniform spaces
    "COEFFICIENTS_UCS_LUO2006",  # CAM02-UCS / LCD / SCD coefficient presets
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

__all__ += [
    "COEFFICIENTS_UCS_LI2017",  # CAM16-UCS / LCD / SCD coefficient presets
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

__all__ += [
    "SPACE_NODES",  # colour-space registry nodes defined by appearance spaces
]
