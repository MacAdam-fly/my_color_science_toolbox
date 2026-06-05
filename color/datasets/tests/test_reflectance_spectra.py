"""Tests for UEF spectral reflectance datasets."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from color.datasets import (
    describe,
    get,
    get_reflectance_spectrum,
    list_categories,
    list_datasets,
    list_reflectance_spectra,
)
from color.datasets._utils import data_dir


EXPECTED = {
    "agfa_it872": ("reflectance_0_1", 31, 288, 1.0),
    "forest_birch": ("corrected_reflectance_0_1", 93, 337, 1.0),
    "forest_pine": ("corrected_reflectance_0_1", 93, 370, 1.0),
    "forest_spruce": ("corrected_reflectance_0_1", 93, 349, 1.0),
    "munsell_glossy_all": ("reflectance_0_1", 401, 1600, 1.0),
    "munsell_matt": ("reflectance_0_1", 421, 1269, 1.0),
    "paper_cardboardsce": ("reflectance_0_1", 31, 140, 1.11),
    "paper_cardboardsci": ("reflectance_0_1", 31, 210, 1.11),
    "paper_newsprintsce": ("reflectance_0_1", 31, 36, 1.11),
    "paper_newsprintsci": ("reflectance_0_1", 31, 54, 1.11),
    "paper_papersce": ("reflectance_0_1", 31, 144, 1.11),
    "paper_papersci": ("reflectance_0_1", 31, 216, 1.11),
}


class TestReflectanceSpectraRegistry:
    def test_category_registered(self):
        assert "reflectance_spectra.uef" in list_categories()

    def test_list_reflectance_spectra(self):
        assert list_reflectance_spectra() == sorted(EXPECTED)
        assert list_datasets("reflectance_spectra.uef") == sorted(EXPECTED)

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_get_matches_generic_get(self, name):
        direct = get_reflectance_spectrum(name)
        generic = get("reflectance_spectra.uef", name)

        assert direct.keys() == generic.keys()
        for key in direct:
            np.testing.assert_array_equal(direct[key], generic[key])

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_data_shape_and_range(self, name):
        _, row_count, sample_count, max_allowed = EXPECTED[name]
        data = get_reflectance_spectrum(name)

        assert "wavelength" in data
        assert data["wavelength"].shape == (row_count,)
        assert np.all(np.diff(data["wavelength"]) > 0)

        sample_keys = [key for key in data if key != "wavelength"]
        assert len(sample_keys) == sample_count
        values = np.stack([data[key] for key in sample_keys], axis=-1)
        assert values.shape == (row_count, sample_count)
        assert np.all(np.isfinite(values))
        assert values.min() >= 0.0
        assert values.max() <= max_allowed

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_metadata(self, name):
        entry = describe("reflectance_spectra.uef", name)

        assert entry.metadata["quantity"] == "spectral_reflectance"
        assert entry.metadata["source_collection"] == "UEF"
        assert entry.metadata["wavelength_unit"] == "nm"
        assert entry.metadata["value_unit"] == "reflectance_factor"
        assert entry.metadata["runtime_source"] == f"uef_csv/{name}.csv"
        assert entry.metadata["audit_source"] == f"uef_sources_data/{name}.xlsx"
        assert entry.metadata["sample_count"] == EXPECTED[name][2]
        assert entry.read_options == {"header": True, "coerce_numeric": True}


class TestReflectanceSpectraCsvExport:
    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_runtime_csv_matches_source_workbook_sheet(self, name):
        sheet, _, _, _ = EXPECTED[name]
        root = data_dir("reflectance_spectra")
        csv_path = Path(root) / "uef_csv" / f"{name}.csv"
        xlsx_path = Path(root) / "uef_sources_data" / f"{name}.xlsx"

        csv_frame = pd.read_csv(csv_path)
        workbook_frame = pd.read_excel(xlsx_path, sheet_name=sheet, engine="openpyxl")

        assert csv_frame.shape == workbook_frame.shape
        assert list(csv_frame.columns) == list(workbook_frame.columns)
        np.testing.assert_allclose(
            csv_frame.to_numpy(dtype=float),
            workbook_frame.to_numpy(dtype=float),
            rtol=0,
            atol=5e-12,
        )
