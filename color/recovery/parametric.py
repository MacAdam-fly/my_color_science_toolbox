"""Parametric Gaussian spectrum recovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import minimize

from color.math import gaussian_values

from .solvers import validate_bounds


_FALLBACK_CENTERS = np.array([420.0, 460.0, 500.0, 540.0, 580.0, 620.0, 660.0])
_SIGMA_INITIALS = np.array([10.0, 25.0, 50.0, 90.0])
_EPSILON = 1e-12


@dataclass(frozen=True)
class ParametricRecoveryResult:
    """Recovered spectra and method metadata."""

    values: np.ndarray
    metadata: dict


def gaussian_spectrum(
    wavelengths: Sequence[float] | np.ndarray,
    amplitude: float,
    center: float,
    sigma: float,
) -> np.ndarray:
    """Return a single Gaussian spectrum."""
    return gaussian_values(
        np.asarray(wavelengths, dtype=np.float64),
        amplitude=amplitude,
        center=center,
        sigma=sigma,
    )


def multi_gaussian_spectrum(
    wavelengths: Sequence[float] | np.ndarray,
    amplitudes: Sequence[float] | np.ndarray,
    centers: Sequence[float] | np.ndarray,
    sigmas: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Return a sum of Gaussian spectra."""
    wl = np.asarray(wavelengths, dtype=np.float64)
    amps = np.asarray(amplitudes, dtype=np.float64)
    ctrs = np.asarray(centers, dtype=np.float64)
    sgm = np.asarray(sigmas, dtype=np.float64)
    if amps.ndim != 1 or ctrs.ndim != 1 or sgm.ndim != 1:
        raise ValueError("amplitudes, centers and sigmas must be one-dimensional")
    if not (amps.size == ctrs.size == sgm.size):
        raise ValueError("amplitudes, centers and sigmas must have matching lengths")
    if np.any(sgm <= 0) or not np.all(np.isfinite(sgm)):
        raise ValueError("sigmas must be finite positive values")
    components = np.array(
        [
            gaussian_values(wl, amplitude=amplitude, center=center, sigma=sigma)
            for amplitude, center, sigma in zip(amps, ctrs, sgm)
        ],
        dtype=np.float64,
    )
    return np.sum(components, axis=0)


def _validate_center_bounds(
    center_bounds: Sequence[float] | None,
    wavelengths: np.ndarray,
) -> tuple[float, float]:
    if center_bounds is None:
        return float(wavelengths[0]), float(wavelengths[-1])
    lower, upper = (float(center_bounds[0]), float(center_bounds[1]))
    if not np.isfinite(lower) or not np.isfinite(upper) or upper <= lower:
        raise ValueError("center_bounds must contain two finite increasing values")
    return lower, upper


def _validate_sigma_bounds(bounds: Sequence[float]) -> tuple[float, float]:
    lower, upper = validate_bounds(bounds)
    if lower <= 0:
        raise ValueError("sigma lower bound must be positive")
    if not np.isfinite(upper):
        raise ValueError("sigma upper bound must be finite")
    return lower, upper


def _validate_error(error: str) -> str:
    if error not in {"absolute", "relative"}:
        raise ValueError("error must be 'absolute' or 'relative'")
    return error


def _as_center_initials(
    center_initials: Sequence[float] | np.ndarray | None,
    center_bounds: tuple[float, float],
) -> np.ndarray:
    centers = _FALLBACK_CENTERS if center_initials is None else np.concatenate(
        [
            np.asarray(center_initials, dtype=np.float64).reshape(-1),
            _FALLBACK_CENTERS,
        ]
    )
    centers = centers[np.isfinite(centers)]
    centers = centers[(centers >= center_bounds[0]) & (centers <= center_bounds[1])]
    if centers.size == 0:
        centers = np.array([0.5 * (center_bounds[0] + center_bounds[1])])
    return np.unique(np.round(centers.astype(np.float64), decimals=8))


