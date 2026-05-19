"""Tests for photometric functions and quantities."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import (
    DEFAULT_PHOTOPIC_K_M,
    DEFAULT_SCOTOPIC_K_M,
    luminous_efficacy,
    luminous_efficiency,
    luminous_flux,
    photopic_luminous_efficacy,
    photopic_luminous_efficiency,
    photopic_luminous_efficiency_function,
    photopic_luminous_flux,
    scotopic_luminous_efficacy,
    scotopic_luminous_efficiency,
    scotopic_luminous_efficiency_function,
    scotopic_luminous_flux,
)
from color.spectra import MultiSpectralDistribution, SpectralDistribution


def test_photopic_luminous_efficiency_function_default():
    lef = photopic_luminous_efficiency_function()

    assert isinstance(lef, SpectralDistribution)
    assert lef.name == "vl1924_1nm"
    assert lef.metadata["vision_regime"] == "photopic"
    assert np.all(lef.values >= 0)


def test_scotopic_luminous_efficiency_function_default():
    lef = scotopic_luminous_efficiency_function()

    assert isinstance(lef, SpectralDistribution)
    assert lef.name == "scotopic_v_1nm"
    assert lef.metadata["vision_regime"] == "scotopic"
    assert np.all(lef.values >= 0)


def test_luminous_flux_single_channel():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])
    lef = SpectralDistribution([400.0, 500.0, 600.0], [0.0, 0.5, 1.0])

    flux = luminous_flux(spectrum, lef, K_m=DEFAULT_PHOTOPIC_K_M)

    assert flux == pytest.approx(683.0 * 250.0)


def test_luminous_efficiency_single_channel():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])
    lef = SpectralDistribution([400.0, 500.0, 600.0], [0.0, 0.5, 1.0])

    efficiency = luminous_efficiency(spectrum, lef)

    assert efficiency == pytest.approx(0.625)


def test_luminous_efficacy_single_channel():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])
    lef = SpectralDistribution([400.0, 500.0, 600.0], [0.0, 0.5, 1.0])

    efficacy = luminous_efficacy(spectrum, lef, K_m=DEFAULT_PHOTOPIC_K_M)

    assert efficacy == pytest.approx(683.0 * 0.625)


def test_luminous_efficiency_uses_zero_outside_lef_domain():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 1.0, 1.0])
    lef = SpectralDistribution([450.0, 550.0], [1.0, 1.0])

    efficiency = luminous_efficiency(spectrum, lef)

    assert efficiency == pytest.approx(0.5)


def test_luminous_flux_multi_channel():
    spectrum = MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [
            [1.0, 2.0],
            [2.0, 2.0],
            [3.0, 2.0],
        ],
        ("a", "b"),
    )
    lef = SpectralDistribution([400.0, 500.0, 600.0], [0.0, 0.5, 1.0])

    flux = luminous_flux(spectrum, lef, K_m=1.0)

    np.testing.assert_allclose(flux, [250.0, 200.0])


def test_luminous_efficiency_zero_integral_raises():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [0.0, 0.0, 0.0])

    with pytest.raises(ZeroDivisionError, match="integral is zero"):
        luminous_efficiency(spectrum)


def test_photopic_wrappers_match_generic_functions():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])

    np.testing.assert_allclose(
        photopic_luminous_flux(spectrum),
        luminous_flux(
            spectrum,
            photopic_luminous_efficiency_function(),
            K_m=DEFAULT_PHOTOPIC_K_M,
        ),
    )
    np.testing.assert_allclose(
        photopic_luminous_efficiency(spectrum),
        luminous_efficiency(
            spectrum,
            photopic_luminous_efficiency_function(),
        ),
    )
    np.testing.assert_allclose(
        photopic_luminous_efficacy(spectrum),
        luminous_efficacy(
            spectrum,
            photopic_luminous_efficiency_function(),
            K_m=DEFAULT_PHOTOPIC_K_M,
        ),
    )


def test_scotopic_wrappers_match_generic_functions():
    spectrum = SpectralDistribution([400.0, 500.0, 600.0], [1.0, 2.0, 3.0])

    np.testing.assert_allclose(
        scotopic_luminous_flux(spectrum),
        luminous_flux(
            spectrum,
            scotopic_luminous_efficiency_function(),
            K_m=DEFAULT_SCOTOPIC_K_M,
        ),
    )
    np.testing.assert_allclose(
        scotopic_luminous_efficiency(spectrum),
        luminous_efficiency(
            spectrum,
            scotopic_luminous_efficiency_function(),
        ),
    )
    np.testing.assert_allclose(
        scotopic_luminous_efficacy(spectrum),
        luminous_efficacy(
            spectrum,
            scotopic_luminous_efficiency_function(),
            K_m=DEFAULT_SCOTOPIC_K_M,
        ),
    )
