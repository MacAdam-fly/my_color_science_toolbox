"""Tests for reflectance recovery."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import XYZ_to_xyY, reflectance_to_XYZ
from color.recovery import (
    recover_reflectance_from_XYZ,
    recover_reflectance_from_xyY,
    reflectance_recovery_matrix,
    second_difference_matrix,
)
from color.spectra import MultiSpectralDistribution, SpectralDistribution


def _constant_reflectance(value: float = 0.42) -> SpectralDistribution:
    _, wavelengths, _ = reflectance_recovery_matrix()
    return SpectralDistribution(
        wavelengths,
        np.full_like(wavelengths, value, dtype=np.float64),
        name="constant reflectance",
    )


def _roughness(values: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(values, n=2)))


def test_recover_reflectance_from_XYZ_round_trips_constant_reflectance() -> None:
    original = _constant_reflectance(0.42)
    target = reflectance_to_XYZ(original, illuminant="D65")

    recovered = recover_reflectance_from_XYZ(target)
    closed = reflectance_to_XYZ(recovered, illuminant="D65")

    assert isinstance(recovered, SpectralDistribution)
    assert np.allclose(closed, target, atol=2e-4)
    assert np.all(recovered.values >= 0.0)
    assert np.all(recovered.values <= 1.0)


def test_recover_reflectance_from_xyY_targets_same_XYZ() -> None:
    original = _constant_reflectance(0.35)
    target = reflectance_to_XYZ(original, illuminant="D65")
    target_xyY = XYZ_to_xyY(target)

    recovered = recover_reflectance_from_xyY(target_xyY)
    closed = reflectance_to_XYZ(recovered, illuminant="D65")

    assert np.allclose(closed, target, atol=2e-4)


def test_recover_reflectance_batch_returns_multi_spectral_distribution() -> None:
    targets = np.vstack(
        [
            reflectance_to_XYZ(_constant_reflectance(0.2), illuminant="D65"),
            reflectance_to_XYZ(_constant_reflectance(0.6), illuminant="D65"),
        ]
    )

    recovered = recover_reflectance_from_XYZ(targets, labels=("low", "high"))

    assert isinstance(recovered, MultiSpectralDistribution)
    assert recovered.labels == ("low", "high")
    assert recovered.values.shape == (recovered.wavelengths.size, 2)
    closed = reflectance_to_XYZ(recovered, illuminant="D65")
    assert np.allclose(closed, targets, atol=3e-4)


def test_recover_reflectance_bounds_are_respected() -> None:
    target = reflectance_to_XYZ(_constant_reflectance(0.8), illuminant="D65")

    recovered = recover_reflectance_from_XYZ(target, bounds=(0.1, 0.5))

    assert np.min(recovered.values) >= 0.1 - 1e-12
    assert np.max(recovered.values) <= 0.5 + 1e-12


def test_recover_reflectance_smoothness_reduces_second_difference() -> None:
    target = np.array([35.0, 22.0, 14.0])

    rough = recover_reflectance_from_XYZ(target, smoothness=0.0)
    smooth = recover_reflectance_from_XYZ(target, smoothness=10.0)

    assert _roughness(smooth.values) < _roughness(rough.values)


def test_second_difference_matrix() -> None:
    matrix = second_difference_matrix(5)

    assert matrix.shape == (3, 5)
    assert np.allclose(matrix @ np.array([0, 1, 4, 9, 16], dtype=float), [2, 2, 2])


@pytest.mark.parametrize(
    "value",
    [
        [1.0, 2.0],
        [[[1.0, 2.0, 3.0]]],
        [1.0, np.nan, 2.0],
    ],
)
def test_recover_reflectance_rejects_invalid_XYZ(value) -> None:
    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"bounds": (1.0, 0.0)},
        {"bounds": (np.nan, 1.0)},
        {"smoothness": -1.0},
        {"method": "basis"},
    ],
)
def test_recover_reflectance_rejects_invalid_options(kwargs) -> None:
    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ([20.0, 20.0, 20.0], **kwargs)


def test_recover_reflectance_rejects_invalid_labels() -> None:
    with pytest.raises(ValueError):
        recover_reflectance_from_XYZ(
            [[20.0, 20.0, 20.0], [30.0, 30.0, 30.0]],
            labels=("only_one",),
        )
