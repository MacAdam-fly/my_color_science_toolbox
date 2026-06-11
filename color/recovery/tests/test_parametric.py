"""Tests for parametric Gaussian spectrum recovery."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import emission_to_LMS, emission_to_XYZ
from color.math import gaussian_values
from color.recovery import (
    recover_spectrum_from_LMS,
    recover_spectrum_from_XYZ,
)
from color.recovery.methods import (
    resolve_reflectance_recovery_method,
    resolve_spectrum_recovery_method,
)
from color.recovery.parametric import gaussian_spectrum, multi_gaussian_spectrum
from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape


def _shape() -> SpectralShape:
    return SpectralShape(400.0, 700.0, 10.0)


def _single_gaussian_sd() -> SpectralDistribution:
    shape = _shape()
    return SpectralDistribution(
        shape.wavelengths,
        gaussian_spectrum(shape.wavelengths, 1.2, 540.0, 35.0),
        name="single gaussian target",
    )


def _double_gaussian_sd() -> SpectralDistribution:
    shape = _shape()
    return SpectralDistribution(
        shape.wavelengths,
        multi_gaussian_spectrum(
            shape.wavelengths,
            [0.9, 0.7],
            [440.0, 640.0],
            [22.0, 30.0],
        ),
        name="double gaussian target",
    )


def _relative_error(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-12))


def test_gaussian_spectrum_uses_math_gaussian_values() -> None:
    wavelengths = np.array([500.0, 540.0, 580.0])
    result = gaussian_spectrum(wavelengths, 1.2, 540.0, 35.0)
    expected = gaussian_values(wavelengths, amplitude=1.2, center=540.0, sigma=35.0)

    np.testing.assert_allclose(result, expected)


@pytest.mark.parametrize(
    "method",
    ["gaussian", "single gaussian", "Gaussian"],
)
def test_spectrum_gaussian_method_aliases(method: str) -> None:
    name, _solver = resolve_spectrum_recovery_method(method)
    assert name == "gaussian"


@pytest.mark.parametrize(
    "method",
    ["multi_gaussian", "multi gaussian", "multigaussian"],
)
def test_spectrum_multi_gaussian_method_aliases(method: str) -> None:
    name, _solver = resolve_spectrum_recovery_method(method)
    assert name == "multi_gaussian"


def test_parametric_methods_are_not_reflectance_methods() -> None:
    for method in ("gaussian", "multi_gaussian", "auto_gaussian"):
        with pytest.raises(ValueError):
            resolve_reflectance_recovery_method(method)


def test_recover_spectrum_from_XYZ_gaussian_round_trips_single_gaussian() -> None:
    shape = _shape()
    target_sd = _single_gaussian_sd()
    target = emission_to_XYZ(target_sd, shape=shape)

    recovered = recover_spectrum_from_XYZ(
        target,
        method="gaussian",
        shape=shape,
    )
    closed = emission_to_XYZ(recovered, shape=shape)

    assert isinstance(recovered, SpectralDistribution)
    assert np.all(recovered.values >= -1e-10)
    assert _relative_error(closed, target) < 2e-3
    assert recovered.metadata["recovery_method"] == "gaussian"
    assert recovered.metadata["selected_parametric_method"] == "gaussian"
    assert recovered.metadata["dominant_wavelength_initial_used"] is True
    center = recovered.metadata["gaussian_parameters"][0]["center"]
    assert abs(center - 540.0) < 20.0


def test_recover_spectrum_from_LMS_gaussian_round_trips() -> None:
    shape = _shape()
    target_sd = _single_gaussian_sd()
    target = emission_to_LMS(target_sd, shape=shape, fill_nan=0.0)

    recovered = recover_spectrum_from_LMS(
        target,
        method="gaussian",
        shape=shape,
        fill_nan=0.0,
    )
    closed = emission_to_LMS(recovered, shape=shape, fill_nan=0.0)

    assert isinstance(recovered, SpectralDistribution)
    assert _relative_error(closed, target) < 5e-3
    assert recovered.metadata["dominant_wavelength_initial_used"] is False


def test_recover_spectrum_gaussian_batch_returns_multi_spectral_distribution() -> None:
    shape = _shape()
    target = emission_to_XYZ(_single_gaussian_sd(), shape=shape)

    recovered = recover_spectrum_from_XYZ(
        np.vstack([target, 0.5 * target]),
        method="gaussian",
        shape=shape,
        labels=("full", "half"),
    )

    assert isinstance(recovered, MultiSpectralDistribution)
    assert recovered.labels == ("full", "half")
    assert recovered.values.shape == (shape.wavelengths.size, 2)


def test_multi_gaussian_improves_double_gaussian_target() -> None:
    shape = _shape()
    target = emission_to_XYZ(_double_gaussian_sd(), shape=shape)

    single = recover_spectrum_from_XYZ(
        target,
        method="gaussian",
        shape=shape,
    )
    multi = recover_spectrum_from_XYZ(
        target,
        method="multi_gaussian",
        shape=shape,
        n_components=2,
    )
    single_error = _relative_error(emission_to_XYZ(single, shape=shape), target)
    multi_error = _relative_error(emission_to_XYZ(multi, shape=shape), target)

    assert multi_error < single_error
    assert multi.metadata["n_components"] == 2


@pytest.mark.parametrize("n_components", [2, 3])
def test_multi_gaussian_component_counts(n_components: int) -> None:
    shape = _shape()
    target = emission_to_XYZ(_double_gaussian_sd(), shape=shape)

    recovered = recover_spectrum_from_XYZ(
        target,
        method="multi_gaussian",
        shape=shape,
        n_components=n_components,
    )

    assert recovered.metadata["n_components"] == n_components


def test_multi_gaussian_rejects_invalid_component_count() -> None:
    shape = _shape()
    target = emission_to_XYZ(_double_gaussian_sd(), shape=shape)

    with pytest.raises(ValueError):
        recover_spectrum_from_XYZ(
            target,
            method="multi_gaussian",
            shape=shape,
            n_components=4,
        )


def test_auto_gaussian_selects_single_for_spectral_target() -> None:
    shape = _shape()
    target = emission_to_XYZ(_single_gaussian_sd(), shape=shape)

    recovered = recover_spectrum_from_XYZ(
        target,
        method="auto_gaussian",
        shape=shape,
    )

    assert recovered.metadata["recovery_method"] == "auto_gaussian"
    assert recovered.metadata["selected_parametric_method"] == "gaussian"
    assert recovered.metadata["selection_reason"] == "spectral_dominant_wavelength"


def test_auto_gaussian_selects_multi_for_purple_target() -> None:
    shape = _shape()
    target = emission_to_XYZ(_double_gaussian_sd(), shape=shape)

    recovered = recover_spectrum_from_XYZ(
        target,
        method="auto_gaussian",
        shape=shape,
        n_components=2,
    )

    assert recovered.metadata["recovery_method"] == "auto_gaussian"
    assert recovered.metadata["selected_parametric_method"] == "multi_gaussian"
    assert recovered.metadata["dominant_region"] == "purple"


def test_auto_gaussian_selects_multi_for_near_white_target() -> None:
    shape = _shape()
    flat = SpectralDistribution(
        shape.wavelengths,
        np.ones_like(shape.wavelengths),
        name="flat spectrum",
    )
    target = emission_to_XYZ(flat, shape=shape)

    recovered = recover_spectrum_from_XYZ(
        target,
        method="auto_gaussian",
        shape=shape,
        n_components=3,
    )

    assert recovered.metadata["selected_parametric_method"] == "multi_gaussian"
