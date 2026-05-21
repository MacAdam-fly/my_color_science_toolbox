"""Standard-observer LMS and XYZ conversion matrices.

The authoritative constants live in :mod:`color.constants.standard_observer_matrices`.
This module re-exports them for colorimetry-module locality.
"""

from __future__ import annotations

from color.constants.standard_observer_matrices import (
    LMS_2_DEGREE_TO_XYZ_2_DEGREE,
    LMS_10_DEGREE_TO_XYZ_10_DEGREE,
    XYZ_2_DEGREE_TO_LMS_2_DEGREE,
    XYZ_10_DEGREE_TO_LMS_10_DEGREE,
)

__all__ = [
    "LMS_2_DEGREE_TO_XYZ_2_DEGREE",
    "XYZ_2_DEGREE_TO_LMS_2_DEGREE",
    "LMS_10_DEGREE_TO_XYZ_10_DEGREE",
    "XYZ_10_DEGREE_TO_LMS_10_DEGREE",
]
