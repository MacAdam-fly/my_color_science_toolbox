"""Spectral templates for Stockman/Rider individual cone fundamentals."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from color.utils.names import canonical_method_name

from ._constants import (
    DEFAULT_LENS_DENSITY_400,
    DEFAULT_MACULAR_DENSITY_460,
    DEFAULT_PHOTOPIGMENT_OD,
    DEFAULT_WAVELENGTHS_NM,
    GeneratedConeDict,
    LENS_COEFFICIENTS,
    LENS_TEMPLATE_400,
    L_TEMPLATE_ALIASES,
    L_SER_COEFFICIENTS,
    MACULAR_COEFFICIENTS,
    MACULAR_TEMPLATE_460,
    M_COEFFICIENTS,
    S_COEFFICIENTS,
)
from ._transforms import (
    apply_prereceptoral_filtering,
    normalise_to_peak,
    quantal_to_energy,
    retinal_absorptance,
)


def as_wavelengths(wavelength_nm: np.ndarray | None) -> np.ndarray:
    """Return wavelengths as a finite one-dimensional array in 360-850 nm."""
    if wavelength_nm is None:
        wavelengths = DEFAULT_WAVELENGTHS_NM
    else:
        wavelengths = np.asarray(wavelength_nm, dtype=np.float64)
    if wavelengths.ndim != 1 or wavelengths.size == 0:
        raise ValueError("wavelength_nm must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(wavelengths)):
        raise ValueError("wavelength_nm must be finite")
    if np.any(wavelengths < 360.0) or np.any(wavelengths > 850.0):
        raise ValueError("wavelength_nm must be within the 360-850 nm model range")
    if np.any(np.diff(wavelengths) <= 0):
        raise ValueError("wavelength_nm must be strictly increasing")
    return np.array(wavelengths, dtype=np.float64, copy=True)


def validate_shift(value: float, name: str) -> float:
    """Return *value* as a finite wavelength shift in nm."""
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _fourier_8(theta: np.ndarray, coefficients: tuple[float, ...]) -> np.ndarray:
    """Evaluate an 8th order Fourier polynomial."""
    result = np.full(theta.shape, coefficients[0], dtype=np.float64)
    index = 1
    for order in range(1, 9):
        result = (
            result
            + coefficients[index] * np.cos(order * theta)
            + coefficients[index + 1] * np.sin(order * theta)
        )
        index += 2
    return result + coefficients[17]


def _fourier_density(
    theta: np.ndarray,
    coefficients: tuple[float, ...],
    order: int,
    scale_index: int,
) -> np.ndarray:
    """Evaluate a finite Fourier density template."""
    result = np.full(theta.shape, coefficients[0], dtype=np.float64)
    index = 1
    for harmonic in range(1, order + 1):
        result = (
            result
            + coefficients[index] * np.cos(harmonic * theta)
            + coefficients[index + 1] * np.sin(harmonic * theta)
        )
        index += 2
    return result * coefficients[scale_index]


def _theta_photopigment(
    wavelength_nm: np.ndarray,
    *,
    lmax_nm: float,
    shift_nm: float,
) -> np.ndarray:
    """Return Stockman/Rider log-wavelength theta for a shifted pigment."""
    if lmax_nm + shift_nm <= 0:
        raise ValueError("shifted photopigment lmax must be positive")
    theta = (
        np.pi
        * (np.log10(wavelength_nm) - np.log10(360.0))
        / np.log10(850.0 / 360.0)
    )
    theta = theta + np.pi * np.log10(lmax_nm / (lmax_nm + shift_nm)) / np.log10(
        850.0 / 360.0
    )
    return theta


def _l_ser_log_absorbance(wavelength_nm: np.ndarray, shift_nm: float) -> np.ndarray:
    """Return L(ser180) log10 absorbance."""
    return _fourier_8(
        _theta_photopigment(wavelength_nm, lmax_nm=553.1, shift_nm=shift_nm),
        L_SER_COEFFICIENTS,
    )


def _l_ala_log_absorbance(wavelength_nm: np.ndarray, shift_nm: float) -> np.ndarray:
    """Return L(ala180) log10 absorbance."""
    return _l_ser_log_absorbance(wavelength_nm, shift_nm - 2.70)


def _l_mean_log_absorbance(wavelength_nm: np.ndarray, shift_nm: float) -> np.ndarray:
    """Return population-mean L log10 absorbance."""
    l_ser = 10.0 ** _l_ser_log_absorbance(wavelength_nm, shift_nm)
    l_ala = 10.0 ** _l_ala_log_absorbance(wavelength_nm, shift_nm)
    mean = 0.56 * l_ser + 0.44 * l_ala
    return np.log10(mean / np.max(mean))


def _m_log_absorbance(wavelength_nm: np.ndarray, shift_nm: float) -> np.ndarray:
    """Return M log10 absorbance."""
    return _fourier_8(
        _theta_photopigment(wavelength_nm, lmax_nm=529.9, shift_nm=shift_nm),
        M_COEFFICIENTS,
    )


def _s_log_absorbance(wavelength_nm: np.ndarray, shift_nm: float) -> np.ndarray:
    """Return S log10 absorbance."""
    return _fourier_8(
        _theta_photopigment(wavelength_nm, lmax_nm=416.9, shift_nm=shift_nm),
        S_COEFFICIENTS,
    )


def _resolve_l_template(l_template: str) -> str:
    """Resolve an L template label."""
    key = canonical_method_name(l_template)
    resolved = L_TEMPLATE_ALIASES.get(key)
    if resolved is None:
        raise ValueError("l_template must be one of: mean, ser180, ala180")
    return resolved


def macular_density_spectrum(
    wavelength_nm: np.ndarray | None = None,
) -> GeneratedConeDict:
    """Return the Stockman/Rider macular pigment optical-density template."""
    wavelengths = as_wavelengths(wavelength_nm)
    theta = np.pi * (wavelengths - 375.0) / (550.0 - 375.0)
    density = _fourier_density(theta, MACULAR_COEFFICIENTS, order=11, scale_index=23)
    density = np.where((wavelengths >= 375.0) & (wavelengths <= 550.0), density, 0.0)
    density = np.clip(density, 0.0, None)
    return {"wavelength": wavelengths, "optical_density": density}


def lens_density_spectrum(
    wavelength_nm: np.ndarray | None = None,
) -> GeneratedConeDict:
    """Return the Stockman/Rider lens pigment optical-density template."""
    wavelengths = as_wavelengths(wavelength_nm)
    theta = np.pi * (wavelengths - 360.0) / (660.0 - 360.0)
    density = _fourier_density(theta, LENS_COEFFICIENTS, order=9, scale_index=19)
    density = np.where(wavelengths <= 660.0, density, 0.0)
    density = np.clip(density, 0.0, None)
    return {"wavelength": wavelengths, "optical_density": density}


def cone_absorbance_spectra(
    wavelength_nm: np.ndarray | None = None,
    *,
    l_shift_nm: float = 0.0,
    m_shift_nm: float = 0.0,
    s_shift_nm: float = 0.0,
    l_template: str = "mean",
) -> GeneratedConeDict:
    """Return linear photopigment absorbance spectra for L, M and S cones."""
    wavelengths = as_wavelengths(wavelength_nm)
    l_shift = validate_shift(l_shift_nm, "l_shift_nm")
    m_shift = validate_shift(m_shift_nm, "m_shift_nm")
    s_shift = validate_shift(s_shift_nm, "s_shift_nm")
    template = _resolve_l_template(l_template)

    if template == "mean":
        l_log = _l_mean_log_absorbance(wavelengths, l_shift)
    elif template == "ser180":
        l_log = _l_ser_log_absorbance(wavelengths, l_shift)
    else:
        l_log = _l_ala_log_absorbance(wavelengths, l_shift)

    values = np.column_stack((
        10.0**l_log,
        10.0 ** _m_log_absorbance(wavelengths, m_shift),
        10.0 ** _s_log_absorbance(wavelengths, s_shift),
    ))
    values = normalise_to_peak(values)
    return {
        "wavelength": wavelengths,
        "l": values[:, 0],
        "m": values[:, 1],
        "s": values[:, 2],
    }


def _validate_non_negative(value: float, name: str) -> float:
    """Return *value* as a non-negative finite float."""
    value = float(value)
    if not np.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite non-negative value")
    return value


def _observer_degree(observer_degree: int) -> int:
    """Validate and return observer field size."""
    if observer_degree not in (2, 10):
        raise ValueError("observer_degree must be 2 or 10")
    return observer_degree


def _column_stack(raw: Mapping[str, np.ndarray]) -> np.ndarray:
    """Stack LMS columns from a raw mapping."""
    return np.column_stack((raw["l"], raw["m"], raw["s"]))


def stockman_rider_2023_model_components(
    wavelength_nm: np.ndarray | None = None,
    *,
    observer_degree: int = 2,
    photopigment_od: tuple[float, float, float] | None = None,
    macular_density_460: float | None = None,
    lens_density_400: float = DEFAULT_LENS_DENSITY_400,
    l_shift_nm: float = 0.0,
    m_shift_nm: float = 0.0,
    s_shift_nm: float = 0.0,
    l_template: str = "mean",
) -> GeneratedConeDict:
    """Return Stockman/Rider 2023 model components for one observer.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres, within the ``360-850 nm`` model
        range. Defaults to the model sampling grid.
    observer_degree
        ``2`` or ``10``. Selects default photopigment optical density and
        macular density when those parameters are not explicitly supplied.
    photopigment_od
        Optional L/M/S peak photopigment optical densities.
    macular_density_460
        Macular pigment optical density at 460 nm. If omitted, the model uses
        the 2-degree or 10-degree default.
    lens_density_400
        Lens optical density scale at 400 nm.
    l_shift_nm, m_shift_nm, s_shift_nm
        L/M/S photopigment wavelength shifts in nanometres.
    l_template
        L-cone template, one of ``"mean"``, ``"ser180"`` or ``"ala180"``.

    Returns
    -------
    dict[str, ndarray]
        Component mapping with ``wavelength``, shifted
        ``photopigment_absorbance``, ``photopigment_od``,
        ``retinal_absorptance``, individual ``macular_density`` and
        ``lens_density``, ``prereceptoral_density``, ``corneal_quantal`` and
        final ``corneal_energy`` arrays.

    Notes
    -----
    The returned components are already evaluated for the current observer
    parameters. ``corneal_energy`` is the source of the final L/M/S curves
    returned by ``generate_stockman_rider_2023_individual_cone_fundamentals``.

    Examples
    --------
    >>> components = stockman_rider_2023_model_components(l_shift_nm=2.0)
    >>> components["corneal_energy"].shape[1]
    3
    """
    wavelengths = as_wavelengths(wavelength_nm)
    degree = _observer_degree(observer_degree)

    if photopigment_od is None:
        photopigment_od = DEFAULT_PHOTOPIGMENT_OD[degree]
    od = np.asarray(photopigment_od, dtype=np.float64)
    if od.shape != (3,) or not np.all(np.isfinite(od)) or np.any(od < 0):
        raise ValueError("photopigment_od must contain three finite non-negative values")

    if macular_density_460 is None:
        macular_density_460 = DEFAULT_MACULAR_DENSITY_460[degree]
    macular_density_460 = _validate_non_negative(
        macular_density_460,
        "macular_density_460",
    )
    lens_density_400 = _validate_non_negative(lens_density_400, "lens_density_400")

    absorbance_raw = cone_absorbance_spectra(
        wavelengths,
        l_shift_nm=l_shift_nm,
        m_shift_nm=m_shift_nm,
        s_shift_nm=s_shift_nm,
        l_template=l_template,
    )
    absorbance = _column_stack(absorbance_raw)
    retinal = retinal_absorptance(absorbance, od)

    macular = macular_density_spectrum(wavelengths)["optical_density"]
    lens = lens_density_spectrum(wavelengths)["optical_density"]
    macular_scale = macular_density_460 / MACULAR_TEMPLATE_460
    lens_scale = lens_density_400 / LENS_TEMPLATE_400
    prereceptoral_density = macular_scale * macular + lens_scale * lens

    corneal_quantal = apply_prereceptoral_filtering(retinal, prereceptoral_density)
    corneal_energy = quantal_to_energy(corneal_quantal, wavelengths)

    return {
        "wavelength": wavelengths,
        "photopigment_absorbance": absorbance,
        "photopigment_od": od,
        "retinal_absorptance": retinal,
        "macular_density": macular_scale * macular,
        "lens_density": lens_scale * lens,
        "prereceptoral_density": prereceptoral_density,
        "corneal_quantal": corneal_quantal,
        "corneal_energy": corneal_energy,
    }


def generate_stockman_rider_2023_individual_cone_fundamentals(
    wavelength_nm: np.ndarray | None = None,
    *,
    observer_degree: int = 2,
    photopigment_od: tuple[float, float, float] | None = None,
    macular_density_460: float | None = None,
    lens_density_400: float = DEFAULT_LENS_DENSITY_400,
    l_shift_nm: float = 0.0,
    m_shift_nm: float = 0.0,
    s_shift_nm: float = 0.0,
    l_template: str = "mean",
) -> GeneratedConeDict:
    """Generate Stockman/Rider 2023 corneal-energy LMS fundamentals.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres, within ``360-850 nm``.
    observer_degree
        ``2`` or ``10`` default observer route.
    photopigment_od, macular_density_460, lens_density_400
        Individual photopigment and prereceptoral density controls.
    l_shift_nm, m_shift_nm, s_shift_nm
        L/M/S photopigment wavelength shifts in nanometres.
    l_template
        L-cone template, one of ``"mean"``, ``"ser180"`` or ``"ala180"``.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"``, ``"l"``, ``"m"`` and ``"s"``.

    Notes
    -----
    Each LMS channel is peak-normalised to 1. Use
    ``stockman_rider_2023_model_components`` when intermediate density,
    absorbance or retinal/corneal stages need inspection.
    """
    components = stockman_rider_2023_model_components(
        wavelength_nm,
        observer_degree=observer_degree,
        photopigment_od=photopigment_od,
        macular_density_460=macular_density_460,
        lens_density_400=lens_density_400,
        l_shift_nm=l_shift_nm,
        m_shift_nm=m_shift_nm,
        s_shift_nm=s_shift_nm,
        l_template=l_template,
    )
    corneal_energy = components["corneal_energy"]
    return {
        "wavelength": components["wavelength"],
        "l": corneal_energy[:, 0],
        "m": corneal_energy[:, 1],
        "s": corneal_energy[:, 2],
    }


__all__ = [
    "macular_density_spectrum",
    "generate_stockman_rider_2023_individual_cone_fundamentals",
]
