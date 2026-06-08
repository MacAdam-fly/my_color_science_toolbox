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
from .library import (
    DEFAULT_REFLECTANCE_LIBRARY_DATASETS,
    DEFAULT_REFLECTANCE_LIBRARY_SHAPE,
    ReflectanceLibrary,
    load_reflectance_library,
)
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
    library: ReflectanceLibrary | None = None,
    library_datasets: str | Sequence[str] = DEFAULT_REFLECTANCE_LIBRARY_DATASETS,
    n_components: int = 8,
    coefficient_regularization: float = 1e-3,
    dictionary_regularization: float = 1e-6,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover bounded smooth reflectance spectra from XYZ values."""
    targets, is_single = as_recovery_targets(XYZ, name="XYZ")
    method_name, solver = resolve_reflectance_recovery_method(method)
    uses_library = method_name in {"dictionary", "pca"}
    if uses_library and library is not None and not isinstance(library, ReflectanceLibrary):
        raise ValueError("library must be a ReflectanceLibrary instance")
    matrix_shape = shape
    if uses_library and matrix_shape is None:
        matrix_shape = library.shape if library is not None else DEFAULT_REFLECTANCE_LIBRARY_SHAPE

    matrix, wavelengths, common_shape = reflectance_recovery_matrix(
        cmfs=cmfs,
        illuminant=illuminant,
        shape=matrix_shape,
    )
    if uses_library:
        if library is None:
            library = load_reflectance_library(
                library_datasets,
                shape=common_shape,
            )
        if not np.array_equal(library.wavelengths, wavelengths):
            raise ValueError(
                "library wavelengths must match the recovery matrix wavelengths"
            )
        if method_name == "pca":
            values = solver(
                targets,
                matrix,
                library=library,
                bounds=bounds,
                n_components=n_components,
                coefficient_regularization=coefficient_regularization,
            )
        else:
            values = solver(
                targets,
                matrix,
                library=library,
                dictionary_regularization=dictionary_regularization,
            )
    else:
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
    if uses_library:
        assert library is not None
        metadata.update(
            {
                "library_datasets": library.metadata.get("datasets"),
                "library_sample_count": library.metadata.get("sample_count"),
            }
        )
    if method_name == "pca":
        metadata.update(
            {
                "n_components": int(n_components),
                "coefficient_regularization": float(coefficient_regularization),
            }
        )
    elif method_name == "dictionary":
        metadata["dictionary_regularization"] = float(dictionary_regularization)
    elif method_name == "meng2015":
        metadata.update(
            {
                "objective": "minimise_first_difference_energy",
                "closure_constraint": "exact_XYZ_equality",
            }
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
