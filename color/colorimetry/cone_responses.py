"""LMS cone response computations from spectral data."""

from __future__ import annotations

from typing import Union

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)

from .integration import SpectralInput, _validate_responses, integrate_responses


ResponseSource = Union[str, MultiSpectralDistribution]
IlluminantSource = Union[str, SpectralDistribution]

DEFAULT_FUNDAMENTALS = "cie2006_lms2_linE_1nm"
DEFAULT_ILLUMINANT = "D65"


def _load_fundamentals(
    fundamentals: ResponseSource,
    *,
    fill_nan: float | None,
) -> MultiSpectralDistribution:
    """Return cone fundamentals from an object or dataset name."""
    if isinstance(fundamentals, MultiSpectralDistribution):
        return fundamentals
    return from_dataset(
        "standard_observers.cone_fundamentals",
        fundamentals,
        fill_nan=fill_nan,
    )


def _load_illuminant(illuminant: IlluminantSource) -> SpectralDistribution:
    """Return an illuminant SPD from an object or dataset name."""
    if isinstance(illuminant, SpectralDistribution):
        return illuminant
    return from_dataset("illuminants", illuminant)


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
    """Convert reflectance data under an illuminant to LMS cone responses."""
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


def emission_to_LMS(
    emission: SpectralInput,
    *,
    fundamentals: ResponseSource = DEFAULT_FUNDAMENTALS,
    shape: SpectralShape | None = None,
    k: float | None = None,
    fill_nan: float | None = 0.0,
) -> np.ndarray:
    """Convert self-luminous spectral data to LMS.

    By default, this uses
    ``standard_observers.cone_fundamentals/cie2006_lms2_linE_1nm`` with
    ``fill_nan=0.0``.
    """
    return emission_to_lms(
        emission,
        _load_fundamentals(fundamentals, fill_nan=fill_nan),
        shape=shape,
        k=k,
    )


def reflectance_to_LMS(
    reflectance: SpectralInput,
    *,
    illuminant: IlluminantSource = DEFAULT_ILLUMINANT,
    fundamentals: ResponseSource = DEFAULT_FUNDAMENTALS,
    shape: SpectralShape | None = None,
    k: float | None = None,
    fill_nan: float | None = 0.0,
    normalisation_channel: str | int | None = None,
) -> np.ndarray:
    """Convert reflectance data to LMS.

    By default, this uses ``illuminants/D65`` and
    ``standard_observers.cone_fundamentals/cie2006_lms2_linE_1nm`` with
    ``fill_nan=0.0``.
    """
    return reflectance_to_lms(
        reflectance,
        _load_illuminant(illuminant),
        _load_fundamentals(fundamentals, fill_nan=fill_nan),
        shape=shape,
        k=k,
        normalisation_channel=normalisation_channel,
    )


__all__ = [
    "DEFAULT_FUNDAMENTALS",
    "DEFAULT_ILLUMINANT",
    "emission_to_lms",
    "reflectance_to_lms",
    "emission_to_LMS",
    "reflectance_to_LMS",
]
