"""Display-primary gamut utilities."""

from __future__ import annotations

from .boundary import GamutBoundary, compute_LCH_gamut_boundary
from .coverage import (
    lab_gamut_coverage,
    lab_gamut_overlap_volume,
    lab_gamut_volume,
    xy_gamut_area,
    xy_gamut_area_from_xy,
    xy_gamut_coverage,
    xy_gamut_coverage_from_xy,
    xy_gamut_intersection_area,
    xy_gamut_intersection_area_from_xy,
)
from .mesh import is_within_mesh_volume
from .primaries import DisplayPrimaries
from .pointer import (
    is_within_pointer_gamut,
    pointer_gamut_LCHab,
    pointer_gamut_XYZ,
    pointer_gamut_boundary,
    pointer_gamut_data,
    pointer_gamut_whitepoint_XYZ,
    pointer_gamut_xy_boundary,
)
from .solvers import (
    is_within_primary_gamut,
    primary_gamut_halfspaces,
    primary_gamut_vertices,
    solve_primary_weights,
)

__all__ = [
    "DisplayPrimaries",
    "GamutBoundary",
    "is_within_primary_gamut",
    "solve_primary_weights",
    "primary_gamut_vertices",
    "primary_gamut_halfspaces",
    "compute_LCH_gamut_boundary",
    "xy_gamut_area",
    "xy_gamut_area_from_xy",
    "xy_gamut_intersection_area",
    "xy_gamut_intersection_area_from_xy",
    "xy_gamut_coverage",
    "xy_gamut_coverage_from_xy",
    "lab_gamut_volume",
    "lab_gamut_overlap_volume",
    "lab_gamut_coverage",
    "is_within_mesh_volume",
    "pointer_gamut_data",
    "pointer_gamut_whitepoint_XYZ",
    "pointer_gamut_LCHab",
    "pointer_gamut_xy_boundary",
    "pointer_gamut_boundary",
    "pointer_gamut_XYZ",
    "is_within_pointer_gamut",
]
