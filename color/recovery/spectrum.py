"""Effective spectrum recovery from three-channel responses."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

from color.colorimetry import DEFAULT_CMFS, XYZ_to_xy, analyze_chromaticity, xyY_to_XYZ
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
from .options import (
    AutoGaussianRecoveryOptions,
    BoundedLeastSquaresOptions,
    GaussianRecoveryOptions,
    MultiGaussianRecoveryOptions,
    ReflectanceRecoveryOption,
    SpectrumRecoveryOption,
    option_values,
)
from .parametric import ParametricRecoveryResult


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


_SPECTRUM_PARAMETRIC_DEFAULTS = {
    "amplitude_bounds": (0.0, np.inf),
    "center_bounds": None,
    "sigma_bounds": (2.0, 120.0),
    "center_initials": None,
    "error": "relative",
    "use_dominant_wavelength_initial": True,
    "whitepoint_xy": (0.3127, 0.3290),
    "dominant_region": None,
    "dominant_wavelength_nm": None,
    "dominant_wavelength_initial_used": False,
}

_SPECTRUM_METHOD_OPTIONS = {
    "bounded_least_squares": {"bounds", "smoothness"},
    "gaussian": {
        "amplitude_bounds",
        "center_bounds",
        "sigma_bounds",
        "center_initials",
        "error",
        "use_dominant_wavelength_initial",
        "whitepoint_xy",
    },
    "multi_gaussian": {
        "amplitude_bounds",
        "center_bounds",
        "sigma_bounds",
        "center_initials",
        "error",
        "n_components",
        "use_dominant_wavelength_initial",
        "whitepoint_xy",
    },
    "auto_gaussian": {
        "amplitude_bounds",
        "center_bounds",
        "sigma_bounds",
        "center_initials",
        "error",
        "n_components",
        "use_dominant_wavelength_initial",
        "whitepoint_xy",
    },
}


def _reject_unknown_options(
    *,
    method_name: str,
    options: dict,
    allowed: set[str],
) -> None:
    unknown = set(options) - allowed
    if unknown:
        names = ", ".join(sorted(unknown))
        allowed_names = ", ".join(sorted(allowed))
        raise ValueError(
            f"Unsupported option(s) for spectrum recovery method "
            f"{method_name!r}: {names}. Allowed options: {allowed_names}"
        )


def _normalise_spectrum_method(
    method: str | SpectrumRecoveryOption,
    method_options: dict,
) -> tuple[str, dict]:
    if isinstance(method, ReflectanceRecoveryOption) and not isinstance(
        method,
        BoundedLeastSquaresOptions,
    ):
        raise ValueError("reflectance recovery options cannot be used for spectrum recovery")

    if isinstance(method, SpectrumRecoveryOption):
        if method_options:
            raise ValueError(
                "Do not pass method-specific keyword options together with a "
                "recovery options object"
            )
        method_name = method.method_name
        config = option_values(method)
        if isinstance(method, BoundedLeastSquaresOptions):
            config["bounds"] = (
                (0.0, np.inf) if config["bounds"] is None else config["bounds"]
            )
            return method_name, config
        config = {**_SPECTRUM_PARAMETRIC_DEFAULTS, **config}
        if isinstance(method, (MultiGaussianRecoveryOptions, AutoGaussianRecoveryOptions)):
            config.setdefault("n_components", 2)
        return method_name, config

    method_name, _solver = resolve_spectrum_recovery_method(method)
    if method_name == "bounded_least_squares":
        defaults = {"bounds": (0.0, np.inf), "smoothness": 1e-3}
    else:
        defaults = dict(_SPECTRUM_PARAMETRIC_DEFAULTS)
        if method_name in {"multi_gaussian", "auto_gaussian"}:
            defaults["n_components"] = 2
    allowed = _SPECTRUM_METHOD_OPTIONS[method_name]
    _reject_unknown_options(
        method_name=method_name,
        options=method_options,
        allowed=allowed,
    )
    return method_name, {**defaults, **method_options}


def _recover_spectrum_from_responses_resolved(
    target: Sequence[float] | np.ndarray,
    responses: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None,
    method_name: str,
    config: dict,
    labels: Sequence[str] | None,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    targets, is_single = as_recovery_targets(target, name="target")
    matrix, wavelengths, common_shape = response_recovery_matrix(
        responses,
        shape=shape,
    )
    _resolved, solver = resolve_spectrum_recovery_method(method_name)
    selected_method = method_name
    selection_reason = None
    if method_name == "auto_gaussian":
        if config.get("dominant_region") == "spectral":
            selected_method = "gaussian"
            selection_reason = "spectral_dominant_wavelength"
        else:
            selected_method = "multi_gaussian"
            selection_reason = config.get("dominant_region") or "no_chromaticity_analysis"
        _resolved, solver = resolve_spectrum_recovery_method(selected_method)

    if selected_method in {"gaussian", "multi_gaussian"}:
        result = solver(
            targets,
            matrix,
            wavelengths=wavelengths,
            amplitude_bounds=config["amplitude_bounds"],
            center_bounds=config["center_bounds"],
            sigma_bounds=config["sigma_bounds"],
            center_initials=config["center_initials"],
            error=config["error"],
            n_components=config.get("n_components", 2),
            dominant_region=config.get("dominant_region"),
        )
        if not isinstance(result, ParametricRecoveryResult):
            raise TypeError("parametric recovery solver returned an invalid result")
        values = result.values
        parametric_metadata = result.metadata
    else:
        values = solver(
            targets,
            matrix,
            bounds=config["bounds"],
            smoothness=config["smoothness"],
        )
        parametric_metadata = {}
    metadata = spectral_recovery_metadata(
        method=method_name,
        bounds=config.get("bounds", (0.0, np.inf)),
        smoothness=config.get("smoothness", 1e-3),
        shape=common_shape,
        recovery_kind="spectrum",
    )
    metadata["responses_labels"] = responses.labels
    if parametric_metadata:
        metadata.update(parametric_metadata)
        metadata["selected_parametric_method"] = selected_method
        if selection_reason is not None:
            metadata["selection_reason"] = selection_reason
        metadata["dominant_wavelength_initial_used"] = bool(
            config.get("dominant_wavelength_initial_used", False)
        )
        if config.get("dominant_wavelength_nm") is not None:
            metadata["dominant_wavelength_nm"] = float(config["dominant_wavelength_nm"])
    return build_recovered_spectral_object(
        wavelengths,
        values,
        is_single=is_single,
        labels=labels,
        name="Recovered spectrum",
        metadata=metadata,
    )


def recover_spectrum_from_responses(
    target: Sequence[float] | np.ndarray,
    responses: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    method: str | SpectrumRecoveryOption = "bounded_least_squares",
    labels: Sequence[str] | None = None,
    **method_options,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from arbitrary three-channel responses."""
    method_name, config = _normalise_spectrum_method(method, method_options)
    return _recover_spectrum_from_responses_resolved(
        target,
        responses,
        shape=shape,
        method_name=method_name,
        config=config,
        labels=labels,
    )


