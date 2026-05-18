"""XYZ tristimulus value computations from spectral data."""

from __future__ import annotations

import numpy as np

from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape

from .spectral_responses import SpectralInput, _validate_responses, integrate_responses


def emission_to_xyz(
    spd: SpectralInput,
    cmfs: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert self-luminous spectral data to XYZ tristimulus values."""
    _validate_responses(cmfs, expected_labels=("X", "Y", "Z"))
    return integrate_responses(spd, cmfs, mode="emission", shape=shape, k=k)


def reflectance_to_xyz(
    reflectance: SpectralInput,
    illuminant: SpectralDistribution,
    cmfs: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert reflectance data under an illuminant to XYZ tristimulus values."""
    _validate_responses(cmfs, expected_labels=("X", "Y", "Z"))
    return integrate_responses(
        reflectance,
        cmfs,
        mode="reflectance",
        illuminant=illuminant,
        shape=shape,
        k=k,
        normalisation_channel="Y",
    )
