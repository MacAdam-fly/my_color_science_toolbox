"""Shared constants for color calculations."""

from .display_matrices import (
    ADOBE_RGB_TO_XYZ,
    COMMON_GAMUTS,
    DCIP3_TO_XYZ,
    DISPLAY_P3_TO_XYZ,
    NTSC_1953_TO_XYZ,
    REC2020_TO_XYZ,
    REC709_TO_XYZ,
    RGB_COLOURSPACE_DEFINITIONS,
    RGB_GAMUT_METADATA,
    SRGB_TO_XYZ,
    XYZ_TO_ADOBE_RGB,
    XYZ_TO_DCIP3,
    XYZ_TO_DISPLAY_P3,
    XYZ_TO_NTSC_1953,
    XYZ_TO_REC2020,
    XYZ_TO_REC709,
    XYZ_TO_SRGB,
)
from .illuminants import D50_XYZ, D55_XYZ, D65_XYZ, E_XYZ
from .standard_observer_matrices import (
    LMS_2_DEGREE_TO_XYZ_2_DEGREE,
    LMS_10_DEGREE_TO_XYZ_10_DEGREE,
    XYZ_2_DEGREE_TO_LMS_2_DEGREE,
    XYZ_10_DEGREE_TO_LMS_10_DEGREE,
)

__all__ = [
    "D50_XYZ",  # CIE D50 whitepoint tristimulus values
    "D55_XYZ",  # CIE D55 whitepoint tristimulus values
    "D65_XYZ",  # CIE D65 whitepoint tristimulus values
    "E_XYZ",  # equal-energy whitepoint tristimulus values
    "SRGB_TO_XYZ",  # linear sRGB to XYZ conversion matrix
    "XYZ_TO_SRGB",  # XYZ to linear sRGB conversion matrix
    "REC709_TO_XYZ",  # linear Rec.709 to XYZ conversion matrix
    "XYZ_TO_REC709",  # XYZ to linear Rec.709 conversion matrix
    "REC2020_TO_XYZ",  # linear Rec.2020 to XYZ conversion matrix
    "XYZ_TO_REC2020",  # XYZ to linear Rec.2020 conversion matrix
    "ADOBE_RGB_TO_XYZ",  # linear Adobe RGB (1998) to XYZ conversion matrix
    "XYZ_TO_ADOBE_RGB",  # XYZ to linear Adobe RGB (1998) conversion matrix
    "DISPLAY_P3_TO_XYZ",  # linear Display P3 to XYZ conversion matrix
    "XYZ_TO_DISPLAY_P3",  # XYZ to linear Display P3 conversion matrix
    "DCIP3_TO_XYZ",  # linear DCI-P3 to XYZ conversion matrix
    "XYZ_TO_DCIP3",  # XYZ to linear DCI-P3 conversion matrix
    "NTSC_1953_TO_XYZ",  # linear NTSC (1953) to XYZ conversion matrix
    "XYZ_TO_NTSC_1953",  # XYZ to linear NTSC (1953) conversion matrix
    "RGB_COLOURSPACE_DEFINITIONS",  # RGB colour-space standard definitions
    "RGB_GAMUT_METADATA",  # backwards-compatible RGB definitions alias
    "COMMON_GAMUTS",  # backwards-compatible RGB matrix registry
    "LMS_2_DEGREE_TO_XYZ_2_DEGREE",  # CIE 2006 2-degree LMS to XYZ matrix
    "XYZ_2_DEGREE_TO_LMS_2_DEGREE",  # CIE 2006 2-degree XYZ to LMS matrix
    "LMS_10_DEGREE_TO_XYZ_10_DEGREE",  # CIE 2006 10-degree LMS to XYZ matrix
    "XYZ_10_DEGREE_TO_LMS_10_DEGREE",  # CIE 2006 10-degree XYZ to LMS matrix
]
