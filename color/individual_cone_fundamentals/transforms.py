"""Optical transforms for Stockman/Rider cone fundamentals."""

from __future__ import annotations

import numpy as np


def normalise_to_peak(values: np.ndarray) -> np.ndarray:
    """Normalise each channel to unit peak."""
    result = np.array(values, dtype=np.float64, copy=True)
    peaks = np.max(result, axis=0)
    if np.any(peaks <= 0) or not np.all(np.isfinite(peaks)):
        raise ValueError("spectra cannot be normalised to unit peak")
    return result / peaks


def retinal_absorptance(
    absorbance: np.ndarray,
    optical_densities: np.ndarray,
) -> np.ndarray:
    """Convert linear absorbance spectra to retinal absorptance."""
    result = np.empty_like(absorbance)
    for index, density in enumerate(optical_densities):
        if density == 0:
            result[:, index] = absorbance[:, index]
        else:
            result[:, index] = (
                (1.0 - 10.0 ** (-density * absorbance[:, index]))
                / (1.0 - 10.0 ** (-density))
            )
    return normalise_to_peak(result)


def apply_prereceptoral_filtering(
    retinal: np.ndarray,
    prereceptoral_density: np.ndarray,
) -> np.ndarray:
    """Apply macular and lens density attenuation to retinal absorptance."""
    corneal_quantal = retinal / (10.0**prereceptoral_density)[:, None]
    return normalise_to_peak(corneal_quantal)


def quantal_to_energy(corneal_quantal: np.ndarray, wavelength_nm: np.ndarray) -> np.ndarray:
    """Convert corneal quantal spectra to corneal energy spectra."""
    return normalise_to_peak(corneal_quantal * wavelength_nm[:, None])


__all__ = [
    "normalise_to_peak",
    "retinal_absorptance",
    "apply_prereceptoral_filtering",
    "quantal_to_energy",
]
