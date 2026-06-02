"""Reflectance recovery from colour stimuli."""

from __future__ import annotations

from .matrix import reflectance_recovery_matrix, second_difference_matrix
from .reflectance import recover_reflectance_from_XYZ, recover_reflectance_from_xyY

__all__ = [
    "recover_reflectance_from_XYZ",  # recover bounded smooth reflectance from XYZ
    "recover_reflectance_from_xyY",  # recover bounded smooth reflectance from xyY
]

__all__ += [
    "reflectance_recovery_matrix",  # build the reflectance-to-XYZ linear matrix
    "second_difference_matrix",  # build the smoothness regularisation matrix
]
