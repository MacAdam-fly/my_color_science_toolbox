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

    assert set(data) == {"L", "h", "C_max"}
    assert XYZ.shape == (len(data["L"]), 3)
    assert XYZ.shape[0] > 0
    assert np.all(np.isfinite(XYZ))
    assert np.all(np.isfinite(data["C_max"]))
    assert np.all(data["C_max"] >= 0.0)


def test_macadam_limits_published_xy_boundary_is_closed():
    xy = macadam_limits_published_xy_boundary("D65")

    assert xy.ndim == 2
    assert xy.shape[1] == 2
    assert np.all(np.isfinite(xy))
    np.testing.assert_allclose(xy[0], xy[-1])


def test_is_within_macadam_limits_matches_reference_values():
    xyY_reference = np.array(
        [
            [0.3205, 0.4131, 0.51],
            [0.0005, 0.0031, 0.001],
            [0.2, 0.3, 0.5],
            [0.4, 0.4, 0.5],
        ],
        dtype=np.float64,
    )
    xyY_project = xyY_reference.copy()
    xyY_project[:, 2] *= 100.0
    XYZ = np.column_stack((
        xyY_project[:, 0] * xyY_project[:, 2] / xyY_project[:, 1],
        xyY_project[:, 2],
        (1.0 - xyY_project[:, 0] - xyY_project[:, 1]) * xyY_project[:, 2] / xyY_project[:, 1],
    ))

    actual = is_within_macadam_limits(XYZ, "A", tolerance=1e-7)
    expected = np.array([True, False, False, True])
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


def test_default_macadam_grid_loads_packaged_L1_H3_boundary():
    boundary = published_macadam_limits("D65")

    assert boundary.C_max.shape == (101, 121)
    np.testing.assert_allclose(boundary.L_values, np.arange(0.0, 101.0, 1.0))
    np.testing.assert_allclose(boundary.hue_values, np.arange(0.0, 361.0, 3.0))
    assert np.max(boundary.C_max) > 0.0


@pytest.mark.parametrize("illuminant", ["A", "C", "D65"])
def test_packaged_L1_H3_boundary_stays_inside_its_raw_mesh(illuminant):
    boundary = published_macadam_limits(illuminant)
    XYZ = boundary.to_XYZ().reshape(-1, 3)
    nonzero = boundary.C_max.reshape(-1) > 0.0

    assert np.all(
        published_is_within_macadam_limits(
            XYZ[nonzero],
            illuminant,
            tolerance=1e-7,
        )
    )


@pytest.mark.parametrize("illuminant", ["A", "C", "D65"])
def test_regular_macadam_boundary_stays_inside_static_mesh(illuminant):
    boundary = macadam_limits(
        illuminant,
        L_values=np.arange(0.0, 101.0, 10.0),
        hue_values=np.arange(0.0, 361.0, 30.0),
        C_upper=400.0,
        iterations=14,
    )
    XYZ = boundary.to_XYZ().reshape(-1, 3)
    nonzero = boundary.C_max.reshape(-1) > 0.0

    assert np.any(nonzero)
    assert np.all(
        is_within_macadam_limits(XYZ[nonzero], illuminant, tolerance=1e-7)
    )


def test_static_macadam_boundary_supports_C_upper_and_exact_subsets():
    kwargs = {
        "L_values": [50.0],
        "hue_values": np.arange(0.0, 361.0, 30.0),
    }
    capped = macadam_limits("D65", C_upper=20.0, iterations=14, **kwargs)
    full = macadam_limits("D65", C_upper=300.0, **kwargs)

    assert np.max(capped.C_max) <= 20.0
    assert np.max(full.C_max) > np.max(capped.C_max)
    with pytest.raises(ValueError, match="integer L_values"):
        published_macadam_limits("D65", L_values=[50.5], hue_values=[0.0])


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
