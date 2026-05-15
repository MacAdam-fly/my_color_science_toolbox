"""Tests for color.datasets.standard_observers — auto-discovered CVRL data."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets import describe
from color.datasets.standard_observers import (
    describe_standard_observer,
    get_standard_observer,
    list_standard_observer_categories,
    list_standard_observers,
)


class TestListCategories:
    """Tests for list_standard_observer_categories()."""

    def test_returns_six_categories(self):
        cats = list_standard_observer_categories()
        assert len(cats) == 6

    def test_expected_names(self):
        cats = list_standard_observer_categories()
        assert "cmfs" in cats
        assert "cone_fundamentals" in cats
        assert "luminous_efficiency" in cats
        assert "prereceptoral_filters" in cats
        assert "chromaticity_coordinates" in cats
        assert "photopigments" in cats


class TestListObservers:
    """Tests for list_standard_observers()."""

    def test_cmfs_count(self):
        items = list_standard_observers("cmfs")
        assert len(items) == 15

    def test_cone_fundamentals_count(self):
        items = list_standard_observers("cone_fundamentals")
        assert len(items) == 27

    def test_luminous_efficiency_count(self):
        items = list_standard_observers("luminous_efficiency")
        assert len(items) == 29

    def test_returns_sorted(self):
        items = list_standard_observers("cmfs")
        assert items == sorted(items)


class TestCIE1931CMFs:
    """Tests for CIE 1931 2° XYZ colour matching functions."""

    def test_returns_dict(self):
        data = get_standard_observer("cmfs", "cie1931_xyz_1nm")
        assert isinstance(data, dict)

    def test_has_xyz_columns(self):
        data = get_standard_observer("cmfs", "cie1931_xyz_1nm")
        assert "X" in data
        assert "Y" in data
        assert "Z" in data

    def test_wavelength_range(self):
        data = get_standard_observer("cmfs", "cie1931_xyz_1nm")
        assert data["wavelength"][0] == 360
        assert data["wavelength"][-1] == 830

    def test_values_non_negative(self):
        data = get_standard_observer("cmfs", "cie1931_xyz_1nm")
        assert np.all(data["X"] >= 0)
        assert np.all(data["Y"] >= 0)
        assert np.all(data["Z"] >= 0)

    def test_5nm_version(self):
        data = get_standard_observer("cmfs", "cie1931_xyz_5nm")
        assert data["wavelength"][0] == 360
        assert len(data["wavelength"]) < 500  # fewer points than 1nm


class TestCIE1964CMFs:
    """Tests for CIE 1964 10° XYZ colour matching functions."""

    def test_has_xyz(self):
        data = get_standard_observer("cmfs", "cie1964_xyz_1nm")
        assert "X" in data
        assert "Y" in data
        assert "Z" in data


class TestConeFundamentals:
    """Tests for cone fundamentals (CIE 2006 = Stockman & Sharpe)."""

    def test_cie2006_lms2_logE(self):
        data = get_standard_observer("cone_fundamentals", "cie2006_lms2_logE_5nm")
        assert "l" in data
        assert "m" in data
        assert "s" in data

    def test_cie2006_lms10_linE(self):
        data = get_standard_observer("cone_fundamentals", "cie2006_lms10_linE_5nm")
        assert "l" in data
        assert "m" in data
        assert "s" in data


class TestLuminousEfficiency:
    """Tests for luminous efficiency functions."""

    def test_cie2008_v2(self):
        data = get_standard_observer("luminous_efficiency", "cie2008_v2_linE_1nm")
        assert "V" in data
        assert np.all(data["V"] >= 0)

    def test_scotopic(self):
        data = get_standard_observer("luminous_efficiency", "scotopic_v_1nm")
        assert "V_prime" in data


class TestPrereceptoralFilters:
    """Tests for macular pigment and lens density."""

    def test_macular(self):
        data = get_standard_observer("prereceptoral_filters", "macular_ss_5nm")
        assert "optical_density" in data

    def test_lens(self):
        data = get_standard_observer("prereceptoral_filters", "lens_ss_5nm")
        assert "optical_density" in data


class TestChromaticityCoordinates:
    """Tests for chromaticity coordinate data."""

    def test_cie31_xy(self):
        data = get_standard_observer("chromaticity_coordinates", "cie1931_chro_5nm")
        assert "x" in data
        assert "y" in data

    def test_macLeod_boynton(self):
        data = get_standard_observer("chromaticity_coordinates", "mb2_chro2_5nm")
        assert "l" in data
        assert "s" in data
        assert "B" in data


class TestPhotopigments:
    """Tests for photopigment absorption spectra."""

    def test_sucrodsh(self):
        data = get_standard_observer("photopigments", "sucrodsh")
        assert "absorption" in data

    def test_succones(self):
        data = get_standard_observer("photopigments", "succones")
        assert "l" in data
        assert "m" in data
        assert "s" in data


class TestDescribeObserver:
    """Tests for describe_standard_observer()."""

    def test_known_category(self):
        desc = describe_standard_observer("cmfs")
        assert "Matching" in desc

    def test_unknown_category_raises(self):
        with pytest.raises(KeyError):
            describe_standard_observer("unknown")


class TestObserverMetadata:
    """Tests for registered standard-observer metadata."""

    def test_cmf_metadata(self):
        entry = describe("standard_observers.cmfs", "cie1931_xyz_1nm")
        assert entry.read_options["header"] is True
        assert "header" not in entry.metadata
        assert entry.metadata["quantity"] == "colour_matching_function"
        assert entry.metadata["color_space"] == "XYZ"
        assert entry.metadata["wavelength_unit"] == "nm"
        assert entry.metadata["value_unit"] == "relative"
        assert entry.metadata["sampling_interval_nm"] == 1.0
        assert entry.metadata["observer_angle_deg"] == 2

    def test_cone_fundamental_metadata(self):
        entry = describe(
            "standard_observers.cone_fundamentals",
            "cie2006_lms10_logE_5nm",
        )
        assert entry.metadata["quantity"] == "cone_fundamental"
        assert entry.metadata["energy_basis"] == "energy"
        assert entry.metadata["scale"] == "logarithmic"
        assert entry.metadata["observer_angle_deg"] == 10

    def test_luminous_efficiency_metadata(self):
        entry = describe("standard_observers.luminous_efficiency", "scotopic_v_1nm")
        assert entry.metadata["quantity"] == "luminous_efficiency"
        assert entry.metadata["vision_regime"] == "scotopic"
        assert entry.metadata["sampling_interval_nm"] == 1.0


class TestCategoryAliases:
    """Tests for category alias resolution."""

    def test_cone_alias(self):
        data = get_standard_observer("cone", "cie2006_lms2_logE_5nm")
        assert "l" in data

    def test_lms_alias(self):
        data = get_standard_observer("lms", "cie2006_lms2_logE_5nm")
        assert "l" in data

    def test_xyz_alias(self):
        data = get_standard_observer("xyz", "cie1931_xyz_1nm")
        assert "X" in data

    def test_luminous_alias(self):
        data = get_standard_observer("luminous", "cie2008_v2_linE_1nm")
        assert "V" in data

    def test_filter_alias(self):
        data = get_standard_observer("filter", "macular_ss_5nm")
        assert "optical_density" in data

    def test_chroma_alias(self):
        data = get_standard_observer("chroma", "cie1931_chro_5nm")
        assert "x" in data

    def test_pigment_alias(self):
        data = get_standard_observer("pigment", "succones")
        assert "l" in data

    def test_list_with_alias(self):
        items = list_standard_observers("cone")
        assert len(items) == 27

    def test_describe_with_alias(self):
        desc = describe_standard_observer("lms")
        assert "Cone" in desc

    def test_case_insensitive(self):
        data = get_standard_observer("Cone", "cie2006_lms2_logE_5nm")
        assert "l" in data
