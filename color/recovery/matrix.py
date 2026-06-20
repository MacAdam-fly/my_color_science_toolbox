"""Matrices for reflectance recovery."""

from __future__ import annotations

from typing import Union

import numpy as np

from color.colorimetry.integration import _intersection_shape
from color.math import quadrature_weights
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)


ResponseSource = Union[str, MultiSpectralDistribution]
IlluminantSource = Union[str, SpectralDistribution]


def _load_cmfs(cmfs: ResponseSource) -> MultiSpectralDistribution:
    """Return XYZ colour matching functions from an object or dataset name."""
    if isinstance(cmfs, MultiSpectralDistribution):
        return cmfs
    return from_dataset("standard_observers.cmfs", cmfs)


def _load_illuminant(illuminant: IlluminantSource) -> SpectralDistribution:
    """Return an illuminant SPD from an object or dataset name."""
    if isinstance(illuminant, SpectralDistribution):
        return illuminant
    return from_dataset("illuminants", illuminant)


def _shape_from_wavelengths(wavelengths: np.ndarray) -> SpectralShape:
    """Return a regular shape covering *wavelengths*."""
    intervals = np.diff(wavelengths)
    interval = float(intervals.min()) if intervals.size else 1.0
    return SpectralShape(float(wavelengths[0]), float(wavelengths[-1]), interval)


def response_recovery_matrix(
    responses: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, SpectralShape]:
    """Return ``(A, wavelengths, shape)`` for ``target = A @ spectrum``."""
    if len(responses.labels) != 3:
        raise ValueError(
            "responses must contain exactly three channels, "
            f"got {len(responses.labels)}"
        )
    common_shape = shape or _shape_from_wavelengths(responses.wavelengths)
    aligned_responses = responses.align(
        common_shape,
        extrapolator="fill",
        fill_value=0.0,
    )
    weights = quadrature_weights(
        common_shape.wavelengths,
        interval=common_shape.interval,
        quadrature="trapezoid",
    )
    matrix = float(k) * (weights[:, np.newaxis] * aligned_responses.values).T
    wavelengths = np.array(common_shape.wavelengths, copy=True)
    return matrix, wavelengths, common_shape


def reflectance_recovery_matrix(
    *,
    cmfs: ResponseSource = "cie1931_xyz_1nm",
    illuminant: IlluminantSource = "D65",
    shape: SpectralShape | None = None,
) -> tuple[np.ndarray, np.ndarray, SpectralShape]:
    """Return ``(A, wavelengths, shape)`` for ``XYZ = A @ reflectance``.

    The matrix follows the same trapezoid integration and reflectance
    normalisation used by ``color.colorimetry.reflectance_to_XYZ``.
    """
    cmfs_obj = _load_cmfs(cmfs)
    if cmfs_obj.labels != ("X", "Y", "Z"):
        raise ValueError("cmfs labels must be ('X', 'Y', 'Z')")

    illuminant_obj = _load_illuminant(illuminant)
    common_shape = shape or _intersection_shape(cmfs_obj, (illuminant_obj,))
    aligned_cmfs = cmfs_obj.align(
        common_shape,
        extrapolator="fill",
        fill_value=0.0,
    )
    aligned_illuminant = illuminant_obj.align(
        common_shape,
        extrapolator="fill",
        fill_value=0.0,
    )

    response_values = aligned_cmfs.values
    illuminant_values = aligned_illuminant.values
    weights = quadrature_weights(
        common_shape.wavelengths,
        interval=common_shape.interval,
        quadrature="trapezoid",
    )
    denominator = np.sum(weights * illuminant_values * response_values[:, 1])
    if denominator == 0:
        raise ZeroDivisionError("reflectance normalisation denominator is zero")

    k = 100.0 / denominator
    matrix = k * (weights[:, np.newaxis] * illuminant_values[:, np.newaxis] * response_values).T
    wavelengths = np.array(common_shape.wavelengths, copy=True)
    return matrix, wavelengths, common_shape


__all__ = [
    "ResponseSource",
    "IlluminantSource",
    "response_recovery_matrix",
    "reflectance_recovery_matrix",
]
