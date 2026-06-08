"""Tests for reflectance recovery libraries."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets import list_reflectance_spectra
from color.recovery import ReflectanceLibrary, load_reflectance_library
from color.spectra import SpectralShape


def test_load_reflectance_library_default_uses_munsell_matt() -> None:
    """Default recovery library should use Munsell matt only."""
    library = load_reflectance_library()

    assert isinstance(library, ReflectanceLibrary)
    assert library.metadata["datasets"] == ("munsell_matt",)
    assert set(library.sources) == {"munsell_matt"}
    assert library.reflectances.shape == (1269, library.wavelengths.size)
    assert library.shape == SpectralShape(400.0, 700.0, 5.0)
    assert library.labels[0].startswith("munsell_matt:")


def test_load_reflectance_library_all_uef_expands_registered_datasets() -> None:
    """The all_uef preset should expand current UEF reflectance datasets."""
    library = load_reflectance_library("all_uef")
    expected = tuple(list_reflectance_spectra())

    assert library.metadata["datasets"] == expected
    assert set(library.sources) == set(expected)
    assert library.metadata["sample_count"] == sum(
        library.metadata["sample_counts"].values()
    )
    assert library.reflectances.shape[0] == len(library.labels)


def test_load_reflectance_library_accepts_explicit_mixed_datasets() -> None:
    """Explicit mixed datasets should preserve sample sources and labels."""
    library = load_reflectance_library(("munsell_matt", "agfa_it872"))

    assert library.metadata["datasets"] == ("munsell_matt", "agfa_it872")
    assert library.metadata["sample_counts"]["munsell_matt"] == 1269
    assert library.metadata["sample_counts"]["agfa_it872"] == 288
    assert library.reflectances.shape[0] == 1269 + 288
    assert library.sources.count("munsell_matt") == 1269
    assert library.sources.count("agfa_it872") == 288
    assert len(set(library.labels)) == len(library.labels)


def test_load_reflectance_library_custom_shape() -> None:
    """Custom shape should define wavelength count and matrix columns."""
    shape = SpectralShape(420.0, 680.0, 10.0)
    library = load_reflectance_library("agfa_it872", shape=shape)

    np.testing.assert_allclose(library.wavelengths, shape.wavelengths)
    assert library.reflectances.shape == (288, len(shape))
    assert np.isfinite(library.reflectances).all()
    assert np.all(library.reflectances >= 0.0)


def test_reflectance_library_arrays_are_read_only() -> None:
    """Returned library arrays should not be mutable."""
    library = load_reflectance_library("agfa_it872")

    assert not library.wavelengths.flags.writeable
    assert not library.reflectances.flags.writeable
    with pytest.raises(ValueError):
        library.wavelengths[0] = 0.0
    with pytest.raises(ValueError):
        library.reflectances[0, 0] = 0.0


@pytest.mark.parametrize(
    "datasets",
    [
        (),
        ("all_uef", "munsell_matt"),
        "all",
        "not_a_reflectance_dataset",
        (1,),
    ],
)
def test_load_reflectance_library_rejects_invalid_datasets(datasets) -> None:
    """Invalid dataset selectors should fail clearly."""
    with pytest.raises(ValueError):
        load_reflectance_library(datasets)


def test_load_reflectance_library_rejects_invalid_shape() -> None:
    """Shape must be a SpectralShape instance or None."""
    with pytest.raises(ValueError):
        load_reflectance_library("munsell_matt", shape=(400, 700, 5))  # type: ignore[arg-type]