def recover_spectrum_from_XYZ(
    XYZ: Sequence[float] | np.ndarray,
    *,
    cmfs: ResponseSource = DEFAULT_CMFS,
    shape: SpectralShape | None = None,
    method: str | SpectrumRecoveryOption = "bounded_least_squares",
    labels: Sequence[str] | None = None,
    **method_options,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from XYZ tristimulus values."""
    resolved_method, config = _normalise_spectrum_method(method, method_options)
    if (
        resolved_method in {"gaussian", "multi_gaussian", "auto_gaussian"}
        and config.get("use_dominant_wavelength_initial", True)
        and config.get("center_initials") is None
    ):
        targets, _is_single = as_recovery_targets(XYZ, name="XYZ")
        whitepoint_xy = config.get("whitepoint_xy", (0.3127, 0.3290))
        xy = XYZ_to_xy(targets, fallback_xy=whitepoint_xy)
        analysis = analyze_chromaticity(xy, xy_n=whitepoint_xy)
        wavelengths = np.asarray(analysis.wavelength, dtype=np.float64).reshape(-1)
        regions = np.asarray(analysis.dominant_region).reshape(-1)
        purities = np.asarray(analysis.excitation_purity, dtype=np.float64).reshape(-1)
        regions = regions.copy()
        regions[purities < 0.1] = "undefined"
        spectral_wavelengths = wavelengths[
            np.isfinite(wavelengths) & (regions == "spectral")
        ]
        if spectral_wavelengths.size:
            initials = np.concatenate(
                [
                    spectral_wavelengths - 40.0,
                    spectral_wavelengths - 20.0,
                    spectral_wavelengths,
                    spectral_wavelengths + 20.0,
                    spectral_wavelengths + 40.0,
                ]
            )
            config["center_initials"] = initials
            config["dominant_wavelength_initial_used"] = True
        unique_regions = set(str(item) for item in regions)
        config["dominant_region"] = (
            unique_regions.pop() if len(unique_regions) == 1 else "mixed"
        )
        if wavelengths.size == 1 and np.isfinite(wavelengths[0]):
            config["dominant_wavelength_nm"] = float(abs(wavelengths[0]))

    return _recover_spectrum_from_responses_resolved(
        XYZ,
        _load_xyz_cmfs(cmfs),
        shape=shape,
        method_name=resolved_method,
        config=config,
        labels=labels,
    )


def recover_spectrum_from_xyY(
    xyY: Sequence[float] | np.ndarray,
    **kwargs,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from xyY tristimulus coordinates."""
    xyy, _ = as_recovery_targets(xyY, name="xyY")
    XYZ = xyY_to_XYZ(xyy)
    if np.asarray(xyY, dtype=np.float64).ndim == 1:
        XYZ = XYZ[0]
    return recover_spectrum_from_XYZ(XYZ, **kwargs)


def recover_spectrum_from_LMS(
    LMS: Sequence[float] | np.ndarray,
    *,
    fundamentals: ResponseSource = DEFAULT_FUNDAMENTALS,
    fill_nan: float | None = 0.0,
    shape: SpectralShape | None = None,
    method: str | SpectrumRecoveryOption = "bounded_least_squares",
    labels: Sequence[str] | None = None,
    **method_options,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from LMS cone responses."""
    return recover_spectrum_from_responses(
        LMS,
        _load_lms_fundamentals(fundamentals, fill_nan=fill_nan),
        shape=shape,
        method=method,
        labels=labels,
        **method_options,
    )


__all__ = [
    "as_recovery_targets",
    "validate_labels",
    "spectral_recovery_metadata",
    "build_recovered_spectral_object",
    "recover_spectrum_from_responses",
    "recover_spectrum_from_XYZ",
    "recover_spectrum_from_xyY",
    "recover_spectrum_from_LMS",
]
