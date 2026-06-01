"""MacAdam optimal-colour gamut utilities."""

from __future__ import annotations

from .macadam import (
    ComputedMacAdamLimitsBoundary,
    MacAdamLimitsBoundary,
    computed_macadam_limits,
    computed_macadam_limits_data,
    computed_macadam_limits_XYZ,
    is_within_computed_macadam_limits,
    is_within_macadam_limits,
    macadam_limits,
    macadam_limits_XYZ,
    macadam_limits_data,
    macadam_limits_published_xy_boundary,
)

__all__ = [
    "MacAdamLimitsBoundary",  # cached MacAdam GamutBoundary subtype
    "macadam_limits",  # return published A/C/D65 MacAdam limits
    "is_within_macadam_limits",  # test XYZ values inside cached MacAdam limits
    "macadam_limits_published_xy_boundary",  # return published MacAdam xy boundary
]

__all__ += [
    "macadam_limits_data",  # return cached MacAdam raw dataset columns
    "macadam_limits_XYZ",  # return cached MacAdam XYZ mesh vertices
]

__all__ += [
    "ComputedMacAdamLimitsBoundary",  # computed MacAdam GamutBoundary subtype
    "computed_macadam_limits",  # compute MacAdam limits from CMFs and an illuminant
    "is_within_computed_macadam_limits",  # test XYZ values inside computed MacAdam limits
    "computed_macadam_limits_XYZ",  # return computed MacAdam XYZ mesh vertices
    "computed_macadam_limits_data",  # return computed MacAdam data columns
]
