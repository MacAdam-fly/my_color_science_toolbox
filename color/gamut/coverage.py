"""Display-gamut coverage metrics."""

from __future__ import annotations

from typing import Sequence
import warnings

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import ConvexHull

from color.colorimetry import XYZ_to_xy

from .boundary import GamutBoundary
from .primaries import DisplayPrimaries, as_display_primaries


def _as_polygon(points: Sequence[Sequence[float]] | np.ndarray, *, name: str) -> np.ndarray:
    """Return finite open 2D polygon vertices."""
    polygon = np.array(points, dtype=np.float64, copy=True)
    if polygon.ndim != 2 or polygon.shape[1] != 2:
        raise ValueError(f"{name} must have shape (n, 2)")
    if polygon.shape[0] >= 2 and np.allclose(polygon[0], polygon[-1]):
        polygon = polygon[:-1]
    if polygon.shape[0] < 3:
        raise ValueError(f"{name} must contain at least three vertices")
    if not np.all(np.isfinite(polygon)):
        raise ValueError(f"{name} must be finite")
    return polygon


def _signed_polygon_area(polygon: np.ndarray) -> float:
    """Return signed polygon area."""
    x = polygon[:, 0]
    y = polygon[:, 1]
    return float(0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def _polygon_area(polygon: Sequence[Sequence[float]] | np.ndarray) -> float:
    """Return absolute polygon area."""
    return abs(_signed_polygon_area(_as_polygon(polygon, name="polygon")))


def _ccw_polygon(polygon: np.ndarray) -> np.ndarray:
    """Return polygon vertices in counter-clockwise order."""
    return polygon if _signed_polygon_area(polygon) >= 0 else polygon[::-1]


def _primary_xy_polygon(
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
) -> np.ndarray:
    """Return an open CIE xy convex-hull polygon for display primaries."""
    display = as_display_primaries(primaries)
    xy = XYZ_to_xy(display.primaries_XYZ)
    if xy.shape[0] < 3:
        raise ValueError("at least three primary chromaticities are required")
    hull = ConvexHull(xy)
    return _ccw_polygon(xy[hull.vertices])


def _xy_polygon(points: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    """Return a counter-clockwise CIE xy convex-hull polygon from xy points."""
    xy = _as_polygon(points, name="xy")
    hull = ConvexHull(xy)
    return _ccw_polygon(xy[hull.vertices])


def _line_intersection(
    start: np.ndarray,
    end: np.ndarray,
    clip_start: np.ndarray,
    clip_end: np.ndarray,
) -> np.ndarray:
    """Return intersection between two infinite 2D lines."""
    direction = end - start
    clip_direction = clip_end - clip_start
    denominator = (
        direction[0] * clip_direction[1]
        - direction[1] * clip_direction[0]
    )
    if abs(denominator) <= 1e-15:
        return end
    delta = clip_start - start
    t = (
        delta[0] * clip_direction[1]
        - delta[1] * clip_direction[0]
    ) / denominator
    return start + t * direction


def _clip_convex_polygon(subject: np.ndarray, clip: np.ndarray) -> np.ndarray:
    """Clip a polygon by a convex counter-clockwise polygon."""
    output = _ccw_polygon(_as_polygon(subject, name="subject"))
    clip_polygon = _ccw_polygon(_as_polygon(clip, name="clip"))

    for index, clip_start in enumerate(clip_polygon):
        clip_end = clip_polygon[(index + 1) % clip_polygon.shape[0]]
        edge = clip_end - clip_start

        def inside(point: np.ndarray) -> bool:
            vector = point - clip_start
            return bool(edge[0] * vector[1] - edge[1] * vector[0] >= -1e-12)

        input_polygon = output
        if input_polygon.size == 0:
            break
        output_vertices: list[np.ndarray] = []
        previous = input_polygon[-1]
        previous_inside = inside(previous)
        for current in input_polygon:
            current_inside = inside(current)
            if current_inside:
                if not previous_inside:
                    output_vertices.append(_line_intersection(previous, current, clip_start, clip_end))
                output_vertices.append(current)
            elif previous_inside:
                output_vertices.append(_line_intersection(previous, current, clip_start, clip_end))
            previous = current
            previous_inside = current_inside
        output = np.array(output_vertices, dtype=np.float64)

    if output.ndim != 2 or output.shape[0] < 3:
        return np.empty((0, 2), dtype=np.float64)
    return output


def xy_gamut_area(
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
) -> float:
    """Return CIE xy primary-hull area for display primaries."""
    return _polygon_area(_primary_xy_polygon(primaries))


def xy_gamut_area_from_xy(xy: Sequence[Sequence[float]] | np.ndarray) -> float:
    """Return CIE xy convex-hull area from xy points or polygon vertices."""
    return _polygon_area(_xy_polygon(xy))


def xy_gamut_intersection_area(
    test: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
    reference: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
) -> float:
    """Return CIE xy intersection area between two primary hulls."""
    test_polygon = _primary_xy_polygon(test)
    reference_polygon = _primary_xy_polygon(reference)
    intersection = _clip_convex_polygon(test_polygon, reference_polygon)
    if intersection.shape[0] < 3:
        return 0.0
    return _polygon_area(intersection)


def xy_gamut_intersection_area_from_xy(
    test_xy: Sequence[Sequence[float]] | np.ndarray,
    reference_xy: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Return CIE xy intersection area between two xy hulls."""
    test_polygon = _xy_polygon(test_xy)
    reference_polygon = _xy_polygon(reference_xy)
    intersection = _clip_convex_polygon(test_polygon, reference_polygon)
    if intersection.shape[0] < 3:
        return 0.0
    return _polygon_area(intersection)


def xy_gamut_coverage(
    test: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
    reference: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
) -> float:
    """Return directional CIE xy area coverage of *reference* by *test*."""
    reference_area = xy_gamut_area(reference)
    if reference_area <= 0:
        raise ValueError("reference xy gamut area must be positive")
    return xy_gamut_intersection_area(test, reference) / reference_area


def xy_gamut_coverage_from_xy(
    test_xy: Sequence[Sequence[float]] | np.ndarray,
    reference_xy: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Return directional CIE xy area coverage from xy points or polygons."""
    reference_area = xy_gamut_area_from_xy(reference_xy)
    if reference_area <= 0:
        raise ValueError("reference xy gamut area must be positive")
    return xy_gamut_intersection_area_from_xy(test_xy, reference_xy) / reference_area


def _validate_boundary(boundary: GamutBoundary, *, name: str) -> GamutBoundary:
    """Return *boundary* if it is a GamutBoundary."""
    if not isinstance(boundary, GamutBoundary):
        raise TypeError(f"{name} must be a GamutBoundary")
    return boundary


def _closed_hue_grid(C: np.ndarray, hue_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ``C`` and hue values closed over one full hue period."""
    C = np.asarray(C, dtype=np.float64)
    hue = np.asarray(hue_values, dtype=np.float64)
    if C.ndim != 2 or C.shape[1] != hue.size:
        raise ValueError("C shape must match hue_values")
    if hue.size < 2:
        raise ValueError("hue_values must contain at least two samples")
    if np.any(np.diff(hue) <= 0):
        raise ValueError("hue_values must be strictly increasing")
    if np.isclose(hue[-1] - hue[0], 360.0):
        return C, hue
    return np.column_stack((C, C[:, 0])), np.append(hue, hue[0] + 360.0)


def _lch_volume_from_C(
    C: np.ndarray,
    L_values: np.ndarray,
    hue_values: np.ndarray,
) -> float:
    """Return Lab/LCHab volume from ``C_max[L, h]`` values.

    Mathematically equivalent to the a*b* shoelace-area method used by
    ``GamutBoundary.volume()`` in boundary.py.  Kept as a standalone helper
    here because overlap-volume calculations need to operate on raw
    ``C_max`` arrays (e.g. ``min(C_test, C_ref)``) rather than full
    ``GamutBoundary`` instances.
    """
    C_closed, hue_closed = _closed_hue_grid(C, hue_values)
    hue_radians = np.radians(hue_closed)
    areas = 0.5 * np.trapz(C_closed**2, hue_radians, axis=1)
    if L_values.size == 1:
        return 0.0
    return float(np.trapz(areas, L_values))


def lab_gamut_volume(boundary: GamutBoundary) -> float:
    """Return deterministic Lab/LCHab gamut volume for a boundary."""
    boundary = _validate_boundary(boundary, name="boundary")
    return _lch_volume_from_C(boundary.C_max, boundary.L_values, boundary.hue_values)


def _regular_grid_C_on_reference(
    test: GamutBoundary,
    reference: GamutBoundary,
) -> np.ndarray:
    """Interpolate test ``C_max`` values onto the reference boundary grid."""
    C_source, hue_source = _closed_hue_grid(test.C_max, test.hue_values)
    hue_start = hue_source[0]
    target_hue = ((reference.hue_values - hue_start) % 360.0) + hue_start
    target_hue = np.where(
        np.isclose(reference.hue_values - hue_start, 360.0),
        hue_start + 360.0,
        target_hue,
    )
    interpolator = RegularGridInterpolator(
        (test.L_values, hue_source),
        C_source,
        bounds_error=False,
        fill_value=0.0,
    )
    L_grid, hue_grid = np.meshgrid(reference.L_values, target_hue, indexing="ij")
    points = np.stack((L_grid, hue_grid), axis=-1)
    C = interpolator(points)
    return np.maximum(C, 0.0)


def _warn_if_boundary_grids_differ(test: GamutBoundary, reference: GamutBoundary) -> None:
    """Warn if coverage will interpolate between different grids."""
    same_L = test.L_values.shape == reference.L_values.shape and np.allclose(test.L_values, reference.L_values)
    same_hue = test.hue_values.shape == reference.hue_values.shape and np.allclose(test.hue_values, reference.hue_values)
    if not (same_L and same_hue):
        warnings.warn(
            "GamutBoundary grids differ; test C_max values will be interpolated "
            "onto the reference boundary grid.",
            UserWarning,
            stacklevel=3,
        )


def _validate_boundary_pair(
    test: GamutBoundary,
    reference: GamutBoundary,
) -> tuple[GamutBoundary, GamutBoundary]:
    """Validate two comparable boundaries."""
    test = _validate_boundary(test, name="test_boundary")
    reference = _validate_boundary(reference, name="reference_boundary")
    if not np.allclose(test.whitepoint_XYZ, reference.whitepoint_XYZ):
        warnings.warn(
            "GamutBoundary whitepoint_XYZ values differ; Lab coverage will compare "
            "the stored C_max boundaries directly without chromatic adaptation.",
            UserWarning,
            stacklevel=3,
        )
    _warn_if_boundary_grids_differ(test, reference)
    return test, reference


def lab_gamut_overlap_volume(
    test_boundary: GamutBoundary,
    reference_boundary: GamutBoundary,
) -> float:
    """Return deterministic Lab/LCHab overlap volume between two boundaries."""
    test, reference = _validate_boundary_pair(test_boundary, reference_boundary)
    C_test = _regular_grid_C_on_reference(test, reference)
    C_overlap = np.minimum(C_test, reference.C_max)
    return _lch_volume_from_C(C_overlap, reference.L_values, reference.hue_values)


def lab_gamut_coverage(
    test_boundary: GamutBoundary,
    reference_boundary: GamutBoundary,
) -> float:
    """Return directional Lab/LCHab volume coverage of reference by test."""
    reference = _validate_boundary(reference_boundary, name="reference_boundary")
    reference_volume = lab_gamut_volume(reference)
    if reference_volume <= 0:
        raise ValueError("reference Lab gamut volume must be positive")
    return lab_gamut_overlap_volume(test_boundary, reference_boundary) / reference_volume


__all__ = [
    "xy_gamut_area",
    "xy_gamut_area_from_xy",
    "xy_gamut_intersection_area",
    "xy_gamut_intersection_area_from_xy",
    "xy_gamut_coverage",
    "xy_gamut_coverage_from_xy",
    "lab_gamut_volume",
    "lab_gamut_overlap_volume",
    "lab_gamut_coverage",
]
