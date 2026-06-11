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
from .library import ReflectanceLibrary
from .methods import resolve_reflectance_recovery_method
from .options import (
    BoundedLeastSquaresOptions,
    Burns2019RecoveryOptions,
    DictionaryReflectanceOptions,
    Meng2015RecoveryOptions,
    PCAReflectanceOptions,
    ReflectanceRecoveryOption,
    SpectrumRecoveryOption,
    option_values,
)
from .spectrum import (
    as_recovery_targets,
    build_recovered_spectral_object,
    spectral_recovery_metadata,
)


_REFLECTANCE_METHOD_OPTIONS = {
    "bounded_least_squares": {"bounds", "smoothness"},
    "burns2019": {"bounds", "max_iterations", "tolerance"},
    "meng2015": {"bounds"},
    "pca": {"library", "bounds", "n_components", "coefficient_regularization"},
    "dictionary": {"library", "dictionary_regularization", "dictionary_top_k"},
}


def _reject_unknown_options(
    *,
    method_name: str,
    options: dict,
    allowed: set[str],
) -> None:
    if "library_datasets" in options:
        raise ValueError(
            "library_datasets is no longer accepted by reflectance recovery; "
            "call load_reflectance_library(...) first and pass library=..."
        )
    unknown = set(options) - allowed
    if unknown:
        names = ", ".join(sorted(unknown))
        allowed_names = ", ".join(sorted(allowed))
        raise ValueError(
            f"Unsupported option(s) for reflectance recovery method "
            f"{method_name!r}: {names}. Allowed options: {allowed_names}"
        )


def _validate_library(value: object) -> ReflectanceLibrary:
    if not isinstance(value, ReflectanceLibrary):
        raise ValueError(
            "PCA and dictionary reflectance recovery require a "
            "ReflectanceLibrary; call load_reflectance_library(...) first and "
            "pass library=..."
        )
    return value


def _normalise_reflectance_method(
    method: str | ReflectanceRecoveryOption,
    method_options: dict,
) -> tuple[str, dict]:
    if isinstance(method, SpectrumRecoveryOption) and not isinstance(
        method,
        BoundedLeastSquaresOptions,
    ):
        raise ValueError("spectrum recovery options cannot be used for reflectance recovery")

    if isinstance(method, ReflectanceRecoveryOption):
        if method_options:
            raise ValueError(
                "Do not pass method-specific keyword options together with a "
                "recovery options object"
            )
        method_name = method.method_name
        config = option_values(method)
        if isinstance(method, BoundedLeastSquaresOptions):
            config["bounds"] = (
                (0.0, 1.0) if config["bounds"] is None else config["bounds"]
            )
        elif isinstance(method, PCAReflectanceOptions):
            config["library"] = _validate_library(config["library"])
        elif isinstance(method, DictionaryReflectanceOptions):
            config["library"] = _validate_library(config["library"])
            config["dictionary_regularization"] = config.pop("regularization")
            config["dictionary_top_k"] = config.pop("top_k")
        elif isinstance(method, (Burns2019RecoveryOptions, Meng2015RecoveryOptions)):
            pass
        return method_name, config

    method_name, _solver = resolve_reflectance_recovery_method(method)
    if method_name == "bounded_least_squares":
        defaults = {"bounds": (0.0, 1.0), "smoothness": 1e-3}
    elif method_name == "burns2019":
        defaults = {"bounds": (0.0, 1.0), "max_iterations": 50, "tolerance": 1e-8}
    elif method_name == "meng2015":
        defaults = {"bounds": (0.0, 1.0)}
    elif method_name == "pca":
        defaults = {
            "library": None,
            "bounds": (0.0, 1.0),
            "n_components": 8,
            "coefficient_regularization": 1e-3,
        }
    else:
        defaults = {
            "library": None,
            "dictionary_regularization": 1e-6,
            "dictionary_top_k": 120,
        }
    allowed = _REFLECTANCE_METHOD_OPTIONS[method_name]
    _reject_unknown_options(
        method_name=method_name,
        options=method_options,
        allowed=allowed,
    )
    config = {**defaults, **method_options}
    if method_name in {"pca", "dictionary"}:
        config["library"] = _validate_library(config["library"])
    return method_name, config


