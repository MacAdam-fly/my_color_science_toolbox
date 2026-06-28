"""RGB display and imaging standard constants.

The authoritative constants live in :mod:`color.constants.display_standards`.
This module re-exports them for RGB-module locality.
"""

from __future__ import annotations

from color.constants.display_standards import (
    ADOBE_RGB_TO_XYZ,
    COMMON_GAMUTS,
    DCIP3_TO_XYZ,
    DISPLAY_P3_TO_XYZ,
    NTSC_1953_TO_XYZ,
    PROPHOTO_RGB_TO_XYZ,
    REC2020_TO_XYZ,
    REC709_TO_XYZ,
    RGB_COLOURSPACE_DEFINITIONS,
    RGB_GAMUT_METADATA,
    SRGB_TO_XYZ,
    XYZ_TO_ADOBE_RGB,
    XYZ_TO_DCIP3,
    XYZ_TO_DISPLAY_P3,
    XYZ_TO_NTSC_1953,
    XYZ_TO_PROPHOTO_RGB,
    XYZ_TO_REC2020,
    XYZ_TO_REC709,
    XYZ_TO_SRGB,
)

__all__ = [
    "SRGB_TO_XYZ",
    "XYZ_TO_SRGB",
    "REC709_TO_XYZ",
    "XYZ_TO_REC709",
    "REC2020_TO_XYZ",
    "XYZ_TO_REC2020",
    "ADOBE_RGB_TO_XYZ",
    "XYZ_TO_ADOBE_RGB",
    "PROPHOTO_RGB_TO_XYZ",
    "XYZ_TO_PROPHOTO_RGB",
    "DISPLAY_P3_TO_XYZ",
    "XYZ_TO_DISPLAY_P3",
    "DCIP3_TO_XYZ",
    "XYZ_TO_DCIP3",
    "NTSC_1953_TO_XYZ",
    "XYZ_TO_NTSC_1953",
    "RGB_COLOURSPACE_DEFINITIONS",
    "RGB_GAMUT_METADATA",
    "COMMON_GAMUTS",
]
