"""Tests for effective spectrum recovery."""

from __future__ import annotations

import numpy as np

from color.colorimetry import XYZ_to_xyY, emission_to_LMS, emission_to_XYZ
from color.generators.ideal import gaussian_spd
from color.recovery import (
    recover_spectrum_from_LMS,
    recover_spectrum_from_responses,
    recover_spectrum_from_XYZ,
    recover_spectrum_from_xyY,
    response_recovery_matrix,
)
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_cie1931_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_columns,
)


def _gaussian_spectrum() -> SpectralDistribution:
    raw = gaussian_spd(
        wavelength_nm=np.arange(400.0, 701.0, 1.0),
        peak_wavelength=540.0,
        width=40.0,
        method="normal",
    )
    return from_columns(raw, y="spd", name="test gaussian spectrum")


def test_recover_spectrum_from_XYZ_round_trips_emission_XYZ() -> None:
    original = _gaussian_spectrum()
    target = emission_to_XYZ(original, shape=SpectralShape(400, 700, 1))

    recovered = recover_spectrum_from_XYZ(
        target,
        shape=SpectralShape(400, 700, 1),
        smoothness=1e-3,
    )
    closed = emission_to_XYZ(recovered, shape=SpectralShape(400, 700, 1))

    assert isinstance(recovered, SpectralDistribution)
    assert np.allclose(closed, target, atol=2e-4)
    assert np.all(recovered.values >= 0.0)


def test_recover_spectrum_from_xyY_round_trips_emission_XYZ() -> None:
    original = _gaussian_spectrum()
    shape = SpectralShape(400, 700, 1)
    target = emission_to_XYZ(original, shape=shape)
    target_xyY = XYZ_to_xyY(target)

    recovered = recover_spectrum_from_xyY(
        target_xyY,
        shape=shape,
        smoothness=1e-3,
    )
    closed = emission_to_XYZ(recovered, shape=shape)

    assert isinstance(recovered, SpectralDistribution)
    assert np.allclose(closed, target, atol=2e-4)


def test_recover_spectrum_from_LMS_round_trips_emission_LMS() -> None:
    original = _gaussian_spectrum()
    shape = SpectralShape(400, 700, 1)
    target = emission_to_LMS(original, shape=shape)

    recovered = recover_spectrum_from_LMS(target, shape=shape, smoothness=1e-3)
    closed = emission_to_LMS(recovered, shape=shape)

    assert np.allclose(closed, target, atol=2e-4)


def test_recover_spectrum_from_responses_accepts_custom_responses() -> None:
    shape = SpectralShape(400, 700, 1)
    responses = from_cie1931_xyz_cmfs().reshape(shape)
    original = _gaussian_spectrum().reshape(shape)
    matrix, _, _ = response_recovery_matrix(responses, shape=shape)
    target = matrix @ original.values

    recovered = recover_spectrum_from_responses(target, responses, shape=shape)
    closed = matrix @ recovered.values

    assert np.allclose(closed, target, atol=2e-4)


def test_recover_spectrum_batch_returns_multi_spectral_distribution() -> None:
    shape = SpectralShape(400, 700, 1)
    original = _gaussian_spectrum()
    target_1 = emission_to_XYZ(original, shape=shape)
    target_2 = 0.5 * target_1
    targets = np.vstack([target_1, target_2])

    recovered = recover_spectrum_from_XYZ(
        targets,
        shape=shape,
        labels=("full", "half"),
    )

    assert isinstance(recovered, MultiSpectralDistribution)
    assert recovered.labels == ("full", "half")
    closed = emission_to_XYZ(recovered, shape=shape)
    assert np.allclose(closed, targets, atol=3e-4)


def test_recover_spectrum_from_LMS_accepts_object_fundamentals() -> None:
    shape = SpectralShape(400, 700, 1)
    fundamentals = from_cie2006_lms_2degree_fundamentals().reshape(shape)
    target = np.array([20.0, 15.0, 5.0])

    recovered = recover_spectrum_from_LMS(
        target,
        fundamentals=fundamentals,
        shape=shape,
    )

    assert isinstance(recovered, SpectralDistribution)
    assert recovered.values.shape == recovered.wavelengths.shape
