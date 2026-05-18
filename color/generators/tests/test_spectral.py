"""Tests for ideal and LED generators."""

from __future__ import annotations

import numpy as np
import pytest

from color.generators import generate
from color.generators.ideal import (
    constant_spd,
    equal_energy_spd,
    gaussian_spd,
    generate_ideal,
    list_ideal_generators,
    zero_spd,
)
from color.generators.leds import (
    list_led_generators,
    multi_led_spd,
    single_led_spd,
)


class TestListIdealGenerators:
    """Tests for list_ideal_generators()."""

    def test_contains_expected_names(self):
        result = list_ideal_generators()
        assert "constant" in result
        assert "equal_energy" in result
        assert "gaussian" in result


class TestListLedGenerators:
    """Tests for list_led_generators()."""

    def test_contains_expected_names(self):
        result = list_led_generators()
        assert "single" in result
        assert "multi" in result


class TestConstant:
    """Tests for constant spectral generators."""

    def test_constant(self):
        wavelengths = np.array([400.0, 500.0, 600.0])
        data = constant_spd(wavelength_nm=wavelengths, value=2.5)
        np.testing.assert_array_equal(data["wavelength"], wavelengths)
        np.testing.assert_array_equal(data["spd"], [2.5, 2.5, 2.5])

    def test_zero_and_equal_energy(self):
        wavelengths = np.array([400.0, 500.0, 600.0])
        np.testing.assert_array_equal(zero_spd(wavelength_nm=wavelengths)["spd"], [0.0, 0.0, 0.0])
        np.testing.assert_array_equal(equal_energy_spd(wavelength_nm=wavelengths)["spd"], [1.0, 1.0, 1.0])

    def test_custom_column(self):
        data = constant_spd(wavelength_nm=np.array([400.0]), value=1.0, column="value")
        assert "value" in data
        assert "spd" not in data

    def test_registry_generate(self):
        data = generate("ideal", "constant", value=3.0)
        assert data["wavelength"][0] == 360
        assert np.all(data["spd"] == 3.0)

    def test_convenience_generate(self):
        data = generate_ideal("equal_energy")
        assert np.all(data["spd"] == 1.0)


class TestGaussian:
    """Tests for Gaussian spectral generator."""

    def test_normal_method_peaks_at_peak_wavelength(self):
        wavelengths = np.array([530.0, 555.0, 580.0])
        data = gaussian_spd(wavelength_nm=wavelengths, peak_wavelength=555.0, width=25.0)
        assert data["spd"][1] == pytest.approx(1.0)
        assert data["spd"][0] == pytest.approx(np.exp(-0.5))
        assert data["spd"][2] == pytest.approx(data["spd"][0])

    def test_fwhm_method_half_width(self):
        wavelengths = np.array([530.0, 555.0, 580.0])
        data = gaussian_spd(
            wavelength_nm=wavelengths,
            peak_wavelength=555.0,
            width=50.0,
            method="fwhm",
        )
        assert data["spd"][1] == pytest.approx(1.0)
        assert data["spd"][0] == pytest.approx(0.5)
        assert data["spd"][2] == pytest.approx(0.5)

    def test_amplitude(self):
        data = gaussian_spd(
            wavelength_nm=np.array([555.0]),
            peak_wavelength=555.0,
            width=25.0,
            amplitude=2.0,
        )
        assert data["spd"][0] == pytest.approx(2.0)

    def test_invalid_width_raises(self):
        with pytest.raises(ValueError, match="width must be positive"):
            gaussian_spd(width=0.0)

    def test_invalid_method_raises(self):
        with pytest.raises(ValueError, match="method must be"):
            gaussian_spd(method="unknown")


class TestLed:
    """Tests for LED spectral generators."""

    def test_single_led_peaks_at_peak_wavelength(self):
        wavelengths = np.array([530.0, 555.0, 580.0])
        data = single_led_spd(
            wavelength_nm=wavelengths,
            peak_wavelength=555.0,
            half_spectral_width=25.0,
        )
        assert data["spd"][1] == pytest.approx(1.0)
        assert data["spd"][0] == pytest.approx(data["spd"][2])
        assert data["spd"][0] < data["spd"][1]

    def test_single_led_amplitude(self):
        data = single_led_spd(
            wavelength_nm=np.array([555.0]),
            peak_wavelength=555.0,
            half_spectral_width=25.0,
            amplitude=2.0,
        )
        assert data["spd"][0] == pytest.approx(2.0)

    def test_multi_led_sums_components(self):
        wavelengths = np.array([450.0, 550.0, 650.0])
        data = multi_led_spd(
            wavelength_nm=wavelengths,
            peak_wavelengths=(450.0, 650.0),
            half_spectral_widths=(20.0, 20.0),
            peak_power_ratios=(1.0, 2.0),
        )
        assert data["spd"][0] > 0.9
        assert data["spd"][2] > 1.9
        assert data["spd"][1] < data["spd"][0]

    def test_invalid_half_spectral_width_raises(self):
        with pytest.raises(ValueError, match="half_spectral_width"):
            single_led_spd(half_spectral_width=0.0)

    def test_invalid_multi_led_inputs_raise(self):
        with pytest.raises(ValueError, match="peak_wavelengths"):
            multi_led_spd(peak_wavelengths=())


def test_rejects_invalid_wavelengths():
    with pytest.raises(ValueError, match="one-dimensional"):
        gaussian_spd(wavelength_nm=np.array([[400.0, 500.0]]))