def _sigma_initials(sigma_bounds: tuple[float, float]) -> np.ndarray:
    sigmas = _SIGMA_INITIALS[
        (_SIGMA_INITIALS >= sigma_bounds[0]) & (_SIGMA_INITIALS <= sigma_bounds[1])
    ]
    if sigmas.size == 0:
        sigmas = np.array([0.5 * (sigma_bounds[0] + sigma_bounds[1])])
    return sigmas


def _target_scale(target: np.ndarray, error: str) -> np.ndarray:
    if error == "absolute":
        return np.ones_like(target, dtype=np.float64)
    return np.maximum(np.abs(target), _EPSILON)


def _fit_amplitudes(
    target: np.ndarray,
    matrix: np.ndarray,
    basis: np.ndarray,
    *,
    scale: np.ndarray,
    amplitude_bounds: tuple[float, float],
) -> np.ndarray:
    response_basis = matrix @ basis.T
    lhs = response_basis / scale[:, None]
    rhs = target / scale
    coeffs, *_ = np.linalg.lstsq(lhs, rhs, rcond=None)
    lower, upper = amplitude_bounds
    return np.clip(coeffs, lower, upper)


def _single_objective(
    params: np.ndarray,
    *,
    target: np.ndarray,
    matrix: np.ndarray,
    wavelengths: np.ndarray,
    error: str,
) -> float:
    spectrum = gaussian_spectrum(wavelengths, params[0], params[1], params[2])
    residual = (matrix @ spectrum - target) / _target_scale(target, error)
    return float(np.sum(residual * residual))


def _multi_objective(
    params: np.ndarray,
    *,
    target: np.ndarray,
    matrix: np.ndarray,
    wavelengths: np.ndarray,
    n_components: int,
    error: str,
) -> float:
    amplitudes = params[:n_components]
    centers = params[n_components : 2 * n_components]
    sigmas = params[2 * n_components :]
    spectrum = multi_gaussian_spectrum(wavelengths, amplitudes, centers, sigmas)
    residual = (matrix @ spectrum - target) / _target_scale(target, error)
    return float(np.sum(residual * residual))


def _optimise_single(
    target: np.ndarray,
    matrix: np.ndarray,
    wavelengths: np.ndarray,
    *,
    amplitude_bounds: tuple[float, float],
    center_bounds: tuple[float, float],
    sigma_bounds: tuple[float, float],
    center_initials: np.ndarray,
    error: str,
) -> tuple[np.ndarray, np.ndarray, float]:
    best_result = None
    for center in center_initials:
        for sigma in _sigma_initials(sigma_bounds):
            unit = gaussian_spectrum(wavelengths, 1.0, center, sigma)
            amplitude = _fit_amplitudes(
                target,
                matrix,
                unit.reshape(1, -1),
                scale=_target_scale(target, error),
                amplitude_bounds=amplitude_bounds,
            )[0]
            result = minimize(
                lambda params, target=target: _single_objective(
                    params,
                    target=target,
                    matrix=matrix,
                    wavelengths=wavelengths,
                    error=error,
                ),
                np.array([amplitude, center, sigma], dtype=np.float64),
                method="L-BFGS-B",
                bounds=(amplitude_bounds, center_bounds, sigma_bounds),
            )
            if result.success and (best_result is None or result.fun < best_result.fun):
                best_result = result
    if best_result is None:
        raise RuntimeError("Gaussian spectrum optimisation failed")
    params = np.asarray(best_result.x, dtype=np.float64)
    return gaussian_spectrum(wavelengths, params[0], params[1], params[2]), params, float(best_result.fun)


