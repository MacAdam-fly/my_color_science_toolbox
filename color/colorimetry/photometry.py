"""Photometric functions and quantities from spectral data."""

from __future__ import annotations

from typing import Union

import numpy as np

from color.spectra import MultiSpectralDistribution, SpectralDistribution, from_dataset


SpectralInput = Union[SpectralDistribution, MultiSpectralDistribution]
LuminousEfficiencySource = Union[str, SpectralDistribution]

DEFAULT_PHOTOPIC_LEF = "vl1924_1nm"
DEFAULT_SCOTOPIC_LEF = "scotopic_v_1nm"
DEFAULT_PHOTOPIC_K_M = 683.0
DEFAULT_SCOTOPIC_K_M = 1700.0


def _load_lef(lef: LuminousEfficiencySource) -> SpectralDistribution:
    """Return a luminous efficiency function from an object or dataset name."""
    if isinstance(lef, SpectralDistribution):
        return lef
    return from_dataset("standard_observers.luminous_efficiency", lef)


def _sample_lef_on(
    wavelengths: np.ndarray,
    lef: SpectralDistribution,
) -> np.ndarray:
    """Sample a LEF on arbitrary wavelengths with zero response out of range."""
    return lef.sample(
        wavelengths,
        bounds_error=False,
        fill_value=0.0,
    )


def _source_values(spectrum: SpectralInput) -> np.ndarray:
    """Return source values as ``(n_sources, n_wavelengths)``."""
    if isinstance(spectrum, SpectralDistribution):
        return spectrum.values.reshape(1, -1)
    return spectrum.values.T


def _integrate_product(
    spectrum: SpectralInput,
    lef: SpectralDistribution,
) -> np.ndarray:
    """Integrate ``spectrum * lef`` for one or more spectral sources."""
    weights = _sample_lef_on(spectrum.wavelengths, lef)
    source_values = _source_values(spectrum)
    return np.trapz(source_values * weights.reshape(1, -1), spectrum.wavelengths, axis=1)


def _integrate_spectrum(spectrum: SpectralInput) -> np.ndarray:
    """Integrate spectral power over wavelength."""
    return np.trapz(_source_values(spectrum), spectrum.wavelengths, axis=1)


def _as_scalar_or_array(
    values: np.ndarray,
    spectrum: SpectralInput,
) -> float | np.ndarray:
    """Return a scalar for single-channel input, otherwise a 1D array."""
    if isinstance(spectrum, SpectralDistribution):
        return float(values[0])
    return values


def photopic_luminous_efficiency_function(
    name: str = DEFAULT_PHOTOPIC_LEF,
) -> SpectralDistribution:
    """Return a photopic luminous efficiency function.

    By default, this returns ``standard_observers.luminous_efficiency/vl1924_1nm``.
    """
    return _load_lef(name)


def scotopic_luminous_efficiency_function(
    name: str = DEFAULT_SCOTOPIC_LEF,
) -> SpectralDistribution:
    """Return a scotopic luminous efficiency function.

    By default, this returns
    ``standard_observers.luminous_efficiency/scotopic_v_1nm``.
    """
    return _load_lef(name)


def luminous_flux(
    spectrum: SpectralInput,
    lef: LuminousEfficiencySource | None = None,
    *,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
) -> float | np.ndarray:
    """Return luminous flux using the given luminous efficiency function.

    If ``lef`` is omitted, the CIE 1924 photopic ``V(lambda)`` function is used.
    """
    lef_sd = photopic_luminous_efficiency_function() if lef is None else _load_lef(lef)
    flux = float(K_m) * _integrate_product(spectrum, lef_sd)
    return _as_scalar_or_array(flux, spectrum)


def luminous_efficiency(
    spectrum: SpectralInput,
    lef: LuminousEfficiencySource | None = None,
) -> float | np.ndarray:
    """Return luminous efficiency using the given luminous efficiency function.

    If ``lef`` is omitted, the CIE 1924 photopic ``V(lambda)`` function is used.
    """
    lef_sd = photopic_luminous_efficiency_function() if lef is None else _load_lef(lef)
    numerator = _integrate_product(spectrum, lef_sd)
    denominator = _integrate_spectrum(spectrum)
    if np.any(np.isclose(denominator, 0.0)):
        raise ZeroDivisionError("spectral integral is zero")
    efficiency = numerator / denominator
    return _as_scalar_or_array(efficiency, spectrum)


def luminous_efficacy(
    spectrum: SpectralInput,
    lef: LuminousEfficiencySource | None = None,
    *,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
) -> float | np.ndarray:
    """Return luminous efficacy in lm/W using the given LEF."""
    efficacy = float(K_m) * np.asarray(luminous_efficiency(spectrum, lef))
    return _as_scalar_or_array(np.atleast_1d(efficacy), spectrum)


def photopic_luminous_flux(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_PHOTOPIC_LEF,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
) -> float | np.ndarray:
    """Return photopic luminous flux with matched default LEF and ``K_m``."""
    return luminous_flux(spectrum, lef, K_m=K_m)


def scotopic_luminous_flux(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_SCOTOPIC_LEF,
    K_m: float = DEFAULT_SCOTOPIC_K_M,
) -> float | np.ndarray:
    """Return scotopic luminous flux with matched default LEF and ``K_m``."""
    return luminous_flux(spectrum, lef, K_m=K_m)


def photopic_luminous_efficiency(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_PHOTOPIC_LEF,
) -> float | np.ndarray:
    """Return photopic luminous efficiency with a matched default LEF."""
    return luminous_efficiency(spectrum, lef)


def scotopic_luminous_efficiency(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_SCOTOPIC_LEF,
) -> float | np.ndarray:
    """Return scotopic luminous efficiency with a matched default LEF."""
    return luminous_efficiency(spectrum, lef)


def photopic_luminous_efficacy(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_PHOTOPIC_LEF,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
) -> float | np.ndarray:
    """Return photopic luminous efficacy with matched default LEF and ``K_m``."""
    return luminous_efficacy(spectrum, lef, K_m=K_m)


def scotopic_luminous_efficacy(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_SCOTOPIC_LEF,
    K_m: float = DEFAULT_SCOTOPIC_K_M,
) -> float | np.ndarray:
    """Return scotopic luminous efficacy with matched default LEF and ``K_m``."""
    return luminous_efficacy(spectrum, lef, K_m=K_m)


__all__ = [
    "DEFAULT_PHOTOPIC_LEF",
    "DEFAULT_SCOTOPIC_LEF",
    "DEFAULT_PHOTOPIC_K_M",
    "DEFAULT_SCOTOPIC_K_M",
    "photopic_luminous_efficiency_function",
    "scotopic_luminous_efficiency_function",
    "luminous_flux",
    "luminous_efficiency",
    "luminous_efficacy",
    "photopic_luminous_flux",
    "scotopic_luminous_flux",
    "photopic_luminous_efficiency",
    "scotopic_luminous_efficiency",
    "photopic_luminous_efficacy",
    "scotopic_luminous_efficacy",
]
