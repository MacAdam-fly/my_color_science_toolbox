"""Effective spectrum recovery from three-channel responses."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

from color.colorimetry import DEFAULT_CMFS
from color.colorimetry.cone_responses import DEFAULT_FUNDAMENTALS
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)
from color.utils.arrays import as_last_axis_triplets

from .matrix import ResponseSource, response_recovery_matrix
from .methods import resolve_spectrum_recovery_method


def as_recovery_targets(
    value: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> tuple[np.ndarray, bool]:
    """Return ``(targets, is_single)`` for one or more target triplets."""
    arr = as_last_axis_triplets(value, name=name)
    if arr.ndim == 1:
        return arr.reshape(1, 3), True
    if arr.ndim == 2:
        return arr, False
    raise ValueError(f"{name} must have shape (3,) or (n, 3)")


def validate_labels(labels: Sequence[str] | None, count: int) -> tuple[str, ...]:
    """Return channel labels for a batch recovery result."""
    if labels is None:
        return tuple(f"sample_{index}" for index in range(count))
    label_tuple = tuple(labels)
    if len(label_tuple) != count:
        raise ValueError("labels length must match the number of input samples")
    if len(set(label_tuple)) != len(label_tuple):
        raise ValueError("labels must be unique")
    return label_tuple


def spectral_recovery_metadata(
    *,
    method: str,
    bounds: Sequence[float],
    smoothness: float,
    shape: SpectralShape,
    recovery_kind: str,
) -> dict:
    """Return metadata for recovered spectral objects."""
    return {
        "recovery_kind": recovery_kind,
        "recovery_method": method,
        "bounds": tuple(float(item) for item in bounds),
        "smoothness": float(smoothness),
        "shape": {
            "start": shape.start,
            "end": shape.end,
            "interval": shape.interval,
        },
    }


def build_recovered_spectral_object(
    wavelengths: np.ndarray,
    values: np.ndarray,
    *,
    is_single: bool,
    labels: Sequence[str] | None,
    name: str,
    metadata: dict,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Return a single or multi-channel spectral recovery result."""
    if is_single:
        return SpectralDistribution(
            wavelengths,
            values[0],
            name=name,
            metadata=metadata,
        )

    channel_labels = validate_labels(labels, values.shape[0])
    return MultiSpectralDistribution(
        wavelengths,
        values.T,
        channel_labels,
        name=name,
        metadata=metadata,
    )


def _load_xyz_cmfs(cmfs: ResponseSource) -> MultiSpectralDistribution:
    """Return XYZ CMFs from an object or dataset name."""
    if isinstance(cmfs, MultiSpectralDistribution):
        return cmfs
    return from_dataset("standard_observers.cmfs", cmfs)


def _load_lms_fundamentals(
    fundamentals: ResponseSource,
    *,
    fill_nan: float | None,
) -> MultiSpectralDistribution:
    """Return LMS fundamentals from an object or dataset name."""
    if isinstance(fundamentals, MultiSpectralDistribution):
        return fundamentals
    return from_dataset(
        "standard_observers.cone_fundamentals",
        fundamentals,
        fill_nan=fill_nan,
    )


def recover_spectrum_from_responses(
    target: Sequence[float] | np.ndarray,
    responses: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    method: str = "bounded_least_squares",
    bounds: tuple[float, float] = (0.0, np.inf),
    smoothness: float = 1e-3,
    labels: Sequence[str] | None = None,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from arbitrary three-channel responses."""
    targets, is_single = as_recovery_targets(target, name="target")
    matrix, wavelengths, common_shape = response_recovery_matrix(
        responses,
        shape=shape,
    )
    method_name, solver = resolve_spectrum_recovery_method(method)
    values = solver(
        targets,
        matrix,
        bounds=bounds,
        smoothness=smoothness,
    )
    metadata = spectral_recovery_metadata(
        method=method_name,
        bounds=bounds,
        smoothness=smoothness,
        shape=common_shape,
        recovery_kind="spectrum",
    )
    metadata["responses_labels"] = responses.labels
    return build_recovered_spectral_object(
        wavelengths,
        values,
        is_single=is_single,
        labels=labels,
        name="Recovered spectrum",
        metadata=metadata,
    )


def recover_spectrum_from_XYZ(
    XYZ: Sequence[float] | np.ndarray,
    *,
    cmfs: ResponseSource = DEFAULT_CMFS,
    **kwargs,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from XYZ tristimulus values."""
    return recover_spectrum_from_responses(
        XYZ,
        _load_xyz_cmfs(cmfs),
        **kwargs,
    )


def recover_spectrum_from_LMS(
    LMS: Sequence[float] | np.ndarray,
    *,
    fundamentals: ResponseSource = DEFAULT_FUNDAMENTALS,
    fill_nan: float | None = 0.0,
    **kwargs,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from LMS cone responses."""
    return recover_spectrum_from_responses(
        LMS,
        _load_lms_fundamentals(fundamentals, fill_nan=fill_nan),
        **kwargs,
    )


__all__ = [
    "as_recovery_targets",
    "validate_labels",
    "spectral_recovery_metadata",
    "build_recovered_spectral_object",
    "recover_spectrum_from_responses",
    "recover_spectrum_from_XYZ",
    "recover_spectrum_from_LMS",
]
