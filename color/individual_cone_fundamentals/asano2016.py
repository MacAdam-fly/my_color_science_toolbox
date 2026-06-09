"""Asano et al. 2016 individual colorimetric observer model."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

from color.datasets.standard_observers import get_standard_observer

from ._constants import DEFAULT_ASANO2016_WAVELENGTHS_NM, GeneratedConeDict
from ._transforms import normalise_to_peak


def _as_wavelengths(wavelength_nm: np.ndarray | None) -> np.ndarray:
    """Return wavelengths as a finite one-dimensional array in 390-830 nm."""
    if wavelength_nm is None:
        wavelengths = DEFAULT_ASANO2016_WAVELENGTHS_NM
    else:
        wavelengths = np.asarray(wavelength_nm, dtype=np.float64)
    if wavelengths.ndim != 1 or wavelengths.size == 0:
        raise ValueError("wavelength_nm must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(wavelengths)):
        raise ValueError("wavelength_nm must be finite")
    if np.any(wavelengths < 390.0) or np.any(wavelengths > 830.0):
        raise ValueError("wavelength_nm must be within the 390-830 nm Asano model range")
    if np.any(np.diff(wavelengths) <= 0):
        raise ValueError("wavelength_nm must be strictly increasing")
    return np.array(wavelengths, dtype=np.float64, copy=True)


def _as_positive_float(value: float, name: str) -> float:
    """Return *value* as a finite positive float."""
    value = float(value)
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive value")
    return value


def _as_density_deviation(value: float, name: str) -> float:
    """Return a finite density deviation percentage."""
    value = float(value)
    if not np.isfinite(value) or value < -100.0:
        raise ValueError(f"{name} must be finite and greater than or equal to -100")
    return value


def _as_triplet(values: tuple[float, float, float], name: str) -> np.ndarray:
    """Return *values* as a finite length-3 float array."""
    result = np.asarray(values, dtype=np.float64)
    if result.shape != (3,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain three finite values")
    return result


def _as_density_deviation_triplet(
    values: tuple[float, float, float],
    name: str,
) -> np.ndarray:
    """Return density deviation percentages for L, M and S photopigments."""
    result = _as_triplet(values, name)
    if np.any(result < -100.0):
        raise ValueError(f"{name} values must be greater than or equal to -100")
    return result


def _linear_interpolate(
    source_wavelengths: np.ndarray,
    values: np.ndarray,
    target_wavelengths: np.ndarray,
) -> np.ndarray:
    """Linearly interpolate a one-dimensional spectral template."""
    return np.interp(target_wavelengths, source_wavelengths, values)


def _spline_shifted_absorbance(
    source_wavelengths: np.ndarray,
    values: np.ndarray,
    target_wavelengths: np.ndarray,
    shift_nm: float,
) -> np.ndarray:
    """Return shifted low-density absorbance using cubic spline interpolation."""
    finite = np.isfinite(source_wavelengths) & np.isfinite(values)
    if np.count_nonzero(finite) < 4:
        raise ValueError("photopigment absorbance template must contain finite samples")
    spline = CubicSpline(
        source_wavelengths[finite],
        values[finite],
        bc_type="natural",
        extrapolate=False,
    )
    shifted = spline(target_wavelengths - shift_nm)
    shifted = np.where(np.isfinite(shifted), shifted, 0.0)
    return np.clip(shifted, 0.0, None)


def _load_ciepo06_templates(target_wavelengths: np.ndarray) -> tuple[np.ndarray, ...]:
    """Load and interpolate CIEPO06 templates needed by the Asano model."""
    photopigments = get_standard_observer("photopigments", "ss_psycho_5nm")
    pigment_wavelengths = np.asarray(photopigments["wavelength"], dtype=np.float64)
    # ss_psycho stores low-density absorbance as log10 relative absorbance.
    low_density_absorbance = np.column_stack((
        10.0 ** np.asarray(photopigments["l"], dtype=np.float64),
        10.0 ** np.asarray(photopigments["m"], dtype=np.float64),
        10.0 ** np.asarray(photopigments["s"], dtype=np.float64),
    ))

    macular = get_standard_observer("prereceptoral_filters", "macular_ss_5nm")
    macular_wavelengths = np.asarray(macular["wavelength"], dtype=np.float64)
    macular_density = np.asarray(macular["optical_density"], dtype=np.float64)
    macular_relative = macular_density / np.max(macular_density)
    macular_relative = _linear_interpolate(
        macular_wavelengths,
        macular_relative,
        target_wavelengths,
    )

    lens = get_standard_observer(
        "prereceptoral_filters",
        "lens_ciepo06_components_5nm",
    )
    lens_wavelengths = np.asarray(lens["wavelength"], dtype=np.float64)
    lens_1 = _linear_interpolate(
        lens_wavelengths,
        np.asarray(lens["d_ocul1"], dtype=np.float64),
        target_wavelengths,
    )
    lens_2 = _linear_interpolate(
        lens_wavelengths,
        np.asarray(lens["d_ocul2"], dtype=np.float64),
        target_wavelengths,
    )
    return pigment_wavelengths, low_density_absorbance, macular_relative, lens_1, lens_2


def _age_lens_factor(age: float) -> float:
    """Return the CIEPO06 age factor for the first ocular media component."""
    if age <= 60.0:
        return 1.0 + 0.02 * (age - 32.0)
    return 1.56 + 0.0667 * (age - 60.0)


def _photopigment_optical_densities(
    field_size_degree: float,
    deviations: np.ndarray,
) -> np.ndarray:
    """Return L, M and S peak photopigment optical densities."""
    common = np.exp(-field_size_degree / 1.333)
    base = np.array((
        0.38 + 0.54 * common,
        0.38 + 0.54 * common,
        0.30 + 0.45 * common,
    ))
    return base * (1.0 + deviations / 100.0)


def asano2016_model_components(
    wavelength_nm: np.ndarray | None = None,
    *,
    age: float = 32.0,
    field_size_degree: float = 2.0,
    lens_density_deviation: float = 0.0,
    macular_density_deviation: float = 0.0,
    photopigment_od_deviation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    photopigment_shift_nm: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> GeneratedConeDict:
    """Return Asano et al. 2016 model components for one observer."""
    wavelengths = _as_wavelengths(wavelength_nm)
    age = _as_positive_float(age, "age")
    field = _as_positive_float(field_size_degree, "field_size_degree")
    lens_deviation = _as_density_deviation(
        lens_density_deviation,
        "lens_density_deviation",
    )
    macular_deviation = _as_density_deviation(
        macular_density_deviation,
        "macular_density_deviation",
    )
    od_deviation = _as_density_deviation_triplet(
        photopigment_od_deviation,
        "photopigment_od_deviation",
    )
    shifts = _as_triplet(photopigment_shift_nm, "photopigment_shift_nm")

    (
        pigment_wavelengths,
        low_density_absorbance,
        macular_relative,
        lens_1,
        lens_2,
    ) = _load_ciepo06_templates(wavelengths)

    shifted_absorbance = np.column_stack([
        _spline_shifted_absorbance(
            pigment_wavelengths,
            low_density_absorbance[:, index],
            wavelengths,
            shifts[index],
        )
        for index in range(3)
    ])

    photopigment_od = _photopigment_optical_densities(field, od_deviation)
    retinal_absorptance = 1.0 - 10.0 ** (-shifted_absorbance * photopigment_od)

    lens_average = lens_1 * _age_lens_factor(age) + lens_2
    lens_density = lens_average * (1.0 + lens_deviation / 100.0)
    macular_peak_density = 0.485 * np.exp(-field / 6.132)
    macular_density = macular_peak_density * (1.0 + macular_deviation / 100.0)
    prereceptoral_density = lens_density + macular_density * macular_relative

    corneal_quantal = retinal_absorptance * 10.0 ** (-prereceptoral_density[:, None])
    corneal_energy = normalise_to_peak(corneal_quantal * wavelengths[:, None])

    return {
        "wavelength": wavelengths,
        "photopigment_absorbance": shifted_absorbance,
        "photopigment_od": photopigment_od,
        "retinal_absorptance": retinal_absorptance,
        "macular_density": macular_density * macular_relative,
        "lens_density": lens_density,
        "prereceptoral_density": prereceptoral_density,
        "corneal_quantal": corneal_quantal,
        "corneal_energy": corneal_energy,
    }


def generate_asano2016_individual_cone_fundamentals(
    wavelength_nm: np.ndarray | None = None,
    *,
    age: float = 32.0,
    field_size_degree: float = 2.0,
    lens_density_deviation: float = 0.0,
    macular_density_deviation: float = 0.0,
    photopigment_od_deviation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    photopigment_shift_nm: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> GeneratedConeDict:
    """Generate Asano et al. 2016 corneal energy LMS cone fundamentals."""
    components = asano2016_model_components(
        wavelength_nm,
        age=age,
        field_size_degree=field_size_degree,
        lens_density_deviation=lens_density_deviation,
        macular_density_deviation=macular_density_deviation,
        photopigment_od_deviation=photopigment_od_deviation,
        photopigment_shift_nm=photopigment_shift_nm,
    )
    corneal_energy = components["corneal_energy"]
    return {
        "wavelength": components["wavelength"],
        "l": corneal_energy[:, 0],
        "m": corneal_energy[:, 1],
        "s": corneal_energy[:, 2],
    }


__all__ = [
    "asano2016_model_components",
    "generate_asano2016_individual_cone_fundamentals",
]
