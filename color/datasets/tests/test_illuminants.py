"""Tests for color.datasets.illuminants static loaders."""

from __future__ import annotations

import numpy as np

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
        assert "fluorescents" in result
        assert "blackbody" not in result
        assert "daylight" not in result

    def test_sorted(self):
        result = list_illuminants()
        assert result == sorted(result)


class TestGetIlluminantA:
    """Tests for CIE Illuminant A."""

    def test_returns_dict(self):
        data = get_illuminant("A")
        assert isinstance(data, dict)

    def test_has_wavelength(self):
        data = get_illuminant("A")
        assert "wavelength" in data
        assert "spd" in data
        assert isinstance(data["wavelength"], np.ndarray)

    def test_wavelength_range(self):
        data = get_illuminant("A")
        assert data["wavelength"][0] == 300
        assert data["wavelength"][-1] == 830

    def test_values_positive(self):
        data = get_illuminant("A")
        assert np.all(data["spd"] > 0)


class TestGetIlluminantD65:
    """Tests for CIE Illuminant D65."""

    def test_returns_dict_with_wavelength(self):
        data = get_illuminant("D65")
        assert "wavelength" in data
        assert "spd" in data

    def test_wavelength_range(self):
        data = get_illuminant("D65")
        assert data["wavelength"][0] >= 290
        assert data["wavelength"][-1] <= 840

    def test_spd_values_non_negative(self):
        data = get_illuminant("D65")
        assert np.all(data["spd"] >= 0)


class TestIlluminantFieldNames:
    """Tests for consistent illuminant field names."""

    def test_relative_spd_datasets_use_spd_key(self):
        for name in ["A", "D65"]:
            data = get_illuminant(name)
            assert "wavelength" in data
            assert "spd" in data
            assert "value" not in data


class TestGetIlluminantFluorescents:
    """Tests for fluorescent lamp data."""

    def test_has_f1_to_f12(self):
        data = get_illuminant("fluorescents")
        for i in range(1, 13):
            assert f"F{i}" in data, f"Missing F{i}"

    def test_wavelength_present(self):
        data = get_illuminant("fluorescents")
        assert "wavelength" in data
