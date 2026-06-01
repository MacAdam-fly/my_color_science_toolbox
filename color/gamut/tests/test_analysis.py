"""Tests for high-level gamut analysis."""

from __future__ import annotations

import numpy as np
import pytest

from color.gamut import (
    DisplayPrimaries,
    GamutAnalysis,
    analyze_gamut,
    compute_LCH_gamut_boundary,
    lab_gamut_volume,
    pointer_gamut,
    xy_gamut_area_from_xy,
)


def _small_grid_kwargs():
    return {
        "L_values": np.arange(0.0, 101.0, 25.0),
        "hue_values": np.arange(0.0, 361.0, 45.0),
        "C_upper": 240.0,
        "iterations": 5,
    }


def _assert_finite_analysis(analysis: GamutAnalysis) -> None:
    values = [
        analysis.xy_area,
        analysis.xy_coverage_rec2020,
        analysis.xy_coverage_pointer,
        analysis.xy_coverage_macadam_d65,
        analysis.lab_volume,
        analysis.projected_ab_area,
        analysis.ring_area,
        analysis.volume_coverage_rec2020,
        analysis.volume_coverage_pointer,
        analysis.volume_coverage_macadam_d65,
    ]
    assert np.all(np.isfinite(values))
    assert np.all(np.asarray(values) >= 0)


def test_analyze_gamut_from_rgb_name():
    kwargs = _small_grid_kwargs()

    with pytest.warns(UserWarning):
        analysis = analyze_gamut("sRGB", **kwargs)

    assert isinstance(analysis, GamutAnalysis)
    assert analysis.name == "sRGB"
    _assert_finite_analysis(analysis)
    np.testing.assert_allclose(
        analysis.xy_area,
        xy_gamut_area_from_xy(analysis.boundary.xy_boundary()),
    )
    np.testing.assert_allclose(analysis.lab_volume, lab_gamut_volume(analysis.boundary))
    assert analysis.warnings


def test_analyze_gamut_from_display_primaries():
    kwargs = _small_grid_kwargs()
    primaries = DisplayPrimaries.from_RGB_colourspace("sRGB")

    with pytest.warns(UserWarning):
        analysis = analyze_gamut(primaries, name="custom sRGB", **kwargs)

    assert analysis.name == "custom sRGB"
    _assert_finite_analysis(analysis)


def test_analyze_gamut_from_existing_boundary_does_not_rebuild_input():
    kwargs = _small_grid_kwargs()
    boundary = compute_LCH_gamut_boundary("sRGB", **kwargs)

    with pytest.warns(UserWarning):
        analysis = analyze_gamut(boundary, **kwargs)

    assert analysis.boundary is boundary
    _assert_finite_analysis(analysis)


def test_analyze_gamut_accepts_reference_boundaries():
    kwargs = _small_grid_kwargs()
    boundary = compute_LCH_gamut_boundary("sRGB", **kwargs)
    rec2020 = compute_LCH_gamut_boundary("Rec.2020", **kwargs)
    pointer = pointer_gamut()

    with pytest.warns(UserWarning):
        analysis = analyze_gamut(
            boundary,
            rec2020_boundary=rec2020,
            pointer_boundary=pointer,
            macadam_d65_boundary=boundary,
            **kwargs,
        )

    assert analysis.boundary is boundary
    _assert_finite_analysis(analysis)
    assert any("whitepoint_XYZ" in message for message in analysis.warnings)
