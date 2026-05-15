"""Tests for color.datasets.gamut_data — gamut boundary loaders."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets import describe
from color.datasets.gamut_data import get_gamut_data, list_gamut_data


class TestListGamutData:
    """Tests for list_gamut_data()."""

    def test_returns_list(self):
        result = list_gamut_data()
        assert isinstance(result, list)

    def test_contains_expected(self):
        result = list_gamut_data()
        assert "pointer" in result
        assert "pointer_raw" in result


class TestPointer:
    """Tests for Pointer's Calculations sheet loader."""

    def test_all_levels(self):
        data = get_gamut_data("pointer")
        assert isinstance(data, dict)
        # 8 L* levels × 37 hue angles = 296 rows
        assert len(data["L"]) == 296
        assert len(data["hab"]) == 296

    def test_columns(self):
        data = get_gamut_data("pointer")
        expected = {"L", "hab", "Xn", "Yn", "Zn", "C", "a", "b",
                    "X'", "Y'", "Z'", "x", "y", "u'", "v'"}
        assert expected == set(data.keys())

    def test_single_lstar(self):
        data = get_gamut_data("pointer", L=50)
        assert len(data["L"]) == 37
        assert np.all(data["L"] == 50.0)
        assert data["hab"][0] == 0.0
        assert data["hab"][-1] == 360.0

    def test_reference_white(self):
        data = get_gamut_data("pointer")
        # Illuminant C, SC 2° observer
        assert abs(data["Xn"][0] - 98.07) < 0.1
        assert abs(data["Yn"][0] - 100.0) < 0.01
        assert abs(data["Zn"][0] - 118.23) < 0.1

    def test_hue_range(self):
        data = get_gamut_data("pointer")
        hab = data["hab"]
        assert hab.min() == 0.0
        assert hab.max() == 360.0

    def test_metadata(self):
        entry = describe("gamut_data", "pointer")
        assert entry.metadata["quantity"] == "real_surface_gamut_boundary"
        assert entry.metadata["color_space"] == "CIELAB"
        assert entry.metadata["illuminant"] == "C"
        assert entry.metadata["observer_angle_deg"] == 2
        assert 50 in entry.metadata["lightness_levels"]
        assert entry.metadata["hue_count_per_lightness"] == 37


class TestPointerRaw:
    """Tests for pointer_raw (generic multi-sheet reader)."""

    def test_data_sheet(self):
        data = get_gamut_data("pointer_raw", sheet="Data")
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_specloc_sheet(self):
        data = get_gamut_data("pointer_raw", sheet="SpecLoc")
        assert len(data) > 0
        assert len(data[list(data.keys())[0]]) > 0

    def test_metadata(self):
        entry = describe("gamut_data", "pointer_raw")
        assert entry.read_options["sheet"] == "Data"
        assert entry.read_options["header"] == 8
        assert entry.read_options["coerce_numeric"] is True
        assert entry.metadata["quantity"] == "raw_pointer_gamut_workbook"
        assert "coerce_numeric" not in entry.metadata
        assert entry.metadata["coerces_non_numeric_to_nan"] is True
        assert "SpecLoc" in entry.metadata["sheets"]
