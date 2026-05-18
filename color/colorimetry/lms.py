"""LMS cone response computations from spectral data."""

from __future__ import annotations

import numpy as np

from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape

from .spectral_responses import SpectralInput, _validate_responses, integrate_responses


def emission_to_lms(
    spd: SpectralInput,
    fundamentals: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert self-luminous spectral data to LMS cone responses."""
    _validate_responses(fundamentals)
    return integrate_responses(spd, fundamentals, mode="emission", shape=shape, k=k)


def reflectance_to_lms(
    reflectance: SpectralInput,
    illuminant: SpectralDistribution,
    fundamentals: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float | None = None,
    normalisation_channel: str | int | None = None,
) -> np.ndarray:
    """Convert reflectance data under an illuminant to LMS cone responses.

    If ``k`` is omitted, the middle response channel is used for normalisation
    by default, usually ``m`` or ``M``.
    """
    _validate_responses(fundamentals)
    return integrate_responses(
        reflectance,
        fundamentals,
        mode="reflectance",
        illuminant=illuminant,
        shape=shape,
        k=k,
        normalisation_channel=normalisation_channel,
    )
