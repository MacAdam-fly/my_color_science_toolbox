"""Display-primary gamut utilities."""

from __future__ import annotations

from .analysis import GamutAnalysis, analyze_gamut
from .boundary import GamutBoundary, compute_LCH_gamut_boundary
from .coverage import (
    lab_gamut_coverage,
    lab_gamut_volume,
    xy_gamut_coverage,
    xy_gamut_area,
    xy_gamut_coverage_from_xy,
    xy_gamut_area_from_xy,
)
from .macadam import (
    is_within_macadam_limits,
    macadam_limits,
    macadam_limits_published_xy_boundary,
)
from .primaries import DisplayPrimaries
from .pointer import (
    is_within_pointer_gamut,
    pointer_gamut,
    pointer_gamut_published_xy_boundary,
)
from .solvers import is_within_primary_gamut, solve_primary_weights

__all__ = [
    "DisplayPrimaries",  # display-primary definition object
    "GamutBoundary",  # regular Lab/LCHab gamut-boundary object
]

__all__ += [
    "is_within_primary_gamut",  # test whether XYZ values are display-primary feasible
    "solve_primary_weights",  # solve primary weights reproducing XYZ values
]

__all__ += [
    "compute_LCH_gamut_boundary",  # compute display-primary boundary in Lab/LCHab
]

__all__ += [
    "GamutAnalysis",  # high-level gamut analysis result object
    "analyze_gamut",  # compute xy, Lab and reference coverage summary metrics
]

__all__ += [
    "xy_gamut_coverage",  # compute directional xy coverage from RGB names, primaries or XYZ rows
    "xy_gamut_area",  # compute xy area from RGB names, primaries or XYZ rows，same as GamutBoundary.xy_area()
    "xy_gamut_coverage_from_xy",  # compute directional xy coverage from xy points or hulls
    "xy_gamut_area_from_xy",  # compute xy area from xy points or hulls
]

__all__ += [
    "lab_gamut_volume",  # compute Lab/LCHab volume of a GamutBoundary，LCH version differs from GamutBoundary.volume() by using cylindrical coordinates
    "lab_gamut_coverage",  # compute directional Lab/LCHab volume coverage
]

__all__ += [
    "macadam_limits",  # return MacAdam limits with automatic source dispatch
    "macadam_limits_published_xy_boundary",  # return cached MacAdam xy boundary
    "is_within_macadam_limits",  # test whether XYZ values are inside dispatched MacAdam limits
]

__all__ += [
    "pointer_gamut",  # return Pointer real-surface gamut as a GamutBoundary
    "pointer_gamut_published_xy_boundary",  # return cached Pointer xy boundary
    "is_within_pointer_gamut",  # test whether XYZ values are inside Pointer gamut
]
