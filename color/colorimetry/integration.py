"""Shared spectral integration against three-channel response functions."""

from __future__ import annotations

from typing import Literal, Union

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
)


SpectralInput = Union[SpectralDistribution, MultiSpectralDistribution]
Mode = Literal["emission", "reflectance"]


def _shape_from_wavelengths(wavelengths: np.ndarray) -> SpectralShape:
    """Return a regular spectral shape covering *wavelengths*."""
    intervals = np.diff(wavelengths)
    interval = float(intervals.min()) if intervals.size else 1.0
    return SpectralShape(float(wavelengths[0]), float(wavelengths[-1]), interval)


def _align_single(
    sd: SpectralDistribution,
    shape: SpectralShape,
) -> SpectralDistribution:
    """Align a single-channel spectrum to *shape*."""
    return sd.align(shape)


def _align_multi(
    msd: MultiSpectralDistribution,
    shape: SpectralShape,
) -> MultiSpectralDistribution:
    """Align a multi-channel spectrum to *shape*."""
    return msd.align(shape)


def _as_source_matrix(spectrum: SpectralInput) -> tuple[np.ndarray, tuple[str, ...] | None]:
    """Return source values as ``(n_sources, n_wavelengths)``."""
    if isinstance(spectrum, SpectralDistribution):
        return spectrum.values.reshape(1, -1), None
    return spectrum.values.T, spectrum.labels


def _validate_responses(
    responses: MultiSpectralDistribution,
    *,
    expected_labels: tuple[str, str, str] | None = None,
) -> None:
    """Validate three-channel spectral response functions."""
    if len(responses.labels) != 3:
        raise ValueError(
            "responses must contain exactly three channels, "
            f"got {len(responses.labels)}"
        )
    if expected_labels is not None and responses.labels != expected_labels:
        raise ValueError(
            f"responses labels must be {expected_labels}, got {responses.labels}"
        )


def _normalisation_channel_index(
    responses: MultiSpectralDistribution,
    normalisation_channel: str | int | None,
) -> int:
    """Resolve the response channel used for reflectance normalisation."""
    if normalisation_channel is None:
        return 1
    if isinstance(normalisation_channel, int):
        if normalisation_channel < 0 or normalisation_channel >= len(responses.labels):
            raise ValueError("normalisation_channel index is out of range")
        return normalisation_channel
    if normalisation_channel not in responses.labels:
        raise ValueError(
            f"normalisation_channel {normalisation_channel!r} is not in "
            f"responses labels {responses.labels}"
        )
    return responses.labels.index(normalisation_channel)


def integrate_responses(
    spectrum: SpectralInput,
    responses: MultiSpectralDistribution,
    *,
    mode: Mode,
    illuminant: SpectralDistribution | None = None,
    shape: SpectralShape | None = None,
    k: float | None = None,
    normalisation_channel: str | int | None = None,
    output_scale: float = 100.0,
) -> np.ndarray:
    """Integrate spectra against three-channel response functions."""
    _validate_responses(responses)
    if mode == "reflectance" and illuminant is None:
        raise ValueError("illuminant is required for reflectance mode")
    if mode == "emission" and illuminant is not None:
        raise ValueError("illuminant must not be provided for emission mode")

    common_shape = shape or _shape_from_wavelengths(responses.wavelengths)
    aligned_spectrum = (
        _align_single(spectrum, common_shape)
        if isinstance(spectrum, SpectralDistribution)
        else _align_multi(spectrum, common_shape)
    )
    aligned_responses = _align_multi(responses, common_shape)

    source_values, source_labels = _as_source_matrix(aligned_spectrum)
    response_values = aligned_responses.values
    interval = common_shape.interval

    if mode == "reflectance":
        assert illuminant is not None
        aligned_illuminant = _align_single(illuminant, common_shape)
        source_values = source_values * aligned_illuminant.values.reshape(1, -1)
        if k is None:
            norm_index = _normalisation_channel_index(
                aligned_responses,
                normalisation_channel,
            )
            denominator = (
                np.sum(aligned_illuminant.values * response_values[:, norm_index])
                * interval
            )
            if denominator == 0:
                raise ZeroDivisionError("reflectance normalisation denominator is zero")
            k_value = output_scale / denominator
        else:
            k_value = float(k)
    else:
        k_value = 1.0 if k is None else float(k)

    result = k_value * (source_values @ response_values) * interval
    if source_labels is None:
        return result[0]
    return result


__all__ = [
    "SpectralInput",
    "Mode",
    "integrate_responses",
]
