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
    return integrate_responses(
        spd,
        fundamentals,
        mode="emission",
        shape=shape,
        k=k,
    )


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
    """Integrate a self-luminous spectrum to LMS cone responses.

    Parameters
    ----------
    emission
        Emission SPD as a ``SpectralDistribution`` or
        ``MultiSpectralDistribution``.
    fundamentals
        LMS cone fundamentals, either as a dataset name or a
        ``MultiSpectralDistribution``.
    shape
        Optional spectral shape used to align the SPD and fundamentals.
    k
        Optional scale factor. If omitted, no ``Y=100`` or LMS white
        normalisation is applied.
    fill_nan
        Replacement value used when loading fundamentals from a dataset name.
        The default treats missing S-cone long-wave tails as zero response.

    Returns
    -------
    ndarray
        LMS values. Single-channel input returns ``(3,)``; multi-channel
        input returns ``(n, 3)``.

    Notes
    -----
    This is a direct spectral response integral, not the matrix
    ``XYZ_to_LMS`` transform. Defaults use CIE 2006 2-degree energy-based LMS
    fundamentals.

    Examples
    --------
    >>> from color.generators import gaussian_spd
    >>> from color.spectra import from_columns
    >>> sd = from_columns(gaussian_spd(peak_wavelength=530), y="spd")
    >>> emission_to_LMS(sd).shape
    (3,)
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
    """Integrate a reflectance spectrum under an illuminant to LMS responses.

    Parameters
    ----------
    reflectance
        Reflectance factor spectrum as a ``SpectralDistribution`` or
        ``MultiSpectralDistribution``.
    illuminant
        Illuminant SPD, either as a dataset name such as ``"D65"`` or a
        ``SpectralDistribution``.
    fundamentals
        LMS cone fundamentals, either as a dataset name or a
        ``MultiSpectralDistribution``.
    shape
        Optional spectral shape used to align reflectance, illuminant and
        fundamentals.
    k
        Optional scale factor. If omitted, a white-normalising factor is
        computed from the illuminant and chosen response channel.
    fill_nan
        Replacement value used when loading fundamentals from a dataset name.
    normalisation_channel
        Response label or channel index used for the reflectance white
        normalisation. If omitted, the integration core uses its default
        channel choice.

    Returns
    -------
    ndarray
        LMS values. Single-channel input returns ``(3,)``; multi-channel
        input returns ``(n, 3)``.

    Notes
    -----
    Reflectance LMS integrates
    ``reflectance * illuminant * fundamentals``. It is not equivalent to
    converting the resulting XYZ through a fixed matrix unless the same
    observer definitions and normalisation semantics are being used.

    Examples
    --------
    >>> from color.datasets import get_color_card
    >>> from color.spectra import from_columns
    >>> raw = get_color_card("pmc")
    >>> patch = from_columns(raw, y="Foliage")
    >>> reflectance_to_LMS(patch, illuminant="D65").shape
    (3,)
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
