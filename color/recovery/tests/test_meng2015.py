"""Tests for Meng et al. (2015) reflectance recovery."""

from __future__ import annotations

import numpy as np

from color.colorimetry import XYZ_to_xyY, reflectance_to_XYZ
from color.recovery import recover_reflectance_from_XYZ, recover_reflectance_from_xyY
from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape


def _shape() -> SpectralShape:
    """Return a coarse shape keeping SLSQP tests fast."""
    return SpectralShape(400.0, 700.0, 25.0)


def _smooth_reflectance(shape: SpectralShape | None = None) -> SpectralDistribution:
    """Return a bounded smooth reflectance for feasible target generation."""
    common_shape = shape or _shape()
    wavelengths = common_shape.wavelengths
    values = 0.35 + 0.15 * np.sin((wavelengths - wavelengths[0]) / 90.0)
    return SpectralDistribution(
        wavelengths,
        values,
        name="smooth reflectance",
    )


def test_recover_reflectance_meng2015_round_trips_XYZ() -> None:
    shape = _shape()
    original = _smooth_reflectance(shape)
    target = reflectance_to_XYZ(original, illuminant="D65", shape=shape)

    recovered = recover_reflectance_from_XYZ(
        target,
        method="meng2015",
        illuminant="D65",
        shape=shape,
    )
    closed = reflectance_to_XYZ(recovered, illuminant="D65", shape=shape)

    assert isinstance(recovered, SpectralDistribution)
    assert np.min(recovered.values) >= -1e-10
    assert np.max(recovered.values) <= 1.0 + 1e-10
    np.testing.assert_allclose(closed, target, atol=2e-4)
    assert recovered.metadata["recovery_method"] == "meng2015"
    assert recovered.metadata["closure_constraint"] == "exact_XYZ_equality"


def test_recover_reflectance_from_xyY_meng2015_uses_XYZ_path() -> None:
    shape = _shape()
    original = _smooth_reflectance(shape)
    target = reflectance_to_XYZ(original, illuminant="D65", shape=shape)

    recovered = recover_reflectance_from_xyY(
        XYZ_to_xyY(target),
        method="Meng 2015",
        illuminant="D65",
        shape=shape,
    )
    closed = reflectance_to_XYZ(recovered, illuminant="D65", shape=shape)

    np.testing.assert_allclose(closed, target, atol=2e-4)


def test_recover_reflectance_meng2015_batch_returns_multi_spectral_distribution() -> None:
    shape = _shape()
    low = reflectance_to_XYZ(_smooth_reflectance(shape), illuminant="D65", shape=shape)
    high_reflectance = SpectralDistribution(
        shape.wavelengths,
        0.8 * _smooth_reflectance(shape).values,
        name="scaled smooth reflectance",
    )
    high = reflectance_to_XYZ(high_reflectance, illuminant="D65", shape=shape)

    recovered = recover_reflectance_from_XYZ(
        np.vstack([low, high]),
        method="meng2015",
        illuminant="D65",
        shape=shape,
        labels=("low", "high"),
    )

    assert isinstance(recovered, MultiSpectralDistribution)
    assert recovered.labels == ("low", "high")
    assert recovered.values.shape == (shape.wavelengths.size, 2)
