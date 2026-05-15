"""Tests for color.datasets._utils — file reading utilities."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets._utils import attest, data_dir, read_csv, read_xls, read_xlsx


class TestAttest:
    """Tests for the attest() validation function."""

    def test_passes_on_true(self):
        attest(True, "should not raise")

    def test_raises_on_false(self):
        with pytest.raises(AssertionError, match="bad input"):
            attest(False, "bad input")

    def test_raises_with_empty_message(self):
        with pytest.raises(AssertionError):
            attest(False)


class TestDataDir:
    """Tests for the data_dir() path helper."""

    def test_returns_path(self):
        p = data_dir("illuminants")
        assert p.name == "illuminants"
        assert p.exists()

    def test_nested_path(self):
        p = data_dir("standard_observer_data", "cmfs")
        assert p.exists()


class TestReadCsv:
    """Tests for read_csv()."""

    def test_basic_csv(self, data_root):
        path = data_root / "illuminants" / "illuminant_A.csv"
        result = read_csv(str(path))
        assert "wavelength" in result
        assert "value" in result
        assert result["wavelength"].shape == result["value"].shape
        assert len(result["wavelength"]) > 100

    def test_header_skiprows(self, data_root):
        path = data_root / "illuminants" / "illuminant_A.csv"
        full = read_csv(str(path))
        skipped = read_csv(str(path), header=False, skiprows=10)
        assert len(skipped["wavelength"]) == len(full["wavelength"]) - 10

    def test_usecols(self, data_root):
        path = data_root / "standard_observer_data" / "cmfs" / "cie1931_xyz_1nm.csv"
        result = read_csv(str(path), usecols=[0, 1])
        assert list(result.keys()) == ["wavelength", "value"]

    def test_custom_names(self, data_root):
        path = data_root / "illuminants" / "illuminant_A.csv"
        result = read_csv(str(path), names=("wl", "spd"))
        assert "wl" in result
        assert "spd" in result

    def test_trailing_commas_handled(self, data_root):
        path = data_root / "color_cards" / "MacbethColorChecker(Sheet1).csv"
        result = read_csv(str(path), header=False, skiprows=3, usecols=range(26))
        assert result["wavelength"].shape[0] > 70

    def test_inhomogeneous_rows_padded(self, tmp_path):
        csv = tmp_path / "test.csv"
        csv.write_text("1,2,3\n4,5\n6,7,8,9\n")
        result = read_csv(str(csv), names=("a", "b", "c", "d"))
        assert result["a"].shape == (3,)
        # Row 0: 1,2,3 — all values present
        assert result["a"][0] == 1.0
        assert result["b"][0] == 2.0
        assert result["c"][0] == 3.0
        # Row 1: 4,5 — only 2 values, c/d should be NaN
        assert result["a"][1] == 4.0
        assert result["b"][1] == 5.0
        assert np.isnan(result["c"][1])
        assert np.isnan(result["d"][1])
        # Row 2: 6,7,8,9 — all values present
        assert result["d"][2] == 9.0

    def test_returns_dict_of_ndarrays(self, data_root):
        path = data_root / "illuminants" / "illuminant_D65.csv"
        result = read_csv(str(path))
        for v in result.values():
            assert isinstance(v, np.ndarray)

    def test_header_reads_column_names(self, tmp_path):
        csv = tmp_path / "test_header.csv"
        csv.write_text("wl,spd1,spd2\n360,0.1,0.2\n361,0.3,0.4\n")
        result = read_csv(str(csv), header=True)
        assert list(result.keys()) == ["wl", "spd1", "spd2"]
        assert len(result["wl"]) == 2

    def test_header_detected_uses_file_names(self, tmp_path):
        csv = tmp_path / "test_header.csv"
        csv.write_text("wl,spd1,spd2\n360,0.1,0.2\n361,0.3,0.4\n")
        result = read_csv(str(csv), header=True)
        # header detected → file header used as column names
        assert list(result.keys()) == ["wl", "spd1", "spd2"]
        assert len(result["wl"]) == 2

    def test_names_used_when_no_header_detected(self, tmp_path):
        csv = tmp_path / "test_noheader.csv"
        csv.write_text("360,0.1,0.2\n361,0.3,0.4\n")
        result = read_csv(str(csv), header=True, names=("a", "b", "c"))
        # all-numeric first line → no header detected → names used
        assert list(result.keys()) == ["a", "b", "c"]
        assert len(result["a"]) == 2

    def test_names_overrides_detected_header(self, tmp_path):
        csv = tmp_path / "test_header.csv"
        csv.write_text("wl,spd1,spd2\n360,0.1,0.2\n361,0.3,0.4\n")
        result = read_csv(str(csv), header=True, names=("a", "b", "c"))
        # names (columns) always overrides detected header
        assert list(result.keys()) == ["a", "b", "c"]
        assert len(result["a"]) == 2

    def test_header_with_usecols(self, tmp_path):
        csv = tmp_path / "test_header.csv"
        csv.write_text("wl,spd1,spd2\n360,0.1,0.2\n361,0.3,0.4\n")
        result = read_csv(str(csv), header=True, usecols=[0, 2])
        assert list(result.keys()) == ["wl", "spd2"]
        assert len(result["wl"]) == 2

    def test_header_false_text_rows_cause_error(self, tmp_path):
        csv = tmp_path / "test_noheader.csv"
        csv.write_text("wl,spd1,spd2\n360,0.1,0.2\n361,0.3,0.4\n")
        with pytest.raises(ValueError, match="could not convert"):
            read_csv(str(csv), header=False)


class TestReadXlsx:
    """Tests for read_xlsx()."""

    def test_basic_xlsx(self, data_root):
        path = data_root / "color_cards" / "PMC.xlsx"
        result = read_xlsx(str(path), sheet=0, header=False, skiprows=1)
        assert len(result) > 1

    def test_by_sheet_index(self, data_root):
        path = data_root / "color_cards" / "PMC.xlsx"
        result = read_xlsx(str(path), sheet=0, header=False, skiprows=1)
        assert len(result) > 1


class TestReadXls:
    """Tests for read_xls()."""

    def test_basic_xls(self, data_root):
        path = data_root / "illuminants" / "Fluorescents.xls"
        result = read_xls(str(path), header=1)
        assert len(result) > 1
        assert len(list(result.values())[0]) > 10

    def test_multi_column(self, data_root):
        path = data_root / "illuminants" / "Fluorescents.xls"
        result = read_xls(
            str(path),
            header=1,
            names=("wl", "F1", "F2", "F3", "F4", "F5", "F6",
                   "F7", "F8", "F9", "F10", "F11", "F12"),
        )
        assert "F1" in result
        assert "F12" in result
