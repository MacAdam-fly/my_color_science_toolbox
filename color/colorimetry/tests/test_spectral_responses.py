"""Tests for spectral response integrations."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry.cone_responses import emission_to_lms, reflectance_to_lms
from color.colorimetry.integration import (
    LEGACY_PHOTOMETRY_POLICY,
    STANDARD_INTEGRATION_POLICY,
    SpectralIntegrationPolicy,
    integrate_response_products,
    integrate_responses,
)
from color.colorimetry.tristimulus import emission_to_xyz, reflectance_to_xyz
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)


def _identity_xyz_responses() -> MultiSpectralDistribution:
    return MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        ("X", "Y", "Z"),
    )


def _identity_lms_responses() -> MultiSpectralDistribution:
    return MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        ("l", "m", "s"),
    )


def test_emission_to_xyz_single_channel():
    spd = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])

    xyz = emission_to_xyz(spd, _identity_xyz_responses())

    np.testing.assert_allclose(xyz, [100.0, 200.0, 300.0])


def test_emission_to_xyz_multi_channel():
    spds = MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [
            [1.0, 2.0],
            [3.0, 4.0],
            [5.0, 6.0],
        ],
        ("a", "b"),
    )

    xyz = emission_to_xyz(spds, _identity_xyz_responses())

    np.testing.assert_allclose(
        xyz,
        [
            [100.0, 300.0, 500.0],
            [200.0, 400.0, 600.0],
        ],
    )


def test_reflectance_to_xyz_perfect_reflector_normalises_y_to_100():
    reflectance = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])
    illuminant = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])

    xyz = reflectance_to_xyz(reflectance, illuminant, _identity_xyz_responses())

    np.testing.assert_allclose(xyz, [100.0, 100.0, 100.0])


def test_reflectance_to_xyz_multi_channel():
    reflectance = MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [
            [1.0, 0.5],
            [1.0, 0.5],
            [1.0, 0.5],
        ],
        ("white", "gray"),
    )
    illuminant = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])

    xyz = reflectance_to_xyz(reflectance, illuminant, _identity_xyz_responses())

    np.testing.assert_allclose(
        xyz,
        [
            [100.0, 100.0, 100.0],
            [50.0, 50.0, 50.0],
        ],
    )


def test_lms_uses_same_response_integration_with_lms_labels():
    spd = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])

    lms = emission_to_lms(spd, _identity_lms_responses())

    np.testing.assert_allclose(lms, [100.0, 200.0, 300.0])


def test_integrate_response_products_rectangle_and_trapezoid():
    spd = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])
    response = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])

    rectangle = integrate_response_products(
        spd,
        response,
        policy=SpectralIntegrationPolicy(
            domain="response",
            quadrature="rectangle",
            extrapolator="fill",
            fill_value=0.0,
        ),
    )
    trapezoid = integrate_response_products(
        spd,
        response,
        policy=SpectralIntegrationPolicy(
            domain="response",
            quadrature="trapezoid",
            extrapolator="fill",
            fill_value=0.0,
        ),
    )

    assert rectangle == pytest.approx(600.0)
    assert trapezoid == pytest.approx(400.0)


def test_integrate_response_products_intersection_uses_response_grid():
    spd = SpectralDistribution([450.0, 500.0, 550.0], [1.0, 2.0, 3.0])
    response = SpectralDistribution(
        [400.0, 450.0, 500.0, 550.0, 600.0],
        [1.0, 1.0, 1.0, 1.0, 1.0],
    )

    value = integrate_response_products(
        spd,
        response,
        policy=STANDARD_INTEGRATION_POLICY,
    )

    assert value == pytest.approx(300.0)


def test_integrate_response_products_intersection_requires_overlap():
    spd = SpectralDistribution([700.0, 800.0], [1.0, 1.0])
    response = SpectralDistribution([400.0, 500.0], [1.0, 1.0])

    with pytest.raises(ValueError, match="overlap"):
        integrate_response_products(
            spd,
            response,
            policy=STANDARD_INTEGRATION_POLICY,
        )


def test_source_domain_reproduces_legacy_photometry_grid():
    spd = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])
    response = SpectralDistribution([400.0, 500.0, 600.0], [0.0, 0.5, 1.0])

    value = integrate_response_products(
        spd,
        response,
        policy=LEGACY_PHOTOMETRY_POLICY,
    )

    assert value == pytest.approx(250.0)


def test_reflectance_to_lms_defaults_to_middle_channel_normalisation():
    reflectance = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])
    illuminant = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])

    lms = reflectance_to_lms(reflectance, illuminant, _identity_lms_responses())

    np.testing.assert_allclose(lms, [100.0, 100.0, 100.0])


def test_emission_rejects_illuminant():
    spd = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])
    illuminant = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])

    with pytest.raises(ValueError, match="must not be provided"):
        integrate_responses(
            spd,
            _identity_xyz_responses(),
            mode="emission",
            illuminant=illuminant,
        )


def test_reflectance_requires_illuminant():
    reflectance = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])

    with pytest.raises(ValueError, match="illuminant is required"):
        integrate_responses(reflectance, _identity_xyz_responses(), mode="reflectance")


def test_xyz_requires_xyz_labels():
    spd = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])

    with pytest.raises(ValueError, match="responses labels"):
        emission_to_xyz(spd, _identity_lms_responses())


def test_real_dataset_reflectance_to_xyz_smoke():
    reflectance = SpectralDistribution(
        np.arange(360.0, 781.0, 1.0),
        np.ones(421),
    )
    illuminant = from_dataset("illuminants", "D65")
    cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")

    xyz = reflectance_to_xyz(
        reflectance,
        illuminant,
        cmfs,
        shape=SpectralShape(360.0, 780.0, 1.0),
    )

    assert xyz.shape == (3,)
    assert xyz[1] == pytest.approx(100.0)
