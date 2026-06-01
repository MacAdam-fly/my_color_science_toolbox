"""Tests for mesh-volume and Pointer gamut utilities."""

from __future__ import annotations

import numpy as np
import pytest

from color.gamut import (
    GamutBoundary,
    is_within_pointer_gamut,
    lab_gamut_volume,
    pointer_gamut,
    pointer_gamut_published_xy_boundary,
)
from color.gamut.mesh import is_within_mesh_volume
from color.gamut.pointer import (
    PointerGamutBoundary,
    pointer_gamut_LCHab,
    pointer_gamut_XYZ,
    pointer_gamut_data,
    pointer_gamut_whitepoint_XYZ,
)


def test_is_within_mesh_volume_single_and_batch():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    assert bool(is_within_mesh_volume([0.1, 0.1, 0.1], vertices))
    result = is_within_mesh_volume(
        [[0.1, 0.1, 0.1], [2.0, 0.1, 0.1]],
        vertices,
    )
    np.testing.assert_array_equal(result, [True, False])


def test_is_within_mesh_volume_rejects_invalid_vertices():
    with pytest.raises(ValueError, match="vertices_XYZ"):
        is_within_mesh_volume([0.0, 0.0, 0.0], [[0, 0, 0], [1, 0, 0]])
    with pytest.raises(ValueError, match="three-dimensional"):
        is_within_mesh_volume(
            [0.0, 0.0, 0.0],
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        )


def test_pointer_gamut_data_and_boundary_shape():
    data = pointer_gamut_data()
    boundary = pointer_gamut()

    assert {"L", "hab", "C", "Xn", "Yn", "Zn"} <= set(data)
    assert isinstance(boundary, GamutBoundary)
    assert isinstance(boundary, PointerGamutBoundary)
    assert boundary.primaries is None
    np.testing.assert_allclose(boundary.L_values, [20, 30, 40, 50, 60, 70, 80, 90])
    np.testing.assert_allclose(boundary.hue_values, np.arange(0.0, 361.0, 10.0))
    assert boundary.C_max.shape == (8, 37)
    assert lab_gamut_volume(boundary) > 0


def test_pointer_gamut_whitepoint_and_lch_rows():
    whitepoint = pointer_gamut_whitepoint_XYZ()
    LCHab = pointer_gamut_LCHab()

    np.testing.assert_allclose(whitepoint, [98.07226476, 100.0, 118.22541898])
    assert LCHab.shape == (296, 3)
    np.testing.assert_allclose(LCHab[:3, 0], 20.0)
    np.testing.assert_allclose(LCHab[:3, 2], [0.0, 10.0, 20.0])


def test_pointer_gamut_published_xy_boundary_is_closed_xy_plane_envelope():
    xy = pointer_gamut_published_xy_boundary()

    assert xy.ndim == 2
    assert xy.shape[1] == 2
    assert xy.shape == (33, 2)
    assert np.all(np.isfinite(xy))
    np.testing.assert_allclose(xy[0], xy[-1])


def test_pointer_boundary_has_xy_boundary():
    boundary = pointer_gamut()
    np.testing.assert_allclose(boundary.xy_boundary(), pointer_gamut_published_xy_boundary())


def test_is_within_pointer_gamut_boundary_vertices_and_batch_shape():
    vertices = pointer_gamut_XYZ()
    inside = is_within_pointer_gamut(vertices, tolerance=1e-7)

    assert vertices.shape == (296, 3)
    assert inside.shape == (296,)
    assert np.count_nonzero(inside) >= 290

    result = is_within_pointer_gamut([vertices[0], [0.0, 0.0, 0.0]], tolerance=1e-7)
    assert result.shape == (2,)
    assert bool(result[0])
    assert not bool(result[1])


def test_is_within_pointer_gamut_matches_colour_for_representative_points():
    colour = pytest.importorskip("colour")

    XYZ = np.array(
        [
            [32.05, 41.31, 51.00],
            [0.05, 0.31, 0.10],
            pointer_gamut_XYZ()[100],
        ],
        dtype=np.float64,
    )
    ours = is_within_pointer_gamut(XYZ, tolerance=1e-7)
    expected = colour.volume.is_within_pointer_gamut(XYZ / 100.0)

    np.testing.assert_array_equal(ours, expected)
