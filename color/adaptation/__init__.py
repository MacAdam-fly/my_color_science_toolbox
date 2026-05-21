"""Chromatic adaptation helpers."""

from __future__ import annotations

from .matrices import (
    CAT_BRADFORD,
    CAT_CAT02,
    CAT_CAT16,
    CAT_VON_KRIES,
    CHROMATIC_ADAPTATION_TRANSFORMS,
)
from .chromatic_adaptation import (
    adapt_from_D65,
    adapt_to_D65,
    chromatic_adaptation_XYZ,
    matrix_chromatic_adaptation_von_kries,
)

__all__ = [
    "CAT_VON_KRIES",  # Von Kries chromatic adaptation transform
    "CAT_BRADFORD",  # Bradford chromatic adaptation transform
    "CAT_CAT02",  # CAT02 chromatic adaptation transform
    "CAT_CAT16",  # CAT16 chromatic adaptation transform
    "CHROMATIC_ADAPTATION_TRANSFORMS",  # supported chromatic adaptation transforms
    "matrix_chromatic_adaptation_von_kries",  # compute a Von Kries style adaptation matrix
    "chromatic_adaptation_XYZ",  # adapt XYZ values between whitepoints
    "adapt_to_D65",  # adapt XYZ values from a source whitepoint to D65
    "adapt_from_D65",  # adapt D65-referred XYZ values to a target whitepoint
]
