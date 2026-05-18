"""Formula-generated idealised spectral distributions."""

from __future__ import annotations

from typing import List

import numpy as np

from ._registry import GeneratedDict, GeneratorEntry, generate, list_generators, register


def _default_wavelengths() -> np.ndarray:
    """Return the default visible spectral domain."""
    return np.arange(360, 781, 1.0, dtype=np.float64)


def _as_wavelengths(wavelength_nm: np.ndarray | None) -> np.ndarray:
    """Return wavelength samples as a one-dimensional float array."""
    if wavelength_nm is None:
        return _default_wavelengths()

    wavelengths = np.asarray(wavelength_nm, dtype=np.float64)
    if wavelengths.ndim != 1:
        raise ValueError("wavelength_nm must be a one-dimensional array")
    if wavelengths.size == 0:
        raise ValueError("wavelength_nm must not be empty")
    return wavelengths


def constant_spd(
    wavelength_nm: np.ndarray | None = None,
    value: float = 1.0,
    column: str = "spd",
) -> GeneratedDict:
    """Generate a constant ideal spectral distribution."""
    wavelengths = _as_wavelengths(wavelength_nm)
    return {
        "wavelength": wavelengths,
        column: np.full(wavelengths.shape, value, dtype=np.float64),
    }


def zero_spd(
    wavelength_nm: np.ndarray | None = None,
    column: str = "spd",
) -> GeneratedDict:
    """Generate a zero ideal spectral distribution."""
    return constant_spd(wavelength_nm=wavelength_nm, value=0.0, column=column)


def equal_energy_spd(
    wavelength_nm: np.ndarray | None = None,
    column: str = "spd",
) -> GeneratedDict:
    """Generate an equal-energy ideal spectral distribution."""
    return constant_spd(wavelength_nm=wavelength_nm, value=1.0, column=column)


def gaussian_spd(
    wavelength_nm: np.ndarray | None = None,
    peak_wavelength: float = 555.0,
    width: float = 25.0,
    method: str = "normal",
    amplitude: float = 1.0,
    column: str = "spd",
) -> GeneratedDict:
    """Generate an idealised Gaussian spectral distribution.

    ``method="normal"`` interprets ``width`` as standard deviation.
    ``method="fwhm"`` interprets ``width`` as full width at half maximum.
    """
    if width <= 0:
        raise ValueError(f"width must be positive, got {width}")

    wavelengths = _as_wavelengths(wavelength_nm)
    method_key = method.strip().lower().replace("-", "").replace("_", "")
    if method_key == "normal":
        sigma = width
    elif method_key == "fwhm":
        sigma = width / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    else:
        raise ValueError("method must be 'normal' or 'fwhm'")

    values = amplitude * np.exp(-((wavelengths - peak_wavelength) ** 2) / (2.0 * sigma**2))
    return {"wavelength": wavelengths, column: values}


register(GeneratorEntry(
    category="ideal",
    name="constant",
    description="Constant ideal spectral distribution",
    generate_fn=constant_spd,
    parameters=("value", "wavelength_nm", "column"),
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))

register(GeneratorEntry(
    category="ideal",
    name="zero",
    description="Zero ideal spectral distribution",
    generate_fn=zero_spd,
    parameters=("wavelength_nm", "column"),
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))

register(GeneratorEntry(
    category="ideal",
    name="equal_energy",
    description="Equal-energy ideal spectral distribution",
    generate_fn=equal_energy_spd,
    parameters=("wavelength_nm", "column"),
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))

register(GeneratorEntry(
    category="ideal",
    name="gaussian",
    description="Idealised Gaussian spectral distribution using normal or FWHM width",
    generate_fn=gaussian_spd,
    parameters=("peak_wavelength", "width", "method", "amplitude", "wavelength_nm", "column"),
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))


def generate_ideal(name: str, **kwargs) -> GeneratedDict:
    """Generate an idealised spectral distribution."""
    return generate("ideal", name, **kwargs)


def list_ideal_generators() -> List[str]:
    """List registered ideal spectral generators."""
    return list_generators("ideal")
