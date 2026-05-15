"""Tests for color.datasets.illuminants — illuminant loaders and computed datasets."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets.illuminants import get_illuminant, list_illuminants


class TestListIlluminants:
    """Tests for list_illuminants()."""

    def test_returns_list(self):
        result = list_illuminants()
        assert isinstance(result, list)

    def test_contains_expected_names(self):
        result = list_illuminants()
        assert "A" in result
        assert "D65" in result
        assert "blackbody" in result
        assert "daylight" in result
        assert "fluorescents" in result

    def test_sorted(self):
        result = list_illuminants()
        assert result == sorted(result)


class TestGetIlluminantA:
    """Tests for CIE Illuminant A (file-based)."""

    def test_returns_dict(self):
        data = get_illuminant("A")
        assert isinstance(data, dict)

    def test_has_wavelength(self):
        data = get_illuminant("A")
        assert "wavelength" in data
        assert isinstance(data["wavelength"], np.ndarray)

    def test_wavelength_range(self):
        data = get_illuminant("A")
        assert data["wavelength"][0] == 300
        assert data["wavelength"][-1] == 830

    def test_values_positive(self):
        data = get_illuminant("A")
        spd_key = [k for k in data if k != "wavelength"][0]
        assert np.all(data[spd_key] > 0)


class TestGetIlluminantD65:
    """Tests for CIE Illuminant D65 (file-based)."""

    def test_returns_dict_with_wavelength(self):
        data = get_illuminant("D65")
        assert "wavelength" in data

    def test_wavelength_range(self):
        data = get_illuminant("D65")
        assert data["wavelength"][0] >= 290
        assert data["wavelength"][-1] <= 840


class TestGetIlluminantFluorescents:
    """Tests for fluorescent lamp data (file-based)."""

    def test_has_f1_to_f12(self):
        data = get_illuminant("fluorescents")
        for i in range(1, 13):
            assert f"F{i}" in data, f"Missing F{i}"

    def test_wavelength_present(self):
        data = get_illuminant("fluorescents")
        assert "wavelength" in data


class TestBlackbody:
    """Tests for computed blackbody radiation (Planck's law)."""

    def test_basic(self):
        data = get_illuminant("blackbody", temperature=6500)
        assert "wavelength" in data
        assert "radiance" in data

    def test_different_temperatures(self):
        for T in [1000, 3000, 6500, 10000]:
            data = get_illuminant("blackbody", temperature=T)
            assert len(data["wavelength"]) > 0
            assert np.all(data["radiance"] > 0)

    def test_peak_shifts_with_temperature(self):
        """Wien's displacement law: peak shifts left as T increases."""
        d3k = get_illuminant("blackbody", temperature=3000)
        d10k = get_illuminant("blackbody", temperature=10000)
        peak_3k = d3k["wavelength"][np.argmax(d3k["radiance"])]
        peak_10k = d10k["wavelength"][np.argmax(d10k["radiance"])]
        assert peak_10k < peak_3k

    def test_negative_temperature_raises(self):
        with pytest.raises(AssertionError):
            get_illuminant("blackbody", temperature=-100)

    def test_custom_wavelength(self):
        wl = np.arange(400, 701, 10.0)
        data = get_illuminant("blackbody", temperature=6500, wavelength_nm=wl)
        np.testing.assert_array_equal(data["wavelength"], wl)


class TestDaylight:
    """Tests for computed CIE D-series daylight."""

    def test_basic(self):
        data = get_illuminant("daylight", cct=6500)
        assert "wavelength" in data
        assert "spd" in data

    def test_different_ccts(self):
        for cct in [4000, 5000, 6500, 10000, 25000]:
            data = get_illuminant("daylight", cct=cct)
            assert len(data["wavelength"]) > 0
            assert np.all(data["spd"] >= 0)

    def test_cct_out_of_range_raises(self):
        with pytest.raises(ValueError, match="4000.*25000"):
            get_illuminant("daylight", cct=3000)

    def test_cct_too_high_raises(self):
        with pytest.raises(ValueError):
            get_illuminant("daylight", cct=30000)

    def test_default_wavelength(self):
        data = get_illuminant("daylight", cct=5000)
        assert data["wavelength"][0] == 300
        assert data["wavelength"][-1] == 830

