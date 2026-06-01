"""Tests for computed MacAdam optimal-colour limits."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import XYZ_to_xyY
from color.colorimetry.lightness import Lstar_to_Y
from color.gamut.macadam import (
    ComputedMacAdamLimitsBoundary,
    computed_macadam_limits,
    computed_macadam_limits_XYZ,
    computed_macadam_limits_data,
    is_within_computed_macadam_limits,
)
from color.spectra import SpectralShape


def test_computed_macadam_limits_data_uses_Lstar_derived_Y_factor():
    shape = SpectralShape(400, 700, 100)
    L_values = np.array([20.0, 50.0, 80.0])
    data = computed_macadam_limits_data(shape=shape, L_values=L_values)
    expected_Y = np.asarray(Lstar_to_Y(L_values, Y_n=100.0))

    assert set(data) == {"x", "y", "Y", "X", "Z", "L", "a", "b", "C", "h"}
    for values in data.values():
        assert values.ndim == 1
        assert np.all(np.isfinite(values))
    np.testing.assert_allclose(np.unique(np.round(data["Y"], 8)), expected_Y)


def test_computed_macadam_limits_data_accepts_static_Y_layers():
    shape = SpectralShape(400, 700, 100)
    data = computed_macadam_limits_data(shape=shape, Y_values=[10.0, 50.0, 90.0])

    np.testing.assert_allclose(np.unique(np.round(data["Y"], 8)), [10.0, 50.0, 90.0])


def test_computed_macadam_limits_handles_zero_Y_layer():
    shape = SpectralShape(400, 700, 100)
    data = computed_macadam_limits_data(shape=shape, Y_values=[0.0])
    vertices = computed_macadam_limits_XYZ(shape=shape, Y_values=[0.0])
    white_data = computed_macadam_limits_data(shape=shape, Y_values=[100.0])
    white_xy = XYZ_to_xyY([
        white_data["X"][0],
        white_data["Y"][0],
        white_data["Z"][0],
    ])[:2]

    assert vertices.shape == (1, 3)
    np.testing.assert_allclose(vertices[0], [0.0, 0.0, 0.0])
    assert len(data["Y"]) == 1
    np.testing.assert_allclose([data["x"][0], data["y"][0]], white_xy)
    np.testing.assert_allclose(data["Y"], [0.0])
    np.testing.assert_allclose(data["C"], [0.0])

    boundary = computed_macadam_limits(
        shape=shape,
        L_values=[0.0],
        hue_values=[0.0, 180.0, 360.0],
    )
    np.testing.assert_allclose(boundary.C_max, [[0.0, 0.0, 0.0]])
    assert bool(is_within_computed_macadam_limits([0.0, 0.0, 0.0], shape=shape, Y_values=[0.0]))
    assert not bool(is_within_computed_macadam_limits([1.0, 0.0, 0.0], shape=shape, Y_values=[0.0]))


def test_computed_macadam_limits_XYZ_returns_Y100_vertices():
    shape = SpectralShape(400, 700, 100)
    vertices = computed_macadam_limits_XYZ(shape=shape, Y_values=[10.0, 50.0, 90.0])

    assert vertices.ndim == 2
    assert vertices.shape[1] == 3
    assert np.all(np.isfinite(vertices))
    np.testing.assert_allclose(np.unique(np.round(vertices[:, 1], 8)), [10.0, 50.0, 90.0])


def test_is_within_computed_macadam_limits_accepts_vertices_and_rejects_far_point():
    shape = SpectralShape(400, 700, 100)
    vertices = computed_macadam_limits_XYZ(shape=shape, Y_values=[0.0, 50.0, 100.0])

    inside = is_within_computed_macadam_limits(
        vertices[:4],
        shape=shape,
        Y_values=[0.0, 50.0, 100.0],
    )
    np.testing.assert_array_equal(inside, np.array([True, True, True, True]))
    assert not bool(
        is_within_computed_macadam_limits(
            [-10.0, 20.0, 30.0],
            shape=shape,
            Y_values=[0.0, 50.0, 100.0],
        )
    )


def test_computed_macadam_limits_returns_regular_LCH_boundary():
    shape = SpectralShape(400, 700, 100)
    boundary = computed_macadam_limits(
        shape=shape,
        L_values=[0.0, 50.0, 100.0],
        hue_values=[0.0, 90.0, 180.0, 270.0, 360.0],
        C_upper=200.0,
        iterations=5,
    )

    assert isinstance(boundary, ComputedMacAdamLimitsBoundary)
    assert boundary.C_max.shape == (3, 5)
    assert boundary.vertices_XYZ.shape[1] == 3
    assert boundary.volume() > 0
    xy = boundary.xy_boundary()
    assert xy.ndim == 2
    assert xy.shape[1] == 2
    np.testing.assert_allclose(xy[0], xy[-1])


def test_computed_macadam_limits_invalid_options_raise():
    shape = SpectralShape(400, 700, 100)
    with pytest.raises(ValueError, match="C_upper"):
        computed_macadam_limits(shape=shape, C_upper=0.0)
    with pytest.raises(ValueError, match="iterations"):
        computed_macadam_limits(shape=shape, iterations=0)
    with pytest.raises(ValueError, match="tolerance"):
        is_within_computed_macadam_limits(
            [1.0, 2.0, 3.0],
            shape=shape,
            tolerance=-1.0,
        )
    with pytest.raises(ValueError, match="L_values and Y_values"):
        computed_macadam_limits_data(
            shape=shape,
            L_values=[50.0],
            Y_values=[50.0],
        )
