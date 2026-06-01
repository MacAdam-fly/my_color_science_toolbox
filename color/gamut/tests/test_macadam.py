"""Tests for MacAdam optimal colour stimuli limits."""

from __future__ import annotations

import numpy as np
import pytest

import color.gamut as gamut
from color.gamut import (
    is_within_macadam_limits,
    lab_gamut_coverage,
    macadam_limits,
    macadam_limits_published_xy_boundary,
    pointer_gamut,
)
from color.gamut.macadam.macadam_computed import ComputedMacAdamLimitsBoundary
from color.gamut.macadam.macadam_published import (
    MacAdamLimitsBoundary,
    is_within_macadam_limits as published_is_within_macadam_limits,
    macadam_limits as published_macadam_limits,
)
from color.gamut.macadam import macadam_limits_XYZ, macadam_limits_data
from color.spectra import SpectralShape


@pytest.mark.parametrize("illuminant", ["A", "C", "D65"])
def test_macadam_limits_data_and_xyz(illuminant):
    data = macadam_limits_data(illuminant)
    XYZ = macadam_limits_XYZ(illuminant)

    assert XYZ.shape == (len(data["Y"]), 3)
    assert XYZ.shape[0] > 0
    assert np.all(np.isfinite(XYZ))
    np.testing.assert_allclose(XYZ[:, 0], data["X"])
    np.testing.assert_allclose(XYZ[:, 1], data["Y"])
    np.testing.assert_allclose(XYZ[:, 2], data["Z"])


def test_macadam_limits_published_xy_boundary_is_closed():
    xy = macadam_limits_published_xy_boundary("D65")

    assert xy.ndim == 2
    assert xy.shape[1] == 2
    assert np.all(np.isfinite(xy))
    np.testing.assert_allclose(xy[0], xy[-1])


def test_is_within_macadam_limits_matches_colour():
    colour = pytest.importorskip("colour")
    xyY_colour = np.array(
        [
            [0.3205, 0.4131, 0.51],
            [0.0005, 0.0031, 0.001],
            [0.2, 0.3, 0.5],
            [0.4, 0.4, 0.5],
        ],
        dtype=np.float64,
    )
    xyY_project = xyY_colour.copy()
    xyY_project[:, 2] *= 100.0
    XYZ = np.column_stack((
        xyY_project[:, 0] * xyY_project[:, 2] / xyY_project[:, 1],
        xyY_project[:, 2],
        (1.0 - xyY_project[:, 0] - xyY_project[:, 1]) * xyY_project[:, 2] / xyY_project[:, 1],
    ))

    actual = is_within_macadam_limits(XYZ, "A", tolerance=1e-7)
    expected = colour.volume.is_within_macadam_limits(xyY_colour, "A")
    np.testing.assert_array_equal(actual, expected)


def test_macadam_limits_and_pointer_coverage():
    boundary = macadam_limits(
        "D65",
        L_values=np.array([0.0, 25.0, 50.0, 75.0, 100.0]),
        hue_values=np.arange(0.0, 361.0, 45.0),
        C_upper=300.0,
        iterations=8,
    )

    assert isinstance(boundary, MacAdamLimitsBoundary)
    assert boundary.illuminant == "D65"
    assert boundary.vertices_XYZ.shape == macadam_limits_XYZ("D65").shape
    np.testing.assert_allclose(boundary.xy_boundary(), macadam_limits_published_xy_boundary("D65"))
    assert boundary.lab_volume() > 0

    with pytest.warns(UserWarning):
        coverage = lab_gamut_coverage(pointer_gamut(), boundary)
    assert np.isfinite(coverage)
    assert coverage >= 0


def test_macadam_limits_auto_uses_published_for_standard_illuminants():
    actual = macadam_limits(
        "D65",
        L_values=np.array([0.0, 50.0, 100.0]),
        hue_values=np.array([0.0, 120.0, 240.0, 360.0]),
        iterations=4,
    )
    expected = published_macadam_limits(
        "D65",
        L_values=np.array([0.0, 50.0, 100.0]),
        hue_values=np.array([0.0, 120.0, 240.0, 360.0]),
        iterations=4,
    )

    assert isinstance(actual, MacAdamLimitsBoundary)
    np.testing.assert_allclose(actual.C_max, expected.C_max)


def test_macadam_limits_auto_uses_computed_when_computed_options_are_given():
    shape = SpectralShape(400, 700, 100)

    boundary = macadam_limits(
        "D65",
        shape=shape,
        L_values=[0.0, 50.0, 100.0],
        hue_values=[0.0, 180.0, 360.0],
        iterations=3,
    )

    assert isinstance(boundary, ComputedMacAdamLimitsBoundary)


def test_macadam_limits_source_computed_forces_computed_route():
    shape = SpectralShape(400, 700, 100)

    boundary = macadam_limits(
        "D65",
        source="computed",
        shape=shape,
        L_values=[0.0, 50.0, 100.0],
        hue_values=[0.0, 180.0, 360.0],
        iterations=3,
    )

    assert isinstance(boundary, ComputedMacAdamLimitsBoundary)


def test_macadam_limits_source_published_rejects_computed_options():
    with pytest.raises(ValueError, match="source='published'"):
        macadam_limits("D65", source="published", shape=SpectralShape(400, 700, 100))


def test_is_within_macadam_limits_uses_dispatch_rules():
    shape = SpectralShape(400, 700, 100)
    sample = np.array([39.57, 51.0, 32.89])

    assert bool(is_within_macadam_limits(sample, "D65")) == bool(
        published_is_within_macadam_limits(sample, "D65")
    )
    assert bool(
        is_within_macadam_limits(
            [0.0, 0.0, 0.0],
            "D65",
            source="computed",
            shape=shape,
        )
    )


def test_computed_macadam_is_not_top_level_gamut_api():
    assert not hasattr(gamut, "computed_macadam_limits")
    assert not hasattr(gamut, "is_within_computed_macadam_limits")


@pytest.mark.parametrize("illuminant", ["invalid", "D50"])
def test_invalid_illuminant_raises(illuminant):
    with pytest.raises(ValueError, match="illuminant"):
        macadam_limits_data(illuminant)
