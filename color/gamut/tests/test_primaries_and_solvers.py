"""Tests for display-primary gamut solvers."""

from __future__ import annotations

from itertools import product

import numpy as np
import pytest

from color.gamut import (
    DisplayPrimaries,
    is_within_primary_gamut,
    primary_gamut_halfspaces,
    primary_gamut_vertices,
    solve_primary_weights,
)
from color.spaces.rgb import XYZ_to_RGB


def _rgb_cube() -> np.ndarray:
    return np.array(list(product((0.0, 1.0), repeat=3)), dtype=np.float64)


def test_display_primaries_from_rgb_colourspace_matches_linear_rgb_path():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    weights = np.array([0.25, 0.5, 0.75])
    XYZ = weights @ primaries.primaries_XYZ

    solved = solve_primary_weights(XYZ, primaries)
    rgb = XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False)

    np.testing.assert_allclose(solved, weights, atol=1e-12)
    np.testing.assert_allclose(solved, rgb, atol=1e-12)


def test_rgb_cube_vertices_are_inside_and_far_points_are_outside():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    vertices = _rgb_cube() @ primaries.primaries_XYZ
    assert np.all(is_within_primary_gamut(vertices, primaries))

    outside = np.array([
        [-1.0, 0.0, 0.0],
        primaries.whitepoint_XYZ * 1.5,
    ])
    np.testing.assert_array_equal(
        is_within_primary_gamut(outside, primaries),
        [False, False],
    )


def test_multi_primary_hull_inside_is_vectorised():
    primaries = DisplayPrimaries(
        [
            [41.0, 21.0, 2.0],
            [35.0, 70.0, 12.0],
            [18.0, 8.0, 80.0],
            [20.0, 55.0, 65.0],
        ],
        names=("R", "G", "B", "C"),
    )
    weights = np.array([
        [0.0, 0.0, 0.0, 0.0],
        [0.2, 0.4, 0.6, 0.8],
        [1.0, 1.0, 1.0, 1.0],
    ])
    XYZ = weights @ primaries.primaries_XYZ
    inside = is_within_primary_gamut(XYZ, primaries)

    assert inside.shape == (3,)
    np.testing.assert_array_equal(inside, [True, True, True])
    assert not bool(is_within_primary_gamut(primaries.whitepoint_XYZ * 1.4, primaries))


@pytest.mark.parametrize("count", [4, 5, 6])
def test_multi_primary_random_feasible_points_are_inside(count):
    base = np.array([
        [42.0, 21.0, 2.0],
        [34.0, 69.0, 11.0],
        [18.0, 7.0, 82.0],
        [10.0, 32.0, 68.0],
        [55.0, 35.0, 16.0],
        [12.0, 44.0, 18.0],
    ])
    primaries = DisplayPrimaries(base[:count])
    rng = np.random.default_rng(12)
    weights = rng.uniform(0.0, 1.0, size=(16, count))
    XYZ = weights @ primaries.primaries_XYZ
    assert np.all(is_within_primary_gamut(XYZ, primaries))


def test_linprog_primary_weight_solution_is_feasible():
    primaries = DisplayPrimaries(
        [
            [42.0, 21.0, 2.0],
            [34.0, 69.0, 11.0],
            [18.0, 7.0, 82.0],
            [10.0, 32.0, 68.0],
        ]
    )
    target_weights = np.array([0.25, 0.5, 0.75, 0.4])
    XYZ = target_weights @ primaries.primaries_XYZ

    weights = solve_primary_weights(XYZ, primaries)

    assert weights.shape == (4,)
    assert np.all(weights >= -1e-9)
    assert np.all(weights <= 1.0 + 1e-9)
    np.testing.assert_allclose(weights @ primaries.primaries_XYZ, XYZ, atol=1e-8)


def test_linprog_inside_test_returns_false_for_infeasible_points():
    primaries = DisplayPrimaries(
        [
            [42.0, 21.0, 2.0],
            [34.0, 69.0, 11.0],
            [18.0, 7.0, 82.0],
            [10.0, 32.0, 68.0],
        ]
    )
    points = np.stack((
        0.5 * primaries.whitepoint_XYZ,
        2.0 * primaries.whitepoint_XYZ,
    ))
    np.testing.assert_array_equal(
        is_within_primary_gamut(points, primaries, method="linprog"),
        [True, False],
    )


def test_vertices_and_halfspaces_shapes():
    primaries = DisplayPrimaries.from_RGB_colourspace("Display P3")
    vertices = primary_gamut_vertices(primaries)
    halfspaces = primary_gamut_halfspaces(primaries)

    assert vertices.shape == (8, 3)
    assert halfspaces.shape[1] == 4


@pytest.mark.parametrize(
    "primaries, match",
    [
        ([[1, 2]], "shape"),
        ([[1, 0, 0], [0, 1, 0]], "at least three"),
        ([[1, 0, 0], [2, 0, 0], [3, 0, 0]], "three-dimensional"),
        ([[1, 0, 0], [0, np.nan, 0], [0, 0, 1]], "finite"),
    ],
)
def test_invalid_display_primaries_raise(primaries, match):
    with pytest.raises(ValueError, match=match):
        DisplayPrimaries(primaries)


def test_invalid_methods_and_infeasible_weights_raise():
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")
    with pytest.raises(ValueError, match="method"):
        is_within_primary_gamut([1, 2, 3], primaries, method="unknown")
    with pytest.raises(ValueError, match="no feasible"):
        solve_primary_weights(primaries.whitepoint_XYZ * 2.0, primaries, method="linprog")
