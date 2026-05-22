"""Tests for blackbody and illuminant generators."""

from __future__ import annotations

import numpy as np
import pytest

from color.generators import generate
from color.generators.blackbody import (
    blackbody_spd,
    generate_blackbody,
    list_blackbody_generators,
)
from color.generators.illuminants import (
    daylight_spd,
    generate_illuminant,
    illuminant_a_spd,
    list_illuminant_generators,
)


class TestListBlackbodyGenerators:
    """Tests for list_blackbody_generators()."""

    def test_contains_expected_names(self):
        assert "blackbody_spd" in list_blackbody_generators()


class TestListIlluminantGenerators:
    """Tests for list_illuminant_generators()."""

    def test_contains_expected_names(self):
        result = list_illuminant_generators()
        assert "A" in result
        assert "cie_d_daylight" in result


class TestBlackbody:
    """Tests for Planck blackbody radiation."""

    def test_basic(self):
        data = blackbody_spd(temperature=6500)
        assert "wavelength" in data
        assert "radiance" in data

    def test_registry_generate(self):
        data = generate("blackbody", "blackbody_spd", temperature=6500)
        assert "radiance" in data
        assert "spd" not in data

    def test_convenience_generate(self):
        data = generate_blackbody(temperature=6500)
        assert "radiance" in data

    def test_different_temperatures(self):
        for temperature in [1000, 3000, 6500, 10000]:
            data = blackbody_spd(temperature=temperature)
            assert len(data["wavelength"]) > 0
            assert np.all(data["radiance"] > 0)

    def test_peak_shifts_with_temperature(self):
        d3k = blackbody_spd(temperature=3000)
        d10k = blackbody_spd(temperature=10000)
        peak_3k = d3k["wavelength"][np.argmax(d3k["radiance"])]
        peak_10k = d10k["wavelength"][np.argmax(d10k["radiance"])]
        assert peak_10k < peak_3k

    def test_negative_temperature_raises(self):
        with pytest.raises(ValueError, match="temperature must be positive"):
            blackbody_spd(temperature=-100)

    def test_custom_wavelength(self):
        wl = np.arange(400, 701, 10.0)
        data = blackbody_spd(temperature=6500, wavelength_nm=wl)
        np.testing.assert_array_equal(data["wavelength"], wl)


class TestIlluminantA:
    """Tests for CIE Standard Illuminant A."""

    def test_basic(self):
        data = illuminant_a_spd()
        assert "wavelength" in data
        assert "spd" in data

    def test_registry_generate(self):
        data = generate("illuminants", "A")
        assert "wavelength" in data
        assert "spd" in data

    def test_convenience_generate(self):
        data = generate_illuminant("A")
        assert "spd" in data

    def test_normalised_at_560_nm(self):
        data = illuminant_a_spd(wavelength_nm=np.array([560.0]))
        assert data["spd"][0] == pytest.approx(100.0)

    def test_custom_wavelength(self):
        wl = np.arange(400, 701, 10.0)
        data = illuminant_a_spd(wavelength_nm=wl)
        np.testing.assert_array_equal(data["wavelength"], wl)


class TestDaylight:
    """Tests for CIE D-series daylight."""

    def test_basic(self):
        data = daylight_spd(cct=6500)
        assert "wavelength" in data
        assert "spd" in data

    def test_registry_generate(self):
        data = generate("illuminants", "cie_d_daylight", cct=6500)
        assert "wavelength" in data
        assert "spd" in data

    def test_different_ccts(self):
        for cct in [4000, 5000, 6500, 10000, 25000]:
            data = daylight_spd(cct=cct)
            assert len(data["wavelength"]) > 0
            assert np.all(data["spd"] >= 0)

    def test_cct_out_of_range_raises(self):
        with pytest.raises(ValueError, match="4000.*25000"):
            daylight_spd(cct=3000)

    def test_cct_too_high_raises(self):
        with pytest.raises(ValueError):
            daylight_spd(cct=30000)

    def test_default_wavelength(self):
        data = daylight_spd(cct=5000)
        assert data["wavelength"][0] == 300
        assert data["wavelength"][-1] == 830
