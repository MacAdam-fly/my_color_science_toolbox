"""Tests for display-gamut coverage metrics."""

from __future__ import annotations

import numpy as np
import pytest

from color.constants import D50_XYZ, D65_XYZ
from color.colorimetry import XYZ_to_xy
from color.gamut import (
    DisplayPrimaries,
    compute_LCH_gamut_boundary,
    lab_gamut_coverage,
    lab_gamut_volume,
    xy_gamut_coverage,
    xy_gamut_coverage_from_xy,
)
from color.gamut.coverage import (
    lab_gamut_overlap_volume,
    xy_gamut_area,
    xy_gamut_area_from_xy,
    xy_gamut_intersection_area,
    xy_gamut_intersection_area_from_xy,
)


def _boundary(name, *, L_step=10.0, hue_step=10.0, C_upper=260.0):
    return compute_LCH_gamut_boundary(
        name,
        whitepoint_XYZ=D65_XYZ,
        L_values=np.arange(0.0, 101.0, L_step),
        hue_values=np.arange(0.0, 361.0, hue_step),
        C_upper=C_upper,
        iterations=8,
    )


def test_xy_gamut_area_and_self_coverage():
    area = xy_gamut_area("sRGB")
    assert area > 0
    np.testing.assert_allclose(xy_gamut_intersection_area("sRGB", "sRGB"), area)
    np.testing.assert_allclose(xy_gamut_coverage("sRGB", "sRGB"), 1.0)


def test_xy_gamut_coverage_is_directional():
    rec2020_covers_srgb = xy_gamut_coverage("Rec.2020", "sRGB")
    srgb_covers_rec2020 = xy_gamut_coverage("sRGB", "Rec.2020")

    assert rec2020_covers_srgb > 0.99
    assert 0.0 < srgb_covers_rec2020 < 1.0


def test_xy_gamut_coverage_supports_multi_primary_display():
    rgbc = DisplayPrimaries(
        [
            [75.35530926, 30.53272055, 0.8324195],
            [3.43647492, 35.46933042, 6.55021212],
            [15.06919248, 3.99794903, 83.44437197],
            [1.18187787, 30.0, 18.06303349],
        ],
        names=("R", "G", "B", "C"),
    )

    assert xy_gamut_area(rgbc) > 0
    coverage = xy_gamut_coverage(rgbc, "sRGB")
    assert 0.0 < coverage <= 1.0


def test_xy_gamut_coverage_from_xy_matches_xyz_primary_path():
    srgb_xy = XYZ_to_xy(DisplayPrimaries.from_RGB_colourspace("sRGB").primaries_XYZ)
    rec2020_xy = XYZ_to_xy(DisplayPrimaries.from_RGB_colourspace("Rec.2020").primaries_XYZ)

    np.testing.assert_allclose(xy_gamut_area_from_xy(srgb_xy), xy_gamut_area("sRGB"))
    np.testing.assert_allclose(
        xy_gamut_intersection_area_from_xy(srgb_xy, rec2020_xy),
        xy_gamut_intersection_area("sRGB", "Rec.2020"),
    )
    np.testing.assert_allclose(
        xy_gamut_coverage_from_xy(srgb_xy, rec2020_xy),
        xy_gamut_coverage("sRGB", "Rec.2020"),
    )


def test_xy_gamut_coverage_from_xy_rejects_invalid_xy():
    with pytest.raises(ValueError, match="xy"):
        xy_gamut_coverage_from_xy([[0.1, 0.2, 0.3]], [[0.1, 0.2], [0.3, 0.4], [0.5, 0.2]])
    with pytest.raises(ValueError, match="at least three"):
        xy_gamut_area_from_xy([[0.1, 0.2], [0.3, 0.4]])


def test_lab_gamut_volume_overlap_and_self_coverage():
    srgb = _boundary("sRGB", C_upper=180.0)

    volume = lab_gamut_volume(srgb)
    overlap = lab_gamut_overlap_volume(srgb, srgb)

    assert volume > 0
    np.testing.assert_allclose(overlap, volume)
    np.testing.assert_allclose(lab_gamut_coverage(srgb, srgb), 1.0)


def test_lab_gamut_coverage_is_directional():
    srgb = _boundary("sRGB", C_upper=180.0)
    rec2020 = _boundary("Rec.2020", C_upper=260.0)

    rec2020_covers_srgb = lab_gamut_coverage(rec2020, srgb)
    srgb_covers_rec2020 = lab_gamut_coverage(srgb, rec2020)
    overlap = lab_gamut_overlap_volume(srgb, rec2020)

    assert rec2020_covers_srgb > 0.95
    assert 0.0 < srgb_covers_rec2020 < 1.0
    assert overlap <= lab_gamut_volume(srgb) * 1.000001
    assert overlap <= lab_gamut_volume(rec2020) * 1.000001


def test_lab_gamut_coverage_warns_when_grids_differ():
    srgb_reference = _boundary("sRGB", L_step=10.0, hue_step=10.0, C_upper=180.0)
    srgb_test = _boundary("sRGB", L_step=20.0, hue_step=20.0, C_upper=180.0)

    with pytest.warns(UserWarning, match="grids differ"):
        coverage = lab_gamut_coverage(srgb_test, srgb_reference)

    assert np.isfinite(coverage)
    assert 0.0 < coverage <= 1.05


def test_lab_gamut_coverage_warns_when_whitepoints_differ():
    srgb = _boundary("sRGB", C_upper=180.0)
    d50 = compute_LCH_gamut_boundary(
        "sRGB",
        whitepoint_XYZ=D50_XYZ,
        L_values=np.arange(0.0, 101.0, 10.0),
        hue_values=np.arange(0.0, 361.0, 10.0),
        C_upper=180.0,
        iterations=8,
    )

    with pytest.warns(UserWarning, match="whitepoint_XYZ"):
        coverage = lab_gamut_coverage(srgb, d50)

    assert np.isfinite(coverage)


def test_lab_gamut_coverage_rejects_non_boundary_inputs():
    with pytest.raises(TypeError, match="GamutBoundary"):
        lab_gamut_coverage("sRGB", "Rec.2020")  # type: ignore[arg-type]
