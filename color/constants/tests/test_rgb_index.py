from __future__ import annotations

from color import constants
from color.constants import display_standards as constants_display_standards
from color.spaces.rgb import RGB_COLOURSPACE_DEFINITIONS
from color.spaces.rgb import display_standards as rgb_display_standards


def test_rgb_matrices_are_available_from_constants_top_level() -> None:
    assert constants.SRGB_TO_XYZ is constants_display_standards.SRGB_TO_XYZ
    assert constants.XYZ_TO_SRGB is constants_display_standards.XYZ_TO_SRGB
    assert constants.REC709_TO_XYZ is constants_display_standards.REC709_TO_XYZ
    assert constants.XYZ_TO_REC709 is constants_display_standards.XYZ_TO_REC709
    assert constants.REC2020_TO_XYZ is constants_display_standards.REC2020_TO_XYZ
    assert constants.XYZ_TO_REC2020 is constants_display_standards.XYZ_TO_REC2020
    assert constants.ADOBE_RGB_TO_XYZ is constants_display_standards.ADOBE_RGB_TO_XYZ
    assert constants.XYZ_TO_ADOBE_RGB is constants_display_standards.XYZ_TO_ADOBE_RGB
    assert constants.PROPHOTO_RGB_TO_XYZ is constants_display_standards.PROPHOTO_RGB_TO_XYZ
    assert constants.XYZ_TO_PROPHOTO_RGB is constants_display_standards.XYZ_TO_PROPHOTO_RGB
    assert constants.DISPLAY_P3_TO_XYZ is constants_display_standards.DISPLAY_P3_TO_XYZ
    assert constants.XYZ_TO_DISPLAY_P3 is constants_display_standards.XYZ_TO_DISPLAY_P3
    assert constants.DCIP3_TO_XYZ is constants_display_standards.DCIP3_TO_XYZ
    assert constants.XYZ_TO_DCIP3 is constants_display_standards.XYZ_TO_DCIP3
    assert constants.NTSC_1953_TO_XYZ is constants_display_standards.NTSC_1953_TO_XYZ
    assert constants.XYZ_TO_NTSC_1953 is constants_display_standards.XYZ_TO_NTSC_1953
    assert constants.RGB_COLOURSPACE_DEFINITIONS is constants_display_standards.RGB_COLOURSPACE_DEFINITIONS
    assert constants.RGB_GAMUT_METADATA is constants_display_standards.RGB_GAMUT_METADATA
    assert constants.COMMON_GAMUTS is constants_display_standards.COMMON_GAMUTS


def test_rgb_registry_uses_constants_display_standards() -> None:
    assert RGB_COLOURSPACE_DEFINITIONS is constants_display_standards.RGB_COLOURSPACE_DEFINITIONS


def test_rgb_module_display_standards_reexports_constants_objects() -> None:
    assert rgb_display_standards.SRGB_TO_XYZ is constants_display_standards.SRGB_TO_XYZ
    assert rgb_display_standards.XYZ_TO_SRGB is constants_display_standards.XYZ_TO_SRGB
    assert rgb_display_standards.PROPHOTO_RGB_TO_XYZ is constants_display_standards.PROPHOTO_RGB_TO_XYZ
    assert rgb_display_standards.XYZ_TO_PROPHOTO_RGB is constants_display_standards.XYZ_TO_PROPHOTO_RGB
    assert (
        rgb_display_standards.RGB_COLOURSPACE_DEFINITIONS
        is constants_display_standards.RGB_COLOURSPACE_DEFINITIONS
    )
    assert rgb_display_standards.RGB_GAMUT_METADATA is constants_display_standards.RGB_GAMUT_METADATA
    assert rgb_display_standards.COMMON_GAMUTS is constants_display_standards.COMMON_GAMUTS
