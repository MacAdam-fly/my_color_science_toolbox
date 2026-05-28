"""Generation pipeline for Stockman/Rider individual cone fundamentals."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from .constants import (
    DEFAULT_LENS_DENSITY_400,
    DEFAULT_MACULAR_DENSITY_460,
    DEFAULT_PHOTOPIGMENT_OD,
    GeneratedConeDict,
    LENS_TEMPLATE_400,
    MACULAR_TEMPLATE_460,
)
from .templates import (
    as_wavelengths,
    cone_absorbance_spectra,
    lens_density_spectrum,
    macular_density_spectrum,
)
from .transforms import (
    apply_prereceptoral_filtering,
    quantal_to_energy,
    retinal_absorptance,
)


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


def generate_individual_cone_fundamentals(
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
    """Generate Stockman/Rider corneal energy LMS cone fundamentals."""
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
        "l": corneal_energy[:, 0],
        "m": corneal_energy[:, 1],
        "s": corneal_energy[:, 2],
    }


__all__ = ["generate_individual_cone_fundamentals"]
