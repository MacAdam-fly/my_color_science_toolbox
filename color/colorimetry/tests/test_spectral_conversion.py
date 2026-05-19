"""Tests for high-level spectral conversion helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import (
    emission_to_LMS,
    emission_to_XYZ,
    reflectance_to_LMS,
    reflectance_to_XYZ,
)
from color.colorimetry.lms import emission_to_lms, reflectance_to_lms
from color.colorimetry.xyz import emission_to_xyz, reflectance_to_xyz
from color.spectra import SpectralDistribution, SpectralShape, from_dataset


def test_emission_to_XYZ_matches_explicit_cmfs():
    shape = SpectralShape(400.0, 700.0, 10.0)
    sd = SpectralDistribution(shape.wavelengths, np.ones(len(shape)))
    cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")

    direct = emission_to_XYZ(sd, shape=shape)
    explicit = emission_to_xyz(sd, cmfs, shape=shape)

    np.testing.assert_allclose(direct, explicit)


def test_reflectance_to_XYZ_matches_explicit_illuminant_and_cmfs():
    shape = SpectralShape(400.0, 700.0, 10.0)
    reflectance = SpectralDistribution(shape.wavelengths, np.ones(len(shape)))
    illuminant = from_dataset("illuminants", "D65")
    cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")

    direct = reflectance_to_XYZ(reflectance, shape=shape)
    explicit = reflectance_to_xyz(reflectance, illuminant, cmfs, shape=shape)

    np.testing.assert_allclose(direct, explicit)
    assert direct[1] == pytest.approx(100.0)


def test_emission_to_LMS_loads_default_fundamentals_with_nan_fill():
    shape = SpectralShape(400.0, 700.0, 10.0)
    sd = SpectralDistribution(shape.wavelengths, np.ones(len(shape)))
    fundamentals = from_dataset(
        "standard_observers.cone_fundamentals",
        "cie2006_lms2_linE_1nm",
        fill_nan=0.0,
    )

    direct = emission_to_LMS(sd, shape=shape)
    explicit = emission_to_lms(sd, fundamentals, shape=shape)

    np.testing.assert_allclose(direct, explicit)
    assert np.all(np.isfinite(direct))


def test_reflectance_to_LMS_accepts_preloaded_sources():
    shape = SpectralShape(400.0, 700.0, 10.0)
    reflectance = SpectralDistribution(shape.wavelengths, np.ones(len(shape)))
    illuminant = from_dataset("illuminants", "D65")
    fundamentals = from_dataset(
        "standard_observers.cone_fundamentals",
        "cie2006_lms2_linE_1nm",
        fill_nan=0.0,
    )

    direct = reflectance_to_LMS(
        reflectance,
        illuminant=illuminant,
        fundamentals=fundamentals,
        shape=shape,
    )
    explicit = reflectance_to_lms(
        reflectance,
        illuminant,
        fundamentals,
        shape=shape,
    )

    np.testing.assert_allclose(direct, explicit)
    assert np.all(np.isfinite(direct))
