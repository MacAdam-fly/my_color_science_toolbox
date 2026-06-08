"""Effective spectrum recovery from three-channel responses."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

from color.colorimetry import DEFAULT_CMFS, XYZ_to_xy, analyze_chromaticity
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


def recover_spectrum_from_responses(
    target: Sequence[float] | np.ndarray,
    responses: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    method: str = "bounded_least_squares",
    bounds: tuple[float, float] = (0.0, np.inf),
    smoothness: float = 1e-3,
    amplitude_bounds: tuple[float, float] = (0.0, np.inf),
    center_bounds: tuple[float, float] | None = None,
    sigma_bounds: tuple[float, float] = (2.0, 120.0),
    center_initials: Sequence[float] | np.ndarray | None = None,
    error: str = "relative",
    n_components: int = 2,
    dominant_region: str | None = None,
    dominant_wavelength_nm: float | None = None,
    dominant_wavelength_initial_used: bool = False,
    labels: Sequence[str] | None = None,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from arbitrary three-channel responses."""
    targets, is_single = as_recovery_targets(target, name="target")
    matrix, wavelengths, common_shape = response_recovery_matrix(
        responses,
        shape=shape,
    )
    method_name, solver = resolve_spectrum_recovery_method(method)
    selected_method = method_name
    selection_reason = None
    if method_name == "auto_gaussian":
        if dominant_region == "spectral":
            selected_method = "gaussian"
            selection_reason = "spectral_dominant_wavelength"
        else:
            selected_method = "multi_gaussian"
            selection_reason = dominant_region or "no_chromaticity_analysis"
        _resolved, solver = resolve_spectrum_recovery_method(selected_method)

    if selected_method in {"gaussian", "multi_gaussian"}:
        result = solver(
            targets,
            matrix,
            wavelengths=wavelengths,
            amplitude_bounds=amplitude_bounds,
            center_bounds=center_bounds,
            sigma_bounds=sigma_bounds,
            center_initials=center_initials,
            error=error,
            n_components=n_components,
            dominant_region=dominant_region,
        )
        if not isinstance(result, ParametricRecoveryResult):
            raise TypeError("parametric recovery solver returned an invalid result")
        values = result.values
        parametric_metadata = result.metadata
    else:
        values = solver(
            targets,
            matrix,
            bounds=bounds,
            smoothness=smoothness,
        )
        parametric_metadata = {}
    metadata = spectral_recovery_metadata(
        method=method_name,
        bounds=bounds,
        smoothness=smoothness,
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
            dominant_wavelength_initial_used
        )
        if dominant_wavelength_nm is not None:
            metadata["dominant_wavelength_nm"] = float(dominant_wavelength_nm)
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
    use_dominant_wavelength_initial: bool = True,
    whitepoint_xy: Sequence[float] = (0.3127, 0.3290),
    **kwargs,
) -> Union[SpectralDistribution, MultiSpectralDistribution]:
    """Recover an effective spectrum from XYZ tristimulus values."""
    method_name = kwargs.get("method", "bounded_least_squares")
    resolved_method, _solver = resolve_spectrum_recovery_method(method_name)
    if (
        resolved_method in {"gaussian", "multi_gaussian", "auto_gaussian"}
        and use_dominant_wavelength_initial
        and kwargs.get("center_initials") is None
    ):
        targets, _is_single = as_recovery_targets(XYZ, name="XYZ")
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
            kwargs["center_initials"] = initials
            kwargs["dominant_wavelength_initial_used"] = True
        unique_regions = set(str(item) for item in regions)
        kwargs["dominant_region"] = (
            unique_regions.pop() if len(unique_regions) == 1 else "mixed"
        )
        if wavelengths.size == 1 and np.isfinite(wavelengths[0]):
            kwargs["dominant_wavelength_nm"] = float(abs(wavelengths[0]))

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
