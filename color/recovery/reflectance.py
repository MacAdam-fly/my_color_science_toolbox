"""Reflectance recovery from tristimulus values."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np
from scipy.optimize import lsq_linear

from color.colorimetry import xyY_to_XYZ
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
)
from color.utils.arrays import as_last_axis_triplets
from color.utils.names import canonical_method_name

from .matrix import IlluminantSource, ResponseSource, reflectance_recovery_matrix
from .matrix import second_difference_matrix


def _as_xyz_targets(
    value: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> tuple[np.ndarray, bool]:
    """Return ``(targets, is_single)`` for one or more XYZ-like triplets."""
    arr = as_last_axis_triplets(value, name=name)
    if arr.ndim == 1:
        return arr.reshape(1, 3), True
    if arr.ndim == 2:
        return arr, False
    raise ValueError(f"{name} must have shape (3,) or (n, 3)")


def _validate_bounds(bounds: tuple[float, float]) -> tuple[float, float]:
    """Validate reflectance bounds."""
    if len(bounds) != 2:
        raise ValueError("bounds must contain exactly two values")
    lower, upper = (float(bounds[0]), float(bounds[1]))
    if not np.isfinite([lower, upper]).all():
        raise ValueError("bounds must be finite")
    if lower >= upper:
        raise ValueError("bounds lower value must be less than upper value")
    return lower, upper


def _validate_labels(labels: Sequence[str] | None, count: int) -> tuple[str, ...]:
    """Return channel labels for a batch recovery result."""
    if labels is None:
        return tuple(f"sample_{index}" for index in range(count))
    label_tuple = tuple(labels)
    if len(label_tuple) != count:
        raise ValueError("labels length must match the number of input samples")
    if len(set(label_tuple)) != len(label_tuple):
        raise ValueError("labels must be unique")
    return label_tuple


def _solve_reflectance_targets(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    bounds: tuple[float, float],
    smoothness: float,
) -> np.ndarray:
    """Solve bounded smooth reflectance spectra for all target XYZ rows."""
    lower, upper = _validate_bounds(bounds)
    smoothness_value = float(smoothness)
    if not np.isfinite(smoothness_value) or smoothness_value < 0:
        raise ValueError("smoothness must be a finite non-negative value")

    if smoothness_value > 0:
        difference = second_difference_matrix(matrix.shape[1])
        lhs = np.vstack((matrix, np.sqrt(smoothness_value) * difference))
        zero_tail = np.zeros(difference.shape[0], dtype=np.float64)
    else:
        lhs = matrix
        zero_tail = np.empty(0, dtype=np.float64)

    recovered = []
    for target in targets:
        rhs = np.concatenate((target, zero_tail))
        result = lsq_linear(lhs, rhs, bounds=(lower, upper))
        recovered.append(result.x)
    return np.asarray(recovered, dtype=np.float64)


def recover_reflectance_from_XYZ(
    XYZ: Sequence[float] | np.ndarray,
    *,
    cmfs: ResponseSource = "cie1931_xyz_1nm",
    illuminant: IlluminantSource = "D65",
    shape: SpectralShape | None = None,
    method: str = "bounded_least_squares",
    bounds: tuple[float, float] = (0.0, 1.0),
    smoothness: float = 1e-3,
    labels: Sequence[str] | None = None,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover bounded smooth reflectance spectra from XYZ values."""
    if canonical_method_name(method) != "boundedleastsquares":
        raise ValueError("method must be 'bounded_least_squares'")

    targets, is_single = _as_xyz_targets(XYZ, name="XYZ")
    matrix, wavelengths, common_shape = reflectance_recovery_matrix(
        cmfs=cmfs,
        illuminant=illuminant,
        shape=shape,
    )
    values = _solve_reflectance_targets(
        targets,
        matrix,
        bounds=bounds,
        smoothness=smoothness,
    )
    metadata = {
        "recovery_method": "bounded_least_squares",
        "bounds": tuple(float(item) for item in bounds),
        "smoothness": float(smoothness),
        "shape": {
            "start": common_shape.start,
            "end": common_shape.end,
            "interval": common_shape.interval,
        },
    }

    if is_single:
        return SpectralDistribution(
            wavelengths,
            values[0],
            name="Recovered reflectance",
            metadata=metadata,
        )

    channel_labels = _validate_labels(labels, values.shape[0])
    return MultiSpectralDistribution(
        wavelengths,
        values.T,
        channel_labels,
        name="Recovered reflectance",
        metadata=metadata,
    )


def recover_reflectance_from_xyY(
    xyY: Sequence[float] | np.ndarray,
    **kwargs,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover bounded smooth reflectance spectra from xyY values."""
    xyy, _ = _as_xyz_targets(xyY, name="xyY")
    XYZ = xyY_to_XYZ(xyy)
    if np.asarray(xyY, dtype=np.float64).ndim == 1:
        XYZ = XYZ[0]
    return recover_reflectance_from_XYZ(XYZ, **kwargs)


__all__ = [
    "recover_reflectance_from_XYZ",
    "recover_reflectance_from_xyY",
]