def _multi_initial_center_sets(
    *,
    n_components: int,
    center_initials: np.ndarray,
    center_bounds: tuple[float, float],
    dominant_region: str | None,
) -> list[np.ndarray]:
    if n_components not in {2, 3}:
        raise ValueError("n_components must be 2 or 3")

    candidates: list[np.ndarray] = []
    if dominant_region == "purple":
        candidates.extend(
            [
                np.array([430.0, 640.0]),
                np.array([450.0, 620.0]),
                np.array([420.0, 660.0]),
            ]
        )
    elif center_initials.size:
        center = float(center_initials[0])
        candidates.append(np.array([center - 40.0, center + 40.0]))
        candidates.append(np.array([center, 0.5 * (center + 660.0)]))

    candidates.extend(
        [
            np.array([450.0, 620.0]),
            np.array([430.0, 560.0]),
            np.array([500.0, 650.0]),
        ]
    )
    if n_components == 3:
        candidates = [
            np.concatenate([candidate, [550.0]]) if candidate.size == 2 else candidate
            for candidate in candidates
        ]
        candidates.append(np.array([450.0, 550.0, 650.0]))

    valid = []
    for candidate in candidates:
        clipped = np.clip(candidate, center_bounds[0], center_bounds[1])
        if np.unique(np.round(clipped, 6)).size == n_components:
            valid.append(np.sort(clipped))
    if not valid:
        valid.append(np.linspace(center_bounds[0], center_bounds[1], n_components + 2)[1:-1])
    return valid


def _optimise_multi(
    target: np.ndarray,
    matrix: np.ndarray,
    wavelengths: np.ndarray,
    *,
    amplitude_bounds: tuple[float, float],
    center_bounds: tuple[float, float],
    sigma_bounds: tuple[float, float],
    center_initials: np.ndarray,
    n_components: int,
    error: str,
    dominant_region: str | None,
) -> tuple[np.ndarray, np.ndarray, float]:
    best_result = None
    sigma0 = float(np.clip(35.0, sigma_bounds[0], sigma_bounds[1]))
    for centers in _multi_initial_center_sets(
        n_components=n_components,
        center_initials=center_initials,
        center_bounds=center_bounds,
        dominant_region=dominant_region,
    ):
        basis = np.array(
            [gaussian_spectrum(wavelengths, 1.0, center, sigma0) for center in centers],
            dtype=np.float64,
        )
        amplitudes = _fit_amplitudes(
            target,
            matrix,
            basis,
            scale=_target_scale(target, error),
            amplitude_bounds=amplitude_bounds,
        )
        initial = np.concatenate(
            [
                amplitudes,
                centers,
                np.full(n_components, sigma0, dtype=np.float64),
            ]
        )
        bounds = (
            [amplitude_bounds] * n_components
            + [center_bounds] * n_components
            + [sigma_bounds] * n_components
        )
        result = minimize(
            lambda params, target=target: _multi_objective(
                params,
                target=target,
                matrix=matrix,
                wavelengths=wavelengths,
                n_components=n_components,
                error=error,
            ),
            initial,
            method="L-BFGS-B",
            bounds=bounds,
        )
        if result.success and (best_result is None or result.fun < best_result.fun):
            best_result = result
    if best_result is None:
        raise RuntimeError("Multi-Gaussian spectrum optimisation failed")

    params = np.asarray(best_result.x, dtype=np.float64)
    amplitudes = params[:n_components]
    centers = params[n_components : 2 * n_components]
    sigmas = params[2 * n_components :]
    order = np.argsort(centers)
    ordered = np.concatenate([amplitudes[order], centers[order], sigmas[order]])
    spectrum = multi_gaussian_spectrum(
        wavelengths,
        amplitudes[order],
        centers[order],
        sigmas[order],
    )
    return spectrum, ordered, float(best_result.fun)


def _base_parametric_metadata(
    *,
    method: str,
    error: str,
    center_initials: np.ndarray,
    dominant_region: str | None,
) -> dict:
    return {
        "parametric_method": method,
        "gaussian_error": error,
        "center_initials": tuple(float(item) for item in center_initials),
        "dominant_region": dominant_region,
    }


