"""Gaussian curve helpers."""

from __future__ import annotations

import numpy as np


def gaussian_values(
    x: np.ndarray,
    *,
    amplitude: float = 1.0,
    center: float = 0.0,
    sigma: float = 1.0,
) -> np.ndarray:
    """Return Gaussian values evaluated at ``x``.

    This is a pure numerical helper. It does not attach wavelength, spectrum,
    metadata, or generator semantics to the returned values.
    """
    x_arr = np.asarray(x, dtype=np.float64)
    amplitude_value = float(amplitude)
    center_value = float(center)
    sigma_value = float(sigma)

    if not np.all(np.isfinite(x_arr)):
        raise ValueError("x must contain finite values")
    if not np.isfinite(amplitude_value):
        raise ValueError("amplitude must be finite")
    if not np.isfinite(center_value):
        raise ValueError("center must be finite")
    if sigma_value <= 0 or not np.isfinite(sigma_value):
        raise ValueError("sigma must be a finite positive value")

    return amplitude_value * np.exp(-0.5 * ((x_arr - center_value) / sigma_value) ** 2)


def sigma_from_fwhm(fwhm: float) -> float:
    """Return the Gaussian standard deviation corresponding to ``fwhm``."""
    fwhm_value = float(fwhm)
    if fwhm_value <= 0 or not np.isfinite(fwhm_value):
        raise ValueError("fwhm must be a finite positive value")
    return float(fwhm_value / (2.0 * np.sqrt(2.0 * np.log(2.0))))


def gaussian_values_from_fwhm(
    x: np.ndarray,
    *,
    amplitude: float = 1.0,
    center: float = 0.0,
    fwhm: float = 1.0,
) -> np.ndarray:
    """Return Gaussian values using full width at half maximum."""
    return gaussian_values(
        x,
        amplitude=amplitude,
        center=center,
        sigma=sigma_from_fwhm(fwhm),
    )


__all__ = [
    "gaussian_values",
    "gaussian_values_from_fwhm",
    "sigma_from_fwhm",
]
