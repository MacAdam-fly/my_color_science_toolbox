"""Tests for color.datasets.color_cards — color checker loaders."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets import describe
from color.datasets.color_cards import (
    BCRA_TILE_NAMES,
    MACBETH_PATCH_NAMES,
    get_color_card,
    list_color_cards,
)


class TestListColorCards:
    """Tests for list_color_cards()."""

    def test_returns_list(self):
        result = list_color_cards()
        assert isinstance(result, list)

    def test_contains_expected(self):
        result = list_color_cards()
        assert "macbeth" in result
        assert "pmc" in result
        assert "bcra" in result


class TestMacbeth:
    """Tests for the Macbeth ColorChecker."""

    def test_returns_dict(self):
        data = get_color_card("macbeth")
        assert isinstance(data, dict)

    def test_has_all_patches(self):
        data = get_color_card("macbeth")
        for name in MACBETH_PATCH_NAMES:
            assert name in data, f"Missing patch: {name}"

    def test_wavelength_range(self):
        data = get_color_card("macbeth")
        assert data["wavelength"][0] == 380
        assert data["wavelength"][-1] == 780

    def test_reflectance_in_range(self):
        data = get_color_card("macbeth")
        for name in MACBETH_PATCH_NAMES:
            assert np.all(data[name] >= 0), f"{name} has negative reflectance"
            assert np.all(data[name] <= 1), f"{name} has reflectance > 1"

    def test_24_patches(self):
        data = get_color_card("macbeth")
        patch_keys = [k for k in data if k != "wavelength"]
        assert len(patch_keys) == 24

    def test_black_darkest(self):
        data = get_color_card("macbeth")
        black_mean = np.mean(data["Black"])
        white_mean = np.mean(data["White"])
        assert black_mean < white_mean

    def test_metadata(self):
        entry = describe("color_cards", "macbeth")
        assert entry.computed is True
        assert entry.compute_fn is not None
        assert "loader" not in entry.metadata
        assert entry.metadata["quantity"] == "spectral_reflectance"
        assert entry.metadata["patch_count"] == 24
        assert entry.metadata["wavelength_unit"] == "nm"
        assert entry.metadata["wavelength_range_nm"] == (380, 780)
        assert entry.metadata["sampling_interval_nm"] == 5


class TestPMC:
    """Tests for the PMC chart."""

    def test_returns_dict(self):
        data = get_color_card("pmc")
        assert isinstance(data, dict)

    def test_has_wavelength(self):
        data = get_color_card("pmc")
        assert "wavelength" in data

    def test_has_neutral_patches(self):
        data = get_color_card("pmc")
        assert "White" in data
        assert "Black" in data


class TestBCRA:
    """Tests for BCRA calibration tiles."""

    def test_returns_dict(self):
        data = get_color_card("bcra")
        assert isinstance(data, dict)

    def test_has_all_tiles(self):
        data = get_color_card("bcra")
        for name in BCRA_TILE_NAMES:
            assert name in data, f"Missing tile: {name}"

    def test_12_tiles(self):
        data = get_color_card("bcra")
        tile_keys = [k for k in data if k != "wavelength"]
        assert len(tile_keys) == 12

    def test_metadata(self):
        entry = describe("color_cards", "bcra")
        assert entry.computed is True
        assert entry.compute_fn is not None
        assert "loader" not in entry.metadata
        assert entry.metadata["quantity"] == "spectral_reflectance"
        assert entry.metadata["patch_count"] == 12
        assert entry.metadata["wavelength_range_nm"] == (380, 730)
