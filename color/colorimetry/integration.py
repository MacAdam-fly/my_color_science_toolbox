"""Shared spectral integration against spectral response functions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
)


SpectralInput = Union[SpectralDistribution, MultiSpectralDistribution]
Mode = Literal["emission", "reflectance"]
IntegrationDomain = Literal["response", "source", "intersection"]
Quadrature = Literal["rectangle", "trapezoid"]
Extrapolator = Literal["constant", "fill"]


@dataclass(frozen=True)
class SpectralIntegrationPolicy:
    """Integration grid, quadrature and extrapolation policy."""

    domain: IntegrationDomain
    quadrature: Quadrature
    extrapolator: Extrapolator
    fill_value: float = 0.0


LEGACY_COLORIMETRY_POLICY = SpectralIntegrationPolicy(
    domain="response",
    quadrature="rectangle",
    extrapolator="constant",
    fill_value=np.nan,
)
"""Legacy colour-response policy used by existing XYZ/LMS integrations."""

LEGACY_PHOTOMETRY_POLICY = SpectralIntegrationPolicy(
    domain="source",
    quadrature="trapezoid",
    extrapolator="fill",
    fill_value=0.0,
)
"""Legacy photometry policy used by existing luminous quantity helpers."""

STANDARD_INTEGRATION_POLICY = SpectralIntegrationPolicy(
    domain="intersection",
    quadrature="rectangle",
    extrapolator="fill",
    fill_value=0.0,
)
"""Recommended policy for new code that needs consistent spectral products."""


def _shape_from_wavelengths(wavelengths: np.ndarray) -> SpectralShape:
    """Return a regular spectral shape covering *wavelengths*."""
    intervals = np.diff(wavelengths)
    interval = float(intervals.min()) if intervals.size else 1.0
    return SpectralShape(float(wavelengths[0]), float(wavelengths[-1]), interval)


def _shape_from_source(spectrum: SpectralInput) -> SpectralShape:
    """Return a regular shape covering the input spectrum wavelengths."""
    return _shape_from_wavelengths(spectrum.wavelengths)


def _intersection_shape(
    responses: SpectralDistribution | MultiSpectralDistribution,
    spectra: tuple[SpectralInput | SpectralDistribution, ...],
) -> SpectralShape:
    """Return a response-grid shape covering the overlap of all spectra."""
    starts = [float(responses.wavelengths[0])]
    ends = [float(responses.wavelengths[-1])]
    for spectrum in spectra:
        starts.append(float(spectrum.wavelengths[0]))
        ends.append(float(spectrum.wavelengths[-1]))

    start = max(starts)
    end = min(ends)
    if start > end:
        raise ValueError("spectral domains do not overlap")

    base_shape = _shape_from_wavelengths(responses.wavelengths)
    wavelengths = base_shape.wavelengths
    mask = (wavelengths >= start) & (wavelengths <= end)
    if not np.any(mask):
        raise ValueError("spectral domains do not overlap on the response grid")
    selected = wavelengths[mask]
    return SpectralShape(float(selected[0]), float(selected[-1]), base_shape.interval)


def _integration_shape(
    spectrum: SpectralInput,
    responses: SpectralDistribution | MultiSpectralDistribution,
    *,
    shape: SpectralShape | None,
    policy: SpectralIntegrationPolicy,
    extra_spectra: tuple[SpectralDistribution, ...] = (),
) -> SpectralShape:
    """Return the effective integration shape for the policy."""
    if shape is not None:
        return shape
    if policy.domain == "source":
        return _shape_from_source(spectrum)
    if policy.domain == "intersection":
        return _intersection_shape(responses, (spectrum, *extra_spectra))
    return _shape_from_wavelengths(responses.wavelengths)


def _align_single(
    sd: SpectralDistribution,
    shape: SpectralShape,
    policy: SpectralIntegrationPolicy = LEGACY_COLORIMETRY_POLICY,
) -> SpectralDistribution:
    """Align a single-channel spectrum to *shape*."""
    return sd.align(
        shape,
        extrapolator=policy.extrapolator,
        fill_value=policy.fill_value,
    )


def _align_multi(
    msd: MultiSpectralDistribution,
    shape: SpectralShape,
    policy: SpectralIntegrationPolicy = LEGACY_COLORIMETRY_POLICY,
) -> MultiSpectralDistribution:
    """Align a multi-channel spectrum to *shape*."""
    return msd.align(
        shape,
        extrapolator=policy.extrapolator,
        fill_value=policy.fill_value,
    )


def _as_source_matrix(spectrum: SpectralInput) -> tuple[np.ndarray, tuple[str, ...] | None]:
    """Return source values as ``(n_sources, n_wavelengths)``."""
    if isinstance(spectrum, SpectralDistribution):
        return spectrum.values.reshape(1, -1), None
    return spectrum.values.T, spectrum.labels


def _as_response_matrix(
    responses: SpectralDistribution | MultiSpectralDistribution,
) -> np.ndarray:
    """Return response values as ``(n_wavelengths, n_responses)``."""
    if isinstance(responses, SpectralDistribution):
        return responses.values.reshape(-1, 1)
    return responses.values


def _integrate_values(
    products: np.ndarray,
    wavelengths: np.ndarray,
    *,
    interval: float,
    quadrature: Quadrature,
) -> np.ndarray:
    """Integrate product rows over wavelength."""
    axis = 0 if products.ndim == 1 else 1
    if quadrature == "trapezoid":
        return _trapezoid(products, wavelengths, axis=axis)
    return np.sum(products, axis=axis) * interval


def _trapezoid(values: np.ndarray, wavelengths: np.ndarray, *, axis: int) -> np.ndarray:
    """Return trapezoidal integration across NumPy versions."""
    trapezoid = getattr(np, "trapezoid", np.trapz)
    return trapezoid(values, wavelengths, axis=axis)


def _quadrature_weights(
    wavelengths: np.ndarray,
    *,
    interval: float,
    quadrature: Quadrature,
) -> np.ndarray:
    """Return per-wavelength weights matching the quadrature rule."""
    if quadrature == "rectangle":
        return np.full(wavelengths.shape, interval, dtype=np.float64)
    weights = np.zeros(wavelengths.shape, dtype=np.float64)
    if wavelengths.size > 1:
        deltas = np.diff(wavelengths)
        weights[0] = deltas[0] / 2.0
        weights[-1] = deltas[-1] / 2.0
        if wavelengths.size > 2:
            weights[1:-1] = (deltas[:-1] + deltas[1:]) / 2.0
    return weights


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


def integrate_response_products(
    spectrum: SpectralInput,
    responses: SpectralDistribution | MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    policy: SpectralIntegrationPolicy = STANDARD_INTEGRATION_POLICY,
) -> np.ndarray:
    """Integrate one or more spectra against one or more response functions."""
    common_shape = _integration_shape(
        spectrum,
        responses,
        shape=shape,
        policy=policy,
    )
    aligned_spectrum = (
        _align_single(spectrum, common_shape, policy)
        if isinstance(spectrum, SpectralDistribution)
        else _align_multi(spectrum, common_shape, policy)
    )
    aligned_responses = (
        _align_single(responses, common_shape, policy)
        if isinstance(responses, SpectralDistribution)
        else _align_multi(responses, common_shape, policy)
    )

    source_values, source_labels = _as_source_matrix(aligned_spectrum)
    response_values = _as_response_matrix(aligned_responses)
    products = source_values[:, :, np.newaxis] * response_values[np.newaxis, :, :]
    result = _integrate_values(
        products,
        common_shape.wavelengths,
        interval=common_shape.interval,
        quadrature=policy.quadrature,
    )
    if isinstance(responses, SpectralDistribution):
        result = result[:, 0]
    if source_labels is None:
        return result[0]
    return result


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
    integration_policy: SpectralIntegrationPolicy | None = None,
) -> np.ndarray:
    """Integrate spectra against three-channel response functions."""
    policy = integration_policy or LEGACY_COLORIMETRY_POLICY
    _validate_responses(responses)
    if mode == "reflectance" and illuminant is None:
        raise ValueError("illuminant is required for reflectance mode")
    if mode == "emission" and illuminant is not None:
        raise ValueError("illuminant must not be provided for emission mode")

    common_shape = _integration_shape(
        spectrum,
        responses,
        shape=shape,
        policy=policy,
        extra_spectra=(illuminant,) if illuminant is not None else (),
    )
    aligned_spectrum = (
        _align_single(spectrum, common_shape, policy)
        if isinstance(spectrum, SpectralDistribution)
        else _align_multi(spectrum, common_shape, policy)
    )
    aligned_responses = _align_multi(responses, common_shape, policy)

    source_values, source_labels = _as_source_matrix(aligned_spectrum)
    response_values = aligned_responses.values

    if mode == "reflectance":
        if illuminant is None:
            raise ValueError("illuminant is required for reflectance mode")
        aligned_illuminant = _align_single(illuminant, common_shape, policy)
        source_values = source_values * aligned_illuminant.values.reshape(1, -1)
        if k is None:
            norm_index = _normalisation_channel_index(
                aligned_responses,
                normalisation_channel,
            )
            denominator = _integrate_values(
                (
                    aligned_illuminant.values.reshape(1, -1)
                    * response_values[:, norm_index].reshape(1, -1)
                ),
                common_shape.wavelengths,
                interval=common_shape.interval,
                quadrature=policy.quadrature,
            )
            denominator = float(denominator[0])
            if denominator == 0:
                raise ZeroDivisionError("reflectance normalisation denominator is zero")
            k_value = output_scale / denominator
        else:
            k_value = float(k)
    else:
        k_value = 1.0 if k is None else float(k)

    products = source_values[:, :, np.newaxis] * response_values[np.newaxis, :, :]
    result = k_value * _integrate_values(
        products,
        common_shape.wavelengths,
        interval=common_shape.interval,
        quadrature=policy.quadrature,
    )
    if source_labels is None:
        return result[0]
    return result


__all__ = [
    "SpectralInput",
    "Mode",
    "SpectralIntegrationPolicy",
    "STANDARD_INTEGRATION_POLICY",
    "LEGACY_COLORIMETRY_POLICY",
    "LEGACY_PHOTOMETRY_POLICY",
    "integrate_response_products",
    "integrate_responses",
]
