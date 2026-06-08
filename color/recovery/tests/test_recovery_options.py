"""Tests for recovery method option objects."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import emission_to_XYZ, reflectance_to_XYZ
from color.recovery import (
    AutoGaussianRecoveryOptions,
    BoundedLeastSquaresOptions,
    Burns2019RecoveryOptions,
    DictionaryReflectanceOptions,
    GaussianRecoveryOptions,
    Meng2015RecoveryOptions,
    MultiGaussianRecoveryOptions,
    PCAReflectanceOptions,
    ReflectanceLibrary,
    recover_reflectance_from_XYZ,
    recover_spectrum_from_XYZ,
)
from color.spectra import SpectralDistribution, SpectralShape


def _shape() -> SpectralShape:
    return SpectralShape(400.0, 700.0, 100.0)


def _constant_reflectance(value: float = 0.4) -> SpectralDistribution:
    shape = _shape()
    return SpectralDistribution(
        shape.wavelengths,
        np.full(shape.wavelengths.shape, value, dtype=np.float64),
        name="constant reflectance",
    )


def _gaussian_spectrum() -> SpectralDistribution:
    shape = _shape()
    values = np.exp(-0.5 * ((shape.wavelengths - 500.0) / 45.0) ** 2)
    return SpectralDistribution(shape.wavelengths, values, name="gaussian spectrum")


def _library() -> ReflectanceLibrary:
    shape = _shape()
    reflectances = np.array(
        [
            [0.15, 0.25, 0.35, 0.45],
            [0.75, 0.55, 0.35, 0.20],
            [0.40, 0.40, 0.40, 0.40],
            [0.25, 0.50, 0.65, 0.85],
        ],
        dtype=np.float64,
    )
    return ReflectanceLibrary(
        wavelengths=shape.wavelengths,
        reflectances=reflectances,
        labels=("a", "b", "c", "d"),
        sources=("test", "test", "test", "test"),
        shape=shape,
        metadata={"datasets": ("test",), "sample_count": 4},
    )


def test_spectrum_options_are_accepted() -> None:
    shape = _shape()
    target = emission_to_XYZ(_gaussian_spectrum(), shape=shape)

    options = [
        BoundedLeastSquaresOptions(),
        GaussianRecoveryOptions(center_initials=(500.0,), use_dominant_wavelength_initial=False),
        MultiGaussianRecoveryOptions(
            center_initials=(460.0, 560.0),
            n_components=2,
            use_dominant_wavelength_initial=False,
        ),
        AutoGaussianRecoveryOptions(n_components=2),
    ]

    for option in options:
        recovered = recover_spectrum_from_XYZ(target, shape=shape, method=option)
        assert isinstance(recovered, SpectralDistribution)
        assert np.all(np.isfinite(recovered.values))


def test_reflectance_options_are_accepted() -> None:
    shape = _shape()
    library = _library()
    target = reflectance_to_XYZ(_constant_reflectance(), illuminant="D65", shape=shape)

    options = [
        BoundedLeastSquaresOptions(),
        Burns2019RecoveryOptions(),
        Meng2015RecoveryOptions(),
        PCAReflectanceOptions(library=library, n_components=2),
        DictionaryReflectanceOptions(library=library, top_k=2),
    ]

    for option in options:
        recovered = recover_reflectance_from_XYZ(target, shape=shape, method=option)
        assert isinstance(recovered, SpectralDistribution)
        assert np.all(np.isfinite(recovered.values))


def test_pca_options_match_string_path() -> None:
    library = _library()
    target = reflectance_to_XYZ(_constant_reflectance(), illuminant="D65", shape=library.shape)

    string_result = recover_reflectance_from_XYZ(
        target,
        method="pca",
        library=library,
        n_components=2,
        coefficient_regularization=1e-3,
    )
    option_result = recover_reflectance_from_XYZ(
        target,
        method=PCAReflectanceOptions(
            library=library,
            n_components=2,
            coefficient_regularization=1e-3,
        ),
    )

    np.testing.assert_allclose(option_result.values, string_result.values)


def test_dictionary_options_match_string_path() -> None:
    library = _library()
    target = reflectance_to_XYZ(_constant_reflectance(), illuminant="D65", shape=library.shape)

    string_result = recover_reflectance_from_XYZ(
        target,
        method="dictionary",
        library=library,
        dictionary_regularization=1e-6,
        dictionary_top_k=2,
    )
    option_result = recover_reflectance_from_XYZ(
        target,
        method=DictionaryReflectanceOptions(
            library=library,
            regularization=1e-6,
            top_k=2,
        ),
    )

    np.testing.assert_allclose(option_result.values, string_result.values)


def test_gaussian_options_match_string_path() -> None:
    shape = _shape()
    target = emission_to_XYZ(_gaussian_spectrum(), shape=shape)

    string_result = recover_spectrum_from_XYZ(
        target,
        shape=shape,
        method="gaussian",
        center_initials=(500.0,),
        use_dominant_wavelength_initial=False,
    )
    option_result = recover_spectrum_from_XYZ(
        target,
        shape=shape,
        method=GaussianRecoveryOptions(
            center_initials=(500.0,),
            use_dominant_wavelength_initial=False,
        ),
    )

    np.testing.assert_allclose(option_result.values, string_result.values)


def test_options_reject_wrong_recovery_family() -> None:
    target_spectrum = emission_to_XYZ(_gaussian_spectrum(), shape=_shape())
    target_reflectance = reflectance_to_XYZ(
        _constant_reflectance(),
        illuminant="D65",
        shape=_shape(),
    )

    with pytest.raises(ValueError, match="reflectance recovery options"):
        recover_spectrum_from_XYZ(
            target_spectrum,
            shape=_shape(),
            method=PCAReflectanceOptions(library=_library(), n_components=2),
        )
    with pytest.raises(ValueError, match="spectrum recovery options"):
        recover_reflectance_from_XYZ(
            target_reflectance,
            shape=_shape(),
            method=GaussianRecoveryOptions(),
        )


def test_options_reject_mixed_keyword_options() -> None:
    target = reflectance_to_XYZ(_constant_reflectance(), illuminant="D65", shape=_shape())

    with pytest.raises(ValueError, match="together with a recovery options object"):
        recover_reflectance_from_XYZ(
            target,
            shape=_shape(),
            method=PCAReflectanceOptions(library=_library(), n_components=2),
            n_components=3,
        )


def test_string_methods_reject_wrong_options() -> None:
    target = reflectance_to_XYZ(_constant_reflectance(), illuminant="D65", shape=_shape())

    with pytest.raises(ValueError, match="Unsupported option"):
        recover_reflectance_from_XYZ(
            target,
            shape=_shape(),
            method="pca",
            library=_library(),
            dictionary_top_k=2,
        )
    with pytest.raises(ValueError, match="library_datasets"):
        recover_reflectance_from_XYZ(
            target,
            shape=_shape(),
            method="pca",
            library_datasets="munsell_matt",
        )


def test_database_methods_require_library() -> None:
    target = reflectance_to_XYZ(_constant_reflectance(), illuminant="D65", shape=_shape())

    with pytest.raises(ValueError, match="load_reflectance_library"):
        recover_reflectance_from_XYZ(target, shape=_shape(), method="pca")
    with pytest.raises(ValueError, match="load_reflectance_library"):
        recover_reflectance_from_XYZ(target, shape=_shape(), method="dictionary")