def recover_reflectance_from_XYZ(
    XYZ: Sequence[float] | np.ndarray,
    *,
    cmfs: ResponseSource = "cie1931_xyz_1nm",
    illuminant: IlluminantSource = "D65",
    shape: SpectralShape | None = None,
    method: str | ReflectanceRecoveryOption = "burns2019",
    labels: Sequence[str] | None = None,
    **method_options,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover bounded reflectance spectra from XYZ values.

    Parameters
    ----------
    XYZ
        Target XYZ tristimulus values on the project Y=100 scale, with shape
        ``(3,)`` or ``(n, 3)``.
    cmfs
        XYZ colour matching functions as a dataset name or spectral object.
    illuminant
        Illuminant SPD as a dataset name or spectral object.
    shape
        Optional recovery wavelength sampling. Library-based methods require
        the library wavelengths to match the recovery matrix wavelengths.
    method
        Reflectance recovery method name or reflectance recovery options object.
        The default is ``"burns2019"``.
    labels
        Optional labels for batch recovery outputs.
    **method_options
        Method-specific keyword options for string method calls.

    Returns
    -------
    SpectralDistribution or MultiSpectralDistribution
        Recovered reflectance for one target or a multi-channel object for
        multiple targets.

    Notes
    -----
    This function solves for reflectance ``r`` in the same forward model used by
    ``reflectance_to_XYZ``. Do not recover an effective spectrum and divide by
    the illuminant when reflectance bounds or material-like curves matter.

    Examples
    --------
    >>> recover_reflectance_from_XYZ([24.0, 20.0, 18.0]).metadata["recovery_method"]
    'burns2019'
    """
    targets, is_single = as_recovery_targets(XYZ, name="XYZ")
    method_name, config = _normalise_reflectance_method(method, method_options)
    _resolved, solver = resolve_reflectance_recovery_method(method_name)
    uses_library = method_name in {"dictionary", "pca"}
    matrix_shape = shape
    if uses_library and matrix_shape is None:
        matrix_shape = config["library"].shape

    matrix, wavelengths, common_shape = reflectance_recovery_matrix(
        cmfs=cmfs,
        illuminant=illuminant,
        shape=matrix_shape,
    )
    if uses_library:
        library = config["library"]
        if not np.array_equal(library.wavelengths, wavelengths):
            raise ValueError(
                "library wavelengths must match the recovery matrix wavelengths"
            )
        if method_name == "pca":
            values = solver(
                targets,
                matrix,
                library=library,
                bounds=config["bounds"],
                n_components=config["n_components"],
                coefficient_regularization=config["coefficient_regularization"],
            )
        else:
            values = solver(
                targets,
                matrix,
                library=library,
                dictionary_regularization=config["dictionary_regularization"],
                dictionary_top_k=config["dictionary_top_k"],
            )
    elif method_name == "burns2019":
        values = solver(
            targets,
            matrix,
            bounds=config["bounds"],
            max_iterations=config["max_iterations"],
            tolerance=config["tolerance"],
        )
    else:
        values = solver(
            targets,
            matrix,
            bounds=config["bounds"],
            smoothness=config.get("smoothness"),
        )
    metadata = spectral_recovery_metadata(
        method=method_name,
        bounds=config.get("bounds", (0.0, 1.0)),
        smoothness=config.get("smoothness", 1e-3),
        shape=common_shape,
        recovery_kind="reflectance",
    )
    if uses_library:
        if library is None:
            raise ValueError("library is required for library-based recovery methods")
        metadata.update(
            {
                "library_datasets": library.metadata.get("datasets"),
                "library_sample_count": library.metadata.get("sample_count"),
            }
        )
    if method_name == "pca":
        metadata.update(
            {
                "n_components": int(config["n_components"]),
                "coefficient_regularization": float(
                    config["coefficient_regularization"]
                ),
            }
        )
    elif method_name == "dictionary":
        metadata.update(
            {
                "dictionary_regularization": float(config["dictionary_regularization"]),
                "dictionary_top_k": (
                    None
                    if config["dictionary_top_k"] is None
                    else int(config["dictionary_top_k"])
                ),
            }
        )
    elif method_name == "burns2019":
        metadata.update(
            {
                "reference": "Burns 2019 Method 3",
                "objective": "minimise_slope_energy_in_atanh_reflectance_space",
                "reflectance_transform": "rho=(tanh(z)+1)/2",
                "boundary_special_cases": "black_and_white",
            }
        )
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
    """Recover bounded reflectance spectra from xyY values.

    Parameters
    ----------
    xyY
        Target ``x, y, Y`` values with shape ``(3,)`` or ``(n, 3)``. ``Y`` uses
        the project Y=100 convention.
    **kwargs
        Forwarded to ``recover_reflectance_from_XYZ`` after converting xyY to
        XYZ.

    Returns
    -------
    SpectralDistribution or MultiSpectralDistribution
        Recovered reflectance.

    Notes
    -----
    This is a convenience wrapper; illuminant, CMFs and method semantics are
    identical to ``recover_reflectance_from_XYZ``.

    Examples
    --------
    >>> recover_reflectance_from_xyY([0.32, 0.31, 20.0]).metadata["recovery_kind"]
    'reflectance'
    """
    xyy, _ = as_recovery_targets(xyY, name="xyY")
    XYZ = xyY_to_XYZ(xyy)
    if np.asarray(xyY, dtype=np.float64).ndim == 1:
        XYZ = XYZ[0]
    return recover_reflectance_from_XYZ(XYZ, **kwargs)


__all__ = [
    "recover_reflectance_from_XYZ",
    "recover_reflectance_from_xyY",
]
