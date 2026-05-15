"""Tests for color.datasets._registry — central dataset registry."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from color.datasets._registry import (
    DatasetEntry,
    _CACHE,
    _REGISTRY,
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

    def test_register_csv_and_load(self):
        """Register a temp CSV file in a custom category, then load it."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            f.write("400, 0.1, 0.2\n")
            f.write("500, 0.3, 0.4\n")
            f.write("600, 0.5, 0.6\n")
            tmp_path = f.name

        try:
            cat = "my_custom_cat"
            name = "my_data"
            register(DatasetEntry(
                category=cat,
                name=name,
                description="Custom CSV test",
                file_path=tmp_path,
                metadata={"names": ("wavelength", "value_a", "value_b")},
            ))

            data = get(cat, name)
            np.testing.assert_array_equal(
                data["wavelength"], [400.0, 500.0, 600.0]
            )
            np.testing.assert_array_equal(
                data["value_a"], [0.1, 0.3, 0.5]
            )
            np.testing.assert_array_equal(
                data["value_b"], [0.2, 0.4, 0.6]
            )

            assert name in list_datasets(cat)
            assert cat in list_categories()
        finally:
            Path(tmp_path).unlink()

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

    def test_load_existing_test_data_csv(self):
        """Load the test_data/just_for_test_ext.csv via manual registration."""
        from color.datasets._utils import data_dir

        csv_path = str(data_dir("test_data", "just_for_test_ext.csv"))
        cat = "test_data"
        name = "just_for_test_ext"
        register(DatasetEntry(
            category=cat,
            name=name,
            description="Test CSV for method 3",
            file_path=csv_path,
            metadata={"names": ("wavelength", "l", "m", "s")},
        ))

        data = get(cat, name)
        assert set(data.keys()) == {"wavelength", "l", "m", "s"}
        assert data["wavelength"][0] == 380.0
        assert len(data["wavelength"]) > 0
