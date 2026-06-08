"""Tests for PCA reflectance recovery."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import reflectance_to_XYZ
from color.recovery import (
    load_reflectance_library,
    recover_reflectance_from_XYZ,
    recover_reflectance_from_xyY,
)
from color.colorimetry import XYZ_to_xyY
from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape


def _library_mean_reflectance() -> tuple:
    library = load_reflectance_library("munsell_matt")
    reflectance = SpectralDistribution(
        library.wavelengths,
        np.mean(library.reflectances, axis=0),
        name="Munsell matt mean reflectance",
    )
    target = reflectance_to_XYZ(reflectance, illuminant="D65", shape=library.shape)
    return library, reflectance, target


def test_recover_reflectance_from_XYZ_pca_round_trips_mean_reflectance() -> None:
    """PCA recovery should close exactly for the library mean."""
    library, _, target = _library_mean_reflectance()

    recovered = recover_reflectance_from_XYZ(
        target,
        method="pca",
        library=library,
    )
    closed = reflectance_to_XYZ(recovered, illuminant="D65", shape=library.shape)

    assert isinstance(recovered, SpectralDistribution)
    assert np.all(recovered.values >= -1e-10)
    assert np.all(recovered.values <= 1.0 + 1e-10)
    np.testing.assert_allclose(closed, target, atol=2e-4)
    assert recovered.metadata["recovery_method"] == "pca"
    assert recovered.metadata["library_sample_count"] == 1269


def test_recover_reflectance_from_xyY_pca_uses_XYZ_path() -> None:
    """xyY input should support PCA through the XYZ recovery path."""
    library, _, target = _library_mean_reflectance()
    xyy = XYZ_to_xyY(target)

    recovered = recover_reflectance_from_xyY(
        xyy,
        method="pca",
        library=library,
    )
    closed = reflectance_to_XYZ(recovered, illuminant="D65", shape=library.shape)

    np.testing.assert_allclose(closed, target, atol=2e-4)


def test_recover_reflectance_pca_batch_returns_multi_spectral_distribution() -> None:
    """PCA recovery should preserve batch shape and labels."""
    library, _, target = _library_mean_reflectance()
    targets = np.vstack([target, target])

    recovered = recover_reflectance_from_XYZ(
        targets,
        method="pca",
        library=library,
        labels=("mean_a", "mean_b"),
    )

    assert isinstance(recovered, MultiSpectralDistribution)
    assert recovered.labels == ("mean_a", "mean_b")
    assert recovered.values.shape == (library.wavelengths.size, 2)
    assert np.all(recovered.values >= -1e-10)
    assert np.all(recovered.values <= 1.0 + 1e-10)


def test_recover_reflectance_pca_loads_default_library() -> None:
    """PCA recovery should load the default Munsell matt library when omitted."""
    library, _, target = _library_mean_reflectance()

    recovered = recover_reflectance_from_XYZ(target, method="pca")

    assert isinstance(recovered, SpectralDistribution)
    assert recovered.wavelengths.shape == library.wavelengths.shape
    assert recovered.metadata["library_datasets"] == ("munsell_matt",)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_components": 0},
        {"n_components": 10_000},
        {"coefficient_regularization": -1.0},
    ],
)
def test_recover_reflectance_pca_rejects_invalid_options(kwargs) -> None:
    """Invalid PCA options should raise ValueError."""
    library, _, target = _library_mean_reflectance()
    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(
            target,
            method="pca",
            library=library,
            **kwargs,
        )


def test_recover_reflectance_pca_rejects_library_shape_mismatch() -> None:
    """PCA library wavelengths must match the recovery matrix shape."""
    library, _, target = _library_mean_reflectance()
    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(
            target,
            method="pca",
            library=library,
            shape=SpectralShape(400.0, 700.0, 10.0),
        )
