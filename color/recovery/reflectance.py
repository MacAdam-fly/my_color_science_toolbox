"""Reflectance recovery from tristimulus values."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

from color.colorimetry import xyY_to_XYZ
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
)

from .matrix import IlluminantSource, ResponseSource, reflectance_recovery_matrix
from .methods import resolve_reflectance_recovery_method
from .spectrum import (
    as_recovery_targets,
    build_recovered_spectral_object,
    spectral_recovery_metadata,
)


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
    targets, is_single = as_recovery_targets(XYZ, name="XYZ")
    matrix, wavelengths, common_shape = reflectance_recovery_matrix(
        cmfs=cmfs,
        illuminant=illuminant,
        shape=shape,
    )
    method_name, solver = resolve_reflectance_recovery_method(method)
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
        recovery_kind="reflectance",
    )
    return build_recovered_spectral_object(
        wavelengths,
        values,
        is_single=is_single,
        labels=labels,
        name="Recovered reflectance",
        metadata=metadata,
    )


def recover_reflectance_from_xyY(
    xyY: Sequence[float] | np.ndarray,
    **kwargs,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover bounded smooth reflectance spectra from xyY values."""
    xyy, _ = as_recovery_targets(xyY, name="xyY")
    XYZ = xyY_to_XYZ(xyy)
    if np.asarray(xyY, dtype=np.float64).ndim == 1:
        XYZ = XYZ[0]
    return recover_reflectance_from_XYZ(XYZ, **kwargs)


__all__ = [
    "recover_reflectance_from_XYZ",
    "recover_reflectance_from_xyY",
]
