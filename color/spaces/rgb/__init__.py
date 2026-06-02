"""RGB colour-space definitions and conversions."""

from __future__ import annotations

from .colourspace import RGBColorSpace
from .conversion import RGB_to_RGB, RGB_to_XYZ, XYZ_to_RGB, XYZ_to_sRGB, sRGB_to_XYZ
from .custom import RGB_colourspace_from_primaries_XYZ, RGB_colourspace_from_primaries_xy
from .display_standards import RGB_COLOURSPACE_DEFINITIONS
from .registry import (
    RGB_COLORSPACES,
    get_RGB_colourspace,
    list_RGB_colourspaces,
    register_RGB_colourspace,
)

__all__ = [
    "RGBColorSpace",  # RGB colour-space definition object
    "RGB_COLOURSPACE_DEFINITIONS",  # RGB colour-space standard definitions
    "RGB_COLORSPACES",  # registered RGB colour spaces
    "get_RGB_colourspace",  # resolve an RGB colour space by name or alias
    "list_RGB_colourspaces",  # list registered RGB colour-space names
    "register_RGB_colourspace",  # register a custom RGB colour space
    "RGB_colourspace_from_primaries_xy",  # create custom RGB space from primary xy coordinates
    "RGB_colourspace_from_primaries_XYZ",  # create custom RGB space from measured primary XYZ values
]

__all__ += [
    "RGB_to_XYZ",  # convert RGB values to XYZ
    "XYZ_to_RGB",  # convert XYZ values to RGB
    "RGB_to_RGB",  # convert between RGB colour spaces
    "sRGB_to_XYZ",  # convert sRGB values to XYZ
    "XYZ_to_sRGB",  # convert XYZ values to sRGB
]
