"""Tests for color.datasets._registry — central dataset registry."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets._registry import (
    DatasetEntry,
    _CACHE,
    _REGISTRY,
    clear_cache,
    describe,
    get,
    list_categories,
    list_datasets,
    register,
    register_computed,
    search,
)


class TestDatasetEntry:
    """Tests for the DatasetEntry dataclass."""

    def test_basic_creation(self):
        entry = DatasetEntry(
            category="illuminants",
            name="test",
            description="A test dataset",
        )
        assert entry.category == "illuminants"
        assert entry.name == "test"
        assert entry.computed is False
        assert entry.read_options == {}
        assert entry.metadata == {}

    def test_frozen(self):
        entry = DatasetEntry(category="c", name="n", description="d")
        with pytest.raises(AttributeError):
            entry.name = "other"


class TestRegister:
    """Tests for register() and register_computed()."""

    def test_register_file_based(self):
        entry = DatasetEntry(
            category="test_cat",
            name="test_file",
            description="test",
            file_path="/tmp/test.csv",
        )
        register(entry)
        assert ("test_cat", "test_file") in _REGISTRY
        assert _REGISTRY[("test_cat", "test_file")].file_path == "/tmp/test.csv"

    def test_register_computed(self):
        def _gen(**kw):
            return {"wavelength": np.array([400.0]), "value": np.array([1.0])}

        register_computed("test_cat", "test_computed", _gen, description="computed")
        entry = _REGISTRY[("test_cat", "test_computed")]
        assert entry.computed is True
        assert entry.compute_fn is _gen

    def test_register_overwrites(self):
        register(DatasetEntry(category="c", name="n", description="v1"))
        register(DatasetEntry(category="c", name="n", description="v2"))
        assert _REGISTRY[("c", "n")].description == "v2"

    def test_register_rejects_unknown_read_options(self):
        entry = DatasetEntry(
            category="test_cat",
            name="bad_options",
            description="test",
            file_path="/tmp/test.csv",
            read_options={"heder": True},
        )

        with pytest.raises(ValueError, match="Unknown read_options"):
            register(entry)

    def test_register_allows_known_read_options(self):
        entry = DatasetEntry(
            category="test_cat",
            name="good_options",
            description="test",
            file_path="/tmp/test.csv",
            read_options={
                "header": True,
                "skiprows": 1,
                "usecols": [0, 1],
                "sheet": "data",
                "coerce_numeric": True,
            },
        )

        register(entry)
        assert _REGISTRY[("test_cat", "good_options")].read_options["header"] is True


class TestGet:
    """Tests for the get() function."""

    def test_missing_dataset_raises_keyerror(self):
        with pytest.raises(KeyError, match="No dataset"):
            get("nonexistent_category", "nonexistent_name")

    def test_invalid_category_type_raises(self):
        with pytest.raises(AssertionError):
            get(123, "name")  # type: ignore

    def test_invalid_name_type_raises(self):
        with pytest.raises(AssertionError):
            get("cat", 456)  # type: ignore

    def test_file_cache_includes_sheet_kwargs(self, tmp_path):
        """Different sheet= kwargs for one Excel file must not share cache data."""
        import pandas as pd

        xlsx_path = tmp_path / "two_sheets.xlsx"
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            pd.DataFrame({
                "wavelength": [400, 500],
                "a": [0.1, 0.2],
            }).to_excel(writer, sheet_name="A", index=False)
            pd.DataFrame({
                "wavelength": [600, 700],
                "b": [0.3, 0.4],
            }).to_excel(writer, sheet_name="B", index=False)

        cat = "cache_sheet_test"
        name = "two_sheets"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Temporary two-sheet XLSX",
            file_path=str(xlsx_path),
            read_options={"sheet": "A", "header": True},
        ))

        sheet_a = get(cat, name)
        sheet_b = get(cat, name, sheet="B")

        assert list(sheet_a.keys()) == ["wavelength", "a"]
        assert list(sheet_b.keys()) == ["wavelength", "b"]
        np.testing.assert_array_equal(sheet_a["wavelength"], [400.0, 500.0])
        np.testing.assert_array_equal(sheet_b["wavelength"], [600.0, 700.0])

    def test_file_result_is_readonly_copy(self, tmp_path):
        """Mutating a returned file dataset should fail and leave cache intact."""
        csv_path = tmp_path / "readonly_file.csv"
        csv_path.write_text("400,0.1\n500,0.2\n", encoding="utf-8")

        cat = "readonly_file_test"
        name = "spd"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Temporary read-only file dataset",
            file_path=str(csv_path),
            columns=("wavelength", "spd"),
        ))

        first = get(cat, name)
        with pytest.raises(ValueError):
            first["spd"][0] = 99.0

        second = get(cat, name)
        assert first is not second
        assert first["spd"] is not second["spd"]
        assert first["spd"].flags.writeable is False
        np.testing.assert_array_equal(second["spd"], [0.1, 0.2])

    def test_computed_result_is_readonly_copy(self):
        """Mutating a returned computed dataset should not touch cached data."""
        calls = 0

        def _gen(**kw):
            nonlocal calls
            calls += 1
            return {"wavelength": np.array([400.0]), "value": np.array([1.0])}

        cat = "readonly_computed_test"
        name = "generated"
        register_computed(cat, name, _gen)

        first = get(cat, name)
        with pytest.raises(ValueError):
            first["value"][0] = 99.0

        second = get(cat, name)
        assert calls == 1
        assert second["value"].flags.writeable is False
        np.testing.assert_array_equal(second["value"], [1.0])


class TestListAndSearch:
    """Tests for list_categories, list_datasets, search."""

    def test_list_categories_returns_sorted(self):
        cats = list_categories()
        assert cats == sorted(cats)

    def test_list_datasets_filters_by_category(self):
        register(DatasetEntry(category="aaa", name="x", description=""))
        register(DatasetEntry(category="aaa", name="y", description=""))
        register(DatasetEntry(category="bbb", name="z", description=""))
        assert list_datasets("aaa") == ["x", "y"]

    def test_search_by_keyword(self):
        results = search("D65")
        assert any("D65" in r.name for r in results)

    def test_search_case_insensitive(self):
        results = search("d65")
        assert any("D65" in r.name for r in results)


class TestClearCache:
    """Tests for selective cache clearing."""

    def test_clear_cache_all(self):
        register_computed(
            "clear_all_a",
            "one",
            lambda **kw: {"wavelength": np.array([400.0]), "v": np.array([1.0])},
        )
        register_computed(
            "clear_all_b",
            "two",
            lambda **kw: {"wavelength": np.array([500.0]), "v": np.array([2.0])},
        )
        get("clear_all_a", "one")
        get("clear_all_b", "two")

        removed = clear_cache()

        assert removed >= 2
        assert len(_CACHE) == 0

    def test_clear_cache_by_category(self):
        clear_cache()
        register_computed(
            "clear_cat_a",
            "one",
            lambda **kw: {"wavelength": np.array([400.0]), "v": np.array([1.0])},
        )
        register_computed(
            "clear_cat_b",
            "two",
            lambda **kw: {"wavelength": np.array([500.0]), "v": np.array([2.0])},
        )
        get("clear_cat_a", "one")
        get("clear_cat_b", "two")

        removed = clear_cache("clear_cat_a")

        assert removed == 1
        assert all(key[0] != "clear_cat_a" for key in _CACHE)
        assert any(key[0] == "clear_cat_b" for key in _CACHE)

    def test_clear_cache_by_category_and_name(self):
        clear_cache()
        register_computed(
            "clear_name",
            "one",
            lambda **kw: {"wavelength": np.array([400.0]), "v": np.array([1.0])},
        )
        register_computed(
            "clear_name",
            "two",
            lambda **kw: {"wavelength": np.array([500.0]), "v": np.array([2.0])},
        )
        get("clear_name", "one")
        get("clear_name", "two")

        removed = clear_cache("clear_name", "one")

        assert removed == 1
        assert all(not (key[0] == "clear_name" and key[1] == "one") for key in _CACHE)
        assert any(key[0] == "clear_name" and key[1] == "two" for key in _CACHE)

    def test_clear_cache_name_without_category_raises(self):
        with pytest.raises(ValueError):
            clear_cache(name="D65")


class TestDescribe:
    """Tests for describe()."""

    def test_describe_existing(self):
        entry = describe("illuminants", "D65")
        assert entry.category == "illuminants"
        assert entry.name == "D65"
        assert "D65" in entry.description

    def test_describe_missing_raises(self):
        with pytest.raises(KeyError):
            describe("illuminants", "NONEXISTENT")


# ---------------------------------------------------------------------------
# 方式三：手动注册新类别 — 集成测试
# ---------------------------------------------------------------------------

class TestManualRegistration:
    """Test registering and loading custom categories (method 3)."""

    def test_register_csv_without_header_and_load(self, tmp_path):
        """Register a temporary no-header CSV in a custom category."""
        csv_path = tmp_path / "rgb_led.csv"
        csv_path.write_text(
            "400,0.1,0.2\n"
            "500,0.3,0.4\n"
            "600,0.5,0.6\n",
            encoding="utf-8",
        )

        cat = "temp_csv_no_header"
        name = "rgb_led"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Temporary no-header CSV test",
            file_path=str(csv_path),
            columns=("wavelength", "value_a", "value_b"),
        ))

        data = get(cat, name)
        np.testing.assert_array_equal(data["wavelength"], [400.0, 500.0, 600.0])
        np.testing.assert_array_equal(data["value_a"], [0.1, 0.3, 0.5])
        np.testing.assert_array_equal(data["value_b"], [0.2, 0.4, 0.6])

        assert name in list_datasets(cat)
        assert cat in list_categories()

    def test_register_csv_with_header_auto(self, tmp_path):
        """Register a temporary CSV whose header is detected automatically."""
        csv_path = tmp_path / "measured_spd.csv"
        csv_path.write_text(
            "wl,spd,uncertainty\n"
            "450,0.2,0.01\n"
            "550,1.0,0.02\n"
            "650,0.3,0.01\n",
            encoding="utf-8",
        )

        cat = "temp_csv_header"
        name = "measured_spd"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Temporary header CSV test",
            file_path=str(csv_path),
            read_options={"header": "auto"},
        ))

        data = get(cat, name)
        assert list(data.keys()) == ["wl", "spd", "uncertainty"]
        np.testing.assert_array_equal(data["wl"], [450.0, 550.0, 650.0])
        assert data["spd"][1] == 1.0

    def test_register_csv_header_with_column_override(self, tmp_path):
        """Explicit columns should override a temporary CSV file header."""
        csv_path = tmp_path / "header_override.csv"
        csv_path.write_text(
            "lambda,power\n"
            "500,0.8\n"
            "510,0.9\n",
            encoding="utf-8",
        )

        cat = "temp_csv_override"
        name = "renamed_spd"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Temporary CSV column override test",
            file_path=str(csv_path),
            columns=("wavelength", "spd"),
            read_options={"header": "auto"},
        ))

        data = get(cat, name)
        assert list(data.keys()) == ["wavelength", "spd"]
        np.testing.assert_array_equal(data["wavelength"], [500.0, 510.0])

    def test_register_xlsx_with_sheet(self, tmp_path):
        """Register a temporary XLSX file and read a named sheet."""
        import pandas as pd

        xlsx_path = tmp_path / "multi_sheet.xlsx"
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            pd.DataFrame({"ignore": [1, 2]}).to_excel(
                writer, sheet_name="Metadata", index=False
            )
            pd.DataFrame({
                "wavelength": [460, 560, 660],
                "spd": [0.2, 1.0, 0.4],
            }).to_excel(writer, sheet_name="SPD", index=False)

        cat = "temp_xlsx"
        name = "sheet_spd"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Temporary XLSX sheet test",
            file_path=str(xlsx_path),
            read_options={"sheet": "SPD", "header": True},
        ))

        data = get(cat, name)
        assert list(data.keys()) == ["wavelength", "spd"]
        np.testing.assert_array_equal(data["wavelength"], [460.0, 560.0, 660.0])

    def test_register_computed_and_load(self):
        """Register a computed dataset and load it with parameters."""
        def _sine(wavelength_nm=None, frequency=1.0):
            if wavelength_nm is None:
                wavelength_nm = np.arange(400, 701, 1.0)
            return {
                "wavelength": wavelength_nm,
                "value": np.sin(2 * np.pi * frequency * wavelength_nm / 100.0),
            }

        cat = "my_computed_cat"
        name = "sine_wave"
        register_computed(
            category=cat,
            name=name,
            compute_fn=_sine,
            description="Test sine wave",
            metadata={"unit": "arbitrary"},
        )

        data = get(cat, name, frequency=2.0)
        assert "wavelength" in data
        assert "value" in data
        assert len(data["wavelength"]) == 301  # 400–700

        entry = describe(cat, name)
        assert entry.computed is True
        assert entry.metadata["unit"] == "arbitrary"

    def test_register_computed_cached(self):
        """Computed datasets with same params return cached result."""
        call_count = 0

        def _counter(**kw):
            nonlocal call_count
            call_count += 1
            return {"wavelength": np.array([400.0]), "v": np.array([1.0])}

        register_computed("cache_test", "ctr", _counter)
        get("cache_test", "ctr")
        get("cache_test", "ctr")
        assert call_count == 1