def solve_gaussian_spectrum(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    wavelengths: Sequence[float] | np.ndarray,
    amplitude_bounds: Sequence[float] = (0.0, np.inf),
    center_bounds: Sequence[float] | None = None,
    sigma_bounds: Sequence[float] = (2.0, 120.0),
    center_initials: Sequence[float] | np.ndarray | None = None,
    error: str = "relative",
    dominant_region: str | None = None,
    **_kwargs,
) -> ParametricRecoveryResult:
    """Recover spectra using a single Gaussian model."""
    wl = np.asarray(wavelengths, dtype=np.float64)
    amp_bounds = validate_bounds(amplitude_bounds)
    ctr_bounds = _validate_center_bounds(center_bounds, wl)
    sig_bounds = _validate_sigma_bounds(sigma_bounds)
    error_name = _validate_error(error)
    centers = _as_center_initials(center_initials, ctr_bounds)

    values = []
    params = []
    errors = []
    for target in np.asarray(targets, dtype=np.float64):
        spectrum, param, final_error = _optimise_single(
            target,
            matrix,
            wl,
            amplitude_bounds=amp_bounds,
            center_bounds=ctr_bounds,
            sigma_bounds=sig_bounds,
            center_initials=centers,
            error=error_name,
        )
        values.append(spectrum)
        params.append(param)
        errors.append(final_error)

    metadata = _base_parametric_metadata(
        method="gaussian",
        error=error_name,
        center_initials=centers,
        dominant_region=dominant_region,
    )
    metadata["gaussian_parameters"] = tuple(
        {
            "amplitude": float(param[0]),
            "center": float(param[1]),
            "sigma": float(param[2]),
        }
        for param in params
    )
    metadata["final_error"] = tuple(float(item) for item in errors)
    return ParametricRecoveryResult(np.asarray(values, dtype=np.float64), metadata)


def solve_multi_gaussian_spectrum(
    targets: np.ndarray,
    matrix: np.ndarray,
    *,
    wavelengths: Sequence[float] | np.ndarray,
    amplitude_bounds: Sequence[float] = (0.0, np.inf),
    center_bounds: Sequence[float] | None = None,
    sigma_bounds: Sequence[float] = (2.0, 120.0),
    center_initials: Sequence[float] | np.ndarray | None = None,
    error: str = "relative",
    n_components: int = 2,
    dominant_region: str | None = None,
    **_kwargs,
) -> ParametricRecoveryResult:
    """Recover spectra using a multi-Gaussian model."""
    wl = np.asarray(wavelengths, dtype=np.float64)
    amp_bounds = validate_bounds(amplitude_bounds)
    ctr_bounds = _validate_center_bounds(center_bounds, wl)
    sig_bounds = _validate_sigma_bounds(sigma_bounds)
    error_name = _validate_error(error)
    components = int(n_components)
    centers = _as_center_initials(center_initials, ctr_bounds)

    values = []
    params = []
    errors = []
    for target in np.asarray(targets, dtype=np.float64):
        spectrum, param, final_error = _optimise_multi(
            target,
            matrix,
            wl,
            amplitude_bounds=amp_bounds,
            center_bounds=ctr_bounds,
            sigma_bounds=sig_bounds,
            center_initials=centers,
            n_components=components,
            error=error_name,
            dominant_region=dominant_region,
        )
        values.append(spectrum)
        params.append(param)
        errors.append(final_error)

    metadata = _base_parametric_metadata(
        method="multi_gaussian",
        error=error_name,
        center_initials=centers,
        dominant_region=dominant_region,
    )
    metadata["n_components"] = components
    metadata["gaussian_parameters"] = tuple(
        {
            "amplitudes": tuple(float(item) for item in param[:components]),
            "centers": tuple(float(item) for item in param[components : 2 * components]),
            "sigmas": tuple(float(item) for item in param[2 * components :]),
        }
        for param in params
    )
    metadata["final_error"] = tuple(float(item) for item in errors)
    return ParametricRecoveryResult(np.asarray(values, dtype=np.float64), metadata)


__all__ = [
    "ParametricRecoveryResult",
    "gaussian_spectrum",
    "multi_gaussian_spectrum",
    "solve_gaussian_spectrum",
    "solve_multi_gaussian_spectrum",
]
