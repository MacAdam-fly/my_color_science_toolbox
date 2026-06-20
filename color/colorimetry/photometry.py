"""Photometric functions and quantities from spectral data."""

from __future__ import annotations

from typing import Union

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)

from .integration import integrate_response_products


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


def _integrate_product(
    spectrum: SpectralInput,
    lef: SpectralDistribution,
    *,
    shape: SpectralShape | None = None,
) -> np.ndarray:
    """Integrate ``spectrum * lef`` for one or more spectral sources."""
    return np.atleast_1d(
        integrate_response_products(
            spectrum,
            lef,
            shape=shape,
        )
    )


def _integrate_spectrum(
    spectrum: SpectralInput,
    *,
    reference: SpectralDistribution,
    shape: SpectralShape | None = None,
) -> np.ndarray:
    """Integrate spectral power over wavelength."""
    unit_response = SpectralDistribution(
        reference.wavelengths,
        np.ones_like(reference.wavelengths, dtype=np.float64),
    )
    return np.atleast_1d(
        integrate_response_products(
            spectrum,
            unit_response,
            shape=shape,
        )
    )


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

    Parameters
    ----------
    name
        Dataset name in ``standard_observers.luminous_efficiency``.

    Returns
    -------
    SpectralDistribution
        Photopic luminous efficiency function.

    Notes
    -----
    The default is CIE 1924 ``V(lambda)``. Use
    ``photopic_luminous_*`` wrappers when you also want the matched
    ``K_m=683 lm/W`` default.
    """
    return _load_lef(name)


def scotopic_luminous_efficiency_function(
    name: str = DEFAULT_SCOTOPIC_LEF,
) -> SpectralDistribution:
    """Return a scotopic luminous efficiency function.

    Parameters
    ----------
    name
        Dataset name in ``standard_observers.luminous_efficiency``.

    Returns
    -------
    SpectralDistribution
        Scotopic luminous efficiency function.

    Notes
    -----
    Use ``scotopic_luminous_*`` wrappers when you also want the matched
    ``K_m=1700 lm/W`` default.
    """
    return _load_lef(name)


def luminous_flux(
    spectrum: SpectralInput,
    lef: LuminousEfficiencySource | None = None,
    *,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return luminous flux using the given luminous efficiency function.

    Parameters
    ----------
    spectrum
        Spectral distribution or multi-spectral distribution.
    lef
        Luminous efficiency function as a dataset name or
        ``SpectralDistribution``. If omitted, photopic ``V(lambda)`` is used.
    K_m
        Maximum luminous efficacy constant in lm/W.

    Returns
    -------
    float or ndarray
        Luminous flux-like integrated quantity. Multi-channel spectra return
        one value per channel.

    Notes
    -----
    This is the generic entry for custom LEFs. Prefer
    ``photopic_luminous_flux`` or ``scotopic_luminous_flux`` for standard
    matched defaults.

    Examples
    --------
    >>> from color.generators import gaussian_spd
    >>> from color.spectra import from_columns
    >>> sd = from_columns(gaussian_spd(), y="spd")
    >>> luminous_flux(sd) > 0
    True
    """
    lef_sd = photopic_luminous_efficiency_function() if lef is None else _load_lef(lef)
    flux = float(K_m) * _integrate_product(
        spectrum,
        lef_sd,
        shape=shape,
    )
    return _as_scalar_or_array(flux, spectrum)


def luminous_efficiency(
    spectrum: SpectralInput,
    lef: LuminousEfficiencySource | None = None,
    *,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return luminous efficiency using the given luminous efficiency function.

    Notes
    -----
    The value is the integral of ``spectrum * LEF`` divided by the integral of
    ``spectrum``. A zero spectral integral raises ``ZeroDivisionError``.
    """
    lef_sd = photopic_luminous_efficiency_function() if lef is None else _load_lef(lef)
    numerator = _integrate_product(
        spectrum,
        lef_sd,
        shape=shape,
    )
    denominator = _integrate_spectrum(
        spectrum,
        reference=lef_sd,
        shape=shape,
    )
    if np.any(np.isclose(denominator, 0.0)):
        raise ZeroDivisionError("spectral integral is zero")
    efficiency = numerator / denominator
    return _as_scalar_or_array(efficiency, spectrum)


def luminous_efficacy(
    spectrum: SpectralInput,
    lef: LuminousEfficiencySource | None = None,
    *,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return luminous efficacy in lm/W using the given LEF.

    Notes
    -----
    This is ``K_m * luminous_efficiency(...)``. Use the photopic/scotopic
    wrappers for matched standard constants.
    """
    efficacy = float(K_m) * np.asarray(
        luminous_efficiency(
            spectrum,
            lef,
            shape=shape,
        )
    )
    return _as_scalar_or_array(np.atleast_1d(efficacy), spectrum)


def photopic_luminous_flux(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_PHOTOPIC_LEF,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return photopic luminous flux with matched default LEF and ``K_m``.

    Notes
    -----
    The defaults pair CIE 1924 ``V(lambda)`` with ``K_m=683 lm/W``.
    """
    return luminous_flux(
        spectrum,
        lef,
        K_m=K_m,
        shape=shape,
    )


def scotopic_luminous_flux(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_SCOTOPIC_LEF,
    K_m: float = DEFAULT_SCOTOPIC_K_M,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return scotopic luminous flux with matched default LEF and ``K_m``.

    Notes
    -----
    The defaults pair the scotopic luminous efficiency function with
    ``K_m=1700 lm/W``.
    """
    return luminous_flux(
        spectrum,
        lef,
        K_m=K_m,
        shape=shape,
    )


def photopic_luminous_efficiency(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_PHOTOPIC_LEF,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return photopic luminous efficiency with a matched default LEF."""
    return luminous_efficiency(
        spectrum,
        lef,
        shape=shape,
    )


def scotopic_luminous_efficiency(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_SCOTOPIC_LEF,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return scotopic luminous efficiency with a matched default LEF."""
    return luminous_efficiency(
        spectrum,
        lef,
        shape=shape,
    )


def photopic_luminous_efficacy(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_PHOTOPIC_LEF,
    K_m: float = DEFAULT_PHOTOPIC_K_M,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return photopic luminous efficacy with matched default LEF and ``K_m``."""
    return luminous_efficacy(
        spectrum,
        lef,
        K_m=K_m,
        shape=shape,
    )


def scotopic_luminous_efficacy(
    spectrum: SpectralInput,
    *,
    lef: LuminousEfficiencySource = DEFAULT_SCOTOPIC_LEF,
    K_m: float = DEFAULT_SCOTOPIC_K_M,
    shape: SpectralShape | None = None,
) -> float | np.ndarray:
    """Return scotopic luminous efficacy with matched default LEF and ``K_m``."""
    return luminous_efficacy(
        spectrum,
        lef,
        K_m=K_m,
        shape=shape,
    )


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
