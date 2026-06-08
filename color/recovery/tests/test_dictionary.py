"""Tests for dictionary reflectance recovery."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import XYZ_to_xyY, reflectance_to_XYZ
from color.recovery import (
    ReflectanceLibrary,
    recover_reflectance_from_XYZ,
    recover_reflectance_from_xyY,
)
from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape


def _small_dictionary_library() -> ReflectanceLibrary:
    shape = SpectralShape(400.0, 700.0, 100.0)
    wavelengths = shape.wavelengths
    reflectances = np.array(
        [
            [0.10, 0.20, 0.30, 0.40],
            [0.80, 0.60, 0.40, 0.20],
            [0.35, 0.35, 0.35, 0.35],
            [0.20, 0.50, 0.70, 0.90],
        ],
        dtype=np.float64,
    )
    return ReflectanceLibrary(
        wavelengths=wavelengths,
        reflectances=reflectances,
        labels=("sample_0", "sample_1", "sample_2", "sample_3"),
        sources=("test", "test", "test", "test"),
        shape=shape,
        metadata={"datasets": ("test",), "sample_count": 4},
    )


def _mean_target(library: ReflectanceLibrary) -> tuple[SpectralDistribution, np.ndarray]:
    mean = SpectralDistribution(
        library.wavelengths,
        np.mean(library.reflectances, axis=0),
        name="dictionary mean",
    )
    target = reflectance_to_XYZ(mean, illuminant="D65", shape=library.shape)
    return mean, target


def test_recover_reflectance_dictionary_round_trips_mean_reflectance() -> None:
    """Dictionary recovery should close for a library convex-combination target."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    recovered = recover_reflectance_from_XYZ(
        target,
        method="dictionary",
        library=library,
        illuminant="D65",
    )
    closed = reflectance_to_XYZ(recovered, illuminant="D65", shape=library.shape)

    assert isinstance(recovered, SpectralDistribution)
    np.testing.assert_allclose(closed, target, atol=2e-4)
    assert np.min(recovered.values) >= np.min(library.reflectances) - 1e-10
    assert np.max(recovered.values) <= np.max(library.reflectances) + 1e-10
    assert recovered.metadata["recovery_method"] == "dictionary"
    assert recovered.metadata["dictionary_regularization"] == pytest.approx(1e-6)
    assert recovered.metadata["dictionary_top_k"] == 120


def test_recover_reflectance_from_xyY_dictionary_uses_XYZ_path() -> None:
    """xyY input should support dictionary through the XYZ recovery path."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    recovered = recover_reflectance_from_xyY(
        XYZ_to_xyY(target),
        method="dictionary",
        library=library,
        illuminant="D65",
    )
    closed = reflectance_to_XYZ(recovered, illuminant="D65", shape=library.shape)

    np.testing.assert_allclose(closed, target, atol=2e-4)


def test_recover_reflectance_dictionary_batch_returns_multi_spectral_distribution() -> None:
    """Dictionary recovery should preserve batch shape and labels."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)
    targets = np.vstack([target, target])

    recovered = recover_reflectance_from_XYZ(
        targets,
        method="dictionary",
        library=library,
        illuminant="D65",
        labels=("mean_a", "mean_b"),
    )

    assert isinstance(recovered, MultiSpectralDistribution)
    assert recovered.labels == ("mean_a", "mean_b")
    assert recovered.values.shape == (library.wavelengths.size, 2)


def test_recover_reflectance_dictionary_requires_explicit_library() -> None:
    """Dictionary recovery requires an explicit ReflectanceLibrary."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    with pytest.raises(ValueError, match="load_reflectance_library"):
        recover_reflectance_from_XYZ(
            target,
            method="dictionary",
            illuminant="D65",
            shape=library.shape,
        )


def test_recover_reflectance_dictionary_accepts_full_library_top_k() -> None:
    """dictionary_top_k=None should use every library atom."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    recovered = recover_reflectance_from_XYZ(
        target,
        method="dictionary",
        library=library,
        illuminant="D65",
        dictionary_top_k=None,
    )

    assert isinstance(recovered, SpectralDistribution)
    assert recovered.metadata["dictionary_top_k"] is None


def test_recover_reflectance_dictionary_accepts_candidate_top_k() -> None:
    """dictionary_top_k should limit candidate atoms without trimming the library."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    recovered = recover_reflectance_from_XYZ(
        target,
        method="dictionary",
        library=library,
        illuminant="D65",
        dictionary_top_k=2,
    )

    assert isinstance(recovered, SpectralDistribution)
    assert recovered.metadata["library_sample_count"] == 4
    assert recovered.metadata["dictionary_top_k"] == 2


def test_recover_reflectance_dictionary_rejects_negative_regularization() -> None:
    """Dictionary regularisation must be non-negative."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(
            target,
            method="dictionary",
            library=library,
            illuminant="D65",
            dictionary_regularization=-1.0,
        )


def test_recover_reflectance_dictionary_rejects_invalid_top_k() -> None:
    """dictionary_top_k must be positive or None."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    with pytest.raises(ValueError, match="dictionary_top_k"):
        recover_reflectance_from_XYZ(
            target,
            method="dictionary",
            library=library,
            illuminant="D65",
            dictionary_top_k=0,
        )


def test_recover_reflectance_dictionary_rejects_library_shape_mismatch() -> None:
    """Dictionary library wavelengths must match the recovery matrix shape."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(
            target,
            method="dictionary",
            library=library,
            illuminant="D65",
            shape=SpectralShape(400.0, 700.0, 50.0),
        )


def test_recover_reflectance_dictionary_rejects_invalid_library_type() -> None:
    """Dictionary recovery requires a ReflectanceLibrary object."""
    library = _small_dictionary_library()
    _, target = _mean_target(library)

    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(
            target,
            method="dictionary",
            library=object(),  # type: ignore[arg-type]
            illuminant="D65",
        )
