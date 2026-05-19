"""Tests for dominant wavelength, complementary wavelength and purity."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import (
    ChromaticityAnalysis,
    analyze_chromaticity,
    colorimetric_purity,
    complementary_wavelength,
    dominant_wavelength,
    excitation_purity,
    is_inside_chromaticity_locus,
    xy_from_dominant_wavelength_pc,
    xy_from_dominant_wavelength_pe,
)
from color.spectra import MultiSpectralDistribution, from_dataset


_WHITEPOINT = (0.3127, 0.3290)


def test_dominant_wavelength_red_region_colour_example():
    wavelength, xy_wl = dominant_wavelength(
        [0.54369557, 0.32107944],
        _WHITEPOINT,
    )

    assert wavelength == pytest.approx(616.0, abs=1.0)
    np.testing.assert_allclose(xy_wl, [0.6835, 0.3163], atol=5e-4)


def test_dominant_wavelength_non_spectral_colour_returns_negative_complement():
    wavelength, xy_wl = dominant_wavelength(
        [0.37605506, 0.24452225],
        _WHITEPOINT,
    )

    assert wavelength == pytest.approx(-509.0, abs=1.0)
    np.testing.assert_allclose(xy_wl, [0.4572, 0.1363], atol=5e-4)


def test_complementary_wavelength_reverse_direction():
    wavelength, xy_wl = complementary_wavelength(
        [0.37605506, 0.24452225],
        _WHITEPOINT,
    )

    assert wavelength == pytest.approx(509.0, abs=1.0)
    np.testing.assert_allclose(xy_wl, [0.0104, 0.7321], atol=5e-4)


def test_analyze_chromaticity_returns_complete_result():
    result = analyze_chromaticity([0.54369557, 0.32107944], _WHITEPOINT)

    assert isinstance(result, ChromaticityAnalysis)
    assert result.wavelength == pytest.approx(616.0, abs=1.0)
    assert result.complementary_wavelength == pytest.approx(491.9, abs=1.0)
    assert result.dominant_region == "spectral"
    assert result.complementary_region == "spectral"
    assert result.excitation_purity == pytest.approx(0.6228856, abs=5e-3)
    assert result.colorimetric_purity == pytest.approx(0.6135828, abs=5e-3)
    np.testing.assert_allclose(result.dominant_xy, [0.6835, 0.3163], atol=5e-4)
    np.testing.assert_allclose(result.complementary_xy, [0.0365, 0.3385], atol=5e-4)


def test_analyze_chromaticity_marks_non_spectral_colour():
    result = analyze_chromaticity([0.37605506, 0.24452225], _WHITEPOINT)

    assert result.wavelength == pytest.approx(-509.0, abs=1.0)
    assert result.complementary_wavelength == pytest.approx(509.0, abs=1.0)
    assert result.dominant_region == "purple"
    assert result.complementary_region == "spectral"
    np.testing.assert_allclose(result.dominant_xy, [0.4572, 0.1363], atol=5e-4)
    np.testing.assert_allclose(result.complementary_xy, [0.0104, 0.7321], atol=5e-4)


def test_analyze_chromaticity_marks_purple_complementary_region():
    result = analyze_chromaticity([0.36, 0.52], _WHITEPOINT)

    assert result.wavelength == pytest.approx(561.4, abs=1.0)
    assert result.complementary_wavelength == pytest.approx(-561.4, abs=1.0)
    assert result.dominant_region == "spectral"
    assert result.complementary_region == "purple"


def test_excitation_purity_colour_example():
    purity = excitation_purity([0.54369557, 0.32107944], _WHITEPOINT)

    assert purity == pytest.approx(0.6228856, abs=5e-3)


def test_colorimetric_purity_colour_example():
    purity = colorimetric_purity([0.54369557, 0.32107944], _WHITEPOINT)

    assert purity == pytest.approx(0.6135828, abs=5e-3)


def test_is_inside_chromaticity_locus_single_and_batch():
    inside = [0.3127, 0.3290]
    outside = [0.8, 0.8]
    locus = from_dataset(
        "standard_observers.chromaticity_coordinates",
        "cie1931_chro_1nm",
    )
    boundary_xy = np.array([
        locus.values[100, locus.labels.index("x")],
        locus.values[100, locus.labels.index("y")],
    ])

    assert is_inside_chromaticity_locus(inside) is True
    assert is_inside_chromaticity_locus(outside) is False
    assert is_inside_chromaticity_locus(boundary_xy) is True

    result = is_inside_chromaticity_locus(np.array([inside, outside, boundary_xy]))
    assert result.shape == (3,)
    np.testing.assert_array_equal(result, [True, False, True])


@pytest.mark.parametrize(
    "xy",
    [
        [0.54369557, 0.32107944],
        [0.36, 0.52],
        [0.37605506, 0.24452225],
    ],
)
def test_xy_from_dominant_wavelength_round_trips_forward_analysis(xy):
    xy = np.asarray(xy, dtype=np.float64)
    result = analyze_chromaticity(xy, _WHITEPOINT)

    reconstructed_pe = xy_from_dominant_wavelength_pe(
        result.wavelength,
        result.excitation_purity,
        _WHITEPOINT,
    )
    reconstructed_pc = xy_from_dominant_wavelength_pc(
        result.wavelength,
        result.colorimetric_purity,
        _WHITEPOINT,
    )

    np.testing.assert_allclose(reconstructed_pe, xy, atol=5e-12)
    np.testing.assert_allclose(reconstructed_pc, xy, atol=5e-12)


def test_xy_from_dominant_wavelength_zero_purity_returns_whitepoint():
    xy_pe = xy_from_dominant_wavelength_pe(616.0, 0.0, _WHITEPOINT)
    xy_pc = xy_from_dominant_wavelength_pc(616.0, 0.0, _WHITEPOINT)

    np.testing.assert_allclose(xy_pe, _WHITEPOINT)
    np.testing.assert_allclose(xy_pc, _WHITEPOINT)


def test_xy_from_dominant_wavelength_unit_purity_returns_boundary():
    wavelength = 616.0
    xy_pe = xy_from_dominant_wavelength_pe(wavelength, 1.0, _WHITEPOINT)
    xy_pc = xy_from_dominant_wavelength_pc(wavelength, 1.0, _WHITEPOINT)
    _dominant, xy_wl = dominant_wavelength([0.54369557, 0.32107944], _WHITEPOINT)

    np.testing.assert_allclose(xy_pe, xy_wl, atol=2e-3)
    np.testing.assert_allclose(xy_pc, xy_wl, atol=2e-3)


def test_xy_from_dominant_wavelength_batch_input_preserves_shape():
    xy = np.array([
        [0.54369557, 0.32107944],
        [0.36, 0.52],
        [0.37605506, 0.24452225],
    ])
    result = analyze_chromaticity(xy, _WHITEPOINT)

    reconstructed = xy_from_dominant_wavelength_pc(
        result.wavelength,
        result.colorimetric_purity,
        _WHITEPOINT,
    )

    assert reconstructed.shape == (3, 2)
    np.testing.assert_allclose(reconstructed, xy, atol=5e-12)


def test_xy_from_dominant_wavelength_rejects_invalid_values():
    with pytest.raises(ValueError, match="excitation_purity"):
        xy_from_dominant_wavelength_pe(616.0, 1.1, _WHITEPOINT)
    with pytest.raises(ValueError, match="colorimetric_purity"):
        xy_from_dominant_wavelength_pc(616.0, -0.1, _WHITEPOINT)
    with pytest.raises(ValueError, match="wavelength must be finite"):
        xy_from_dominant_wavelength_pe(np.nan, 0.5, _WHITEPOINT)
    with pytest.raises(ValueError, match="locus range"):
        xy_from_dominant_wavelength_pe(1000.0, 0.5, _WHITEPOINT)


def test_whitepoint_returns_nan_wavelength_and_zero_purity():
    wavelength, xy_wl = dominant_wavelength(_WHITEPOINT, _WHITEPOINT)
    result = analyze_chromaticity(_WHITEPOINT, _WHITEPOINT)

    assert np.isnan(wavelength)
    assert np.all(np.isnan(xy_wl))
    assert np.isnan(result.wavelength)
    assert np.isnan(result.complementary_wavelength)
    assert np.all(np.isnan(result.dominant_xy))
    assert np.all(np.isnan(result.complementary_xy))
    assert result.dominant_region == "undefined"
    assert result.complementary_region == "undefined"
    assert excitation_purity(_WHITEPOINT, _WHITEPOINT) == pytest.approx(0.0)
    assert colorimetric_purity(_WHITEPOINT, _WHITEPOINT) == pytest.approx(0.0)


def test_batch_xy_input_preserves_shape():
    xy = np.array([
        [0.54369557, 0.32107944],
        [0.36, 0.52],
        [0.18, 0.22],
        [0.16, 0.08],
        [0.37605506, 0.24452225],
    ])

    wavelength, xy_wl = dominant_wavelength(xy, _WHITEPOINT)
    complementary, xy_comp = complementary_wavelength(xy, _WHITEPOINT)
    result = analyze_chromaticity(xy, _WHITEPOINT)
    purity = excitation_purity(xy, _WHITEPOINT)

    assert wavelength.shape == (5,)
    assert complementary.shape == (5,)
    assert xy_wl.shape == (5, 2)
    assert xy_comp.shape == (5, 2)
    assert result.wavelength.shape == (5,)
    assert result.complementary_wavelength.shape == (5,)
    assert result.dominant_xy.shape == (5, 2)
    assert result.complementary_xy.shape == (5, 2)
    assert result.dominant_region.shape == (5,)
    assert result.complementary_region.shape == (5,)
    np.testing.assert_array_equal(
        result.dominant_region,
        ["spectral", "spectral", "spectral", "spectral", "purple"],
    )
    np.testing.assert_array_equal(
        result.complementary_region,
        ["spectral", "purple", "spectral", "spectral", "spectral"],
    )
    assert purity.shape == (5,)
    assert wavelength[0] > 0
    assert wavelength[-1] < 0
    assert np.all(np.isfinite(wavelength[:-1]))
    assert np.all(np.isfinite(complementary))
    assert np.all((purity >= 0.0) & (purity <= 1.0))


def test_custom_locus_matches_default_locus_name():
    locus = from_dataset(
        "standard_observers.chromaticity_coordinates",
        "cie1931_chro_1nm",
    )

    default = dominant_wavelength([0.54369557, 0.32107944], _WHITEPOINT)
    custom = dominant_wavelength([0.54369557, 0.32107944], _WHITEPOINT, locus)

    assert custom[0] == pytest.approx(default[0])
    np.testing.assert_allclose(custom[1], default[1])


def test_rejects_invalid_xy_shape():
    with pytest.raises(ValueError, match="2 values"):
        dominant_wavelength([0.3, 0.3, 0.4])


def test_rejects_locus_without_x_y_labels():
    locus = MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [
            [0.1, 0.2],
            [0.2, 0.3],
            [0.3, 0.4],
        ],
        ("u", "v"),
    )

    with pytest.raises(ValueError, match="'x' and 'y'"):
        dominant_wavelength([0.3, 0.3], _WHITEPOINT, locus)
