"""Tests for LCH gamut-boundary computation."""

from __future__ import annotations

import numpy as np
import pytest

from color.gamut import (
    DisplayPrimaries,
    GamutBoundary,
    compute_LCH_gamut_boundary,
    is_within_primary_gamut,
)
from color.spaces.basic.lab import Lab_to_XYZ, LCHab_to_Lab


def test_compute_lch_boundary_shape_and_values():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([0.0, 50.0, 100.0]),
        hue_values=np.array([0.0, 90.0, 180.0, 270.0]),
        C_upper=180.0,
        iterations=8,
    )

    assert boundary.C_max.shape == (3, 4)
    assert np.all(np.isfinite(boundary.C_max))
    assert np.all(boundary.C_max >= 0)
    assert boundary.to_LCHab().shape == (3, 4, 3)
    assert boundary.to_Lab().shape == (3, 4, 3)
    assert boundary.to_XYZ().shape == (3, 4, 3)


def test_boundary_points_are_inside_and_expanded_points_are_mostly_outside():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([25.0, 50.0, 75.0]),
        hue_values=np.arange(0.0, 360.0, 45.0),
        C_upper=220.0,
        iterations=12,
    )

    XYZ = boundary.to_XYZ()
    assert np.all(is_within_primary_gamut(XYZ, primaries, tolerance=2e-2))

    expanded = boundary.to_LCHab()
    expanded[..., 1] += 5.0
    expanded_XYZ = Lab_to_XYZ(
        LCHab_to_Lab(expanded),
        whitepoint_XYZ=boundary.whitepoint_XYZ,
    )
    outside = ~is_within_primary_gamut(expanded_XYZ, primaries, tolerance=1e-4)
    assert np.count_nonzero(outside) >= outside.size // 2


def test_boundary_matches_bruteforce_grid_for_representative_direction():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    L = 50.0
    hue = 40.0
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([L]),
        hue_values=np.array([hue]),
        C_upper=220.0,
        iterations=12,
    )
    C_values = np.linspace(0.0, 220.0, 2001)
    LCHab = np.stack((
        np.full_like(C_values, L),
        C_values,
        np.full_like(C_values, hue),
    ), axis=-1)
    XYZ = Lab_to_XYZ(LCHab_to_Lab(LCHab), whitepoint_XYZ=boundary.whitepoint_XYZ)
    inside = is_within_primary_gamut(XYZ, primaries)
    brute = C_values[inside][-1]
    np.testing.assert_allclose(boundary.C_max[0, 0], brute, atol=0.25)


def test_slice_l_interpolates_boundary():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([40.0, 60.0]),
        hue_values=np.array([0.0, 180.0]),
        C_upper=180.0,
        iterations=6,
    )
    slice_l = boundary.slice_L(50.0)
    assert slice_l.shape == (2, 3)
    np.testing.assert_allclose(slice_l[:, 0], 50.0)
    np.testing.assert_allclose(slice_l[:, 2], [0.0, 180.0])


def test_boundary_area_volume_and_rings():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([0.0, 25.0, 50.0, 75.0, 100.0]),
        hue_values=np.arange(0.0, 361.0, 30.0),
        C_upper=180.0,
        iterations=8,
    )

    area_50 = boundary.area_at_L(50.0)
    areas = boundary.areas()
    volume = boundary.volume()
    rings, steps = boundary.gamut_rings([50.0, 100.0])
    ring_area = boundary.ring_area()
    ring_areas = boundary.ring_areas([50.0, 100.0])

    assert area_50 > 0
    assert areas.shape == (5,)
    assert np.all(areas >= 0)
    assert volume > 0
    assert rings.shape == (2, boundary.hue_values.size, 2)
    np.testing.assert_allclose(steps, [50.0, 100.0])
    assert ring_area > area_50
    assert set(ring_areas) == {50.0, 100.0}
    assert ring_areas[100.0] >= ring_areas[50.0]


def test_boundary_projected_plane_gamut():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([0.0, 25.0, 50.0, 75.0, 100.0]),
        hue_values=np.arange(0.0, 361.0, 45.0),
        C_upper=180.0,
        iterations=8,
    )

    projected_C = boundary.projected_chroma_boundary()
    projected_L = boundary.projected_lightness_boundary()
    projected_LCHab = boundary.projected_LCHab_boundary()
    projected_ab = boundary.projected_ab_boundary()
    projected_area = boundary.projected_ab_area()

    assert projected_C.shape == boundary.hue_values.shape
    assert projected_L.shape == boundary.hue_values.shape
    assert projected_LCHab.shape == (boundary.hue_values.size, 3)
    assert projected_ab.shape == (boundary.hue_values.size, 2)
    assert projected_area > 0
    np.testing.assert_allclose(projected_C, np.max(boundary.C_max, axis=0))
    np.testing.assert_allclose(projected_LCHab[:, 1], projected_C)
    np.testing.assert_allclose(projected_LCHab[:, 2], boundary.hue_values)
    hue_rad = np.radians(boundary.hue_values)
    expected_ab = np.stack(
        (
            projected_C * np.cos(hue_rad),
            projected_C * np.sin(hue_rad),
        ),
        axis=-1,
    )
    np.testing.assert_allclose(projected_ab, expected_ab, atol=1e-12)
    assert np.all(boundary.C_max <= projected_C[np.newaxis, :] + 1e-12)


def test_xy_boundary_is_closed_and_finite():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(primaries)

    primary_hull = boundary.xy_boundary()
    assert primary_hull.shape[1] == 2
    assert np.all(np.isfinite(primary_hull))
    np.testing.assert_allclose(primary_hull[0], primary_hull[-1])
    primary_area = 0.5 * abs(
        np.dot(primary_hull[:, 0], np.roll(primary_hull[:, 1], -1))
        - np.dot(primary_hull[:, 1], np.roll(primary_hull[:, 0], -1))
    )
    assert primary_area > 0


def test_xy_boundary_fallback_without_primaries():
    boundary = GamutBoundary(
        C_max=np.full((3, 4), 20.0),
        L_values=np.array([25.0, 50.0, 75.0]),
        hue_values=np.array([0.0, 120.0, 240.0, 360.0]),
        whitepoint_XYZ=np.array([95.047, 100.0, 108.883]),
        primaries=None,
    )

    xy = boundary.xy_boundary()
    assert xy.shape[1] == 2
    assert np.all(np.isfinite(xy))
    np.testing.assert_allclose(xy[0], xy[-1])


def test_boundary_summary_methods_validate_inputs():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    boundary = compute_LCH_gamut_boundary(
        primaries,
        L_values=np.array([0.0, 50.0, 100.0]),
        hue_values=np.array([0.0, 90.0, 180.0, 270.0]),
        C_upper=180.0,
        iterations=6,
    )
    with pytest.raises(ValueError, match="L is outside"):
        boundary.area_at_L(120.0)
    with pytest.raises(ValueError, match="L_steps"):
        boundary.gamut_rings([-1.0])


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"L_values": np.empty(0)}, "L_values"),
        ({"hue_values": np.empty(0)}, "hue_values"),
        ({"C_upper": 0}, "C_upper"),
        ({"iterations": 0}, "iterations"),
        ({"whitepoint_XYZ": [1, 2]}, "whitepoint_XYZ"),
    ],
)
def test_invalid_boundary_inputs_raise(kwargs, match):
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    with pytest.raises(ValueError, match=match):
        compute_LCH_gamut_boundary(primaries, **kwargs)
