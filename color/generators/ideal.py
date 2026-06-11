"""Formula-generated idealised spectral distributions."""

from __future__ import annotations

from typing import List

import numpy as np

from color.math import gaussian_values, gaussian_values_from_fwhm

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
    """Generate a constant ideal spectral distribution.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres. Defaults to ``360-780 nm`` at
        ``1 nm`` spacing.
    value
        Constant value assigned to all wavelengths.
    column
        Name of the generated value column.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"`` and ``column``.
    """
    wavelengths = _as_wavelengths(wavelength_nm)
    return {
        "wavelength": wavelengths,
        column: np.full(wavelengths.shape, value, dtype=np.float64),
    }


def zero_spd(
    wavelength_nm: np.ndarray | None = None,
    column: str = "spd",
) -> GeneratedDict:
    """Generate a zero-valued ideal spectral distribution."""
    return constant_spd(wavelength_nm=wavelength_nm, value=0.0, column=column)


def equal_energy_spd(
    wavelength_nm: np.ndarray | None = None,
    column: str = "spd",
) -> GeneratedDict:
    """Generate a unit-valued equal-energy ideal spectral distribution."""
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

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres.
    peak_wavelength
        Gaussian centre wavelength in nanometres.
    width
        Standard deviation when ``method="normal"``; full width at half
        maximum when ``method="fwhm"``.
    method
        Width interpretation, ``"normal"`` or ``"fwhm"``.
    amplitude
        Peak amplitude.
    column
        Name of the generated value column.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"`` and ``column``.

    Notes
    -----
    This is a mathematical Gaussian curve. LED spectra use a separate Ohno
    2005 LED model in ``color.generators.leds``.
    """
    if width <= 0:
        raise ValueError(f"width must be positive, got {width}")

    wavelengths = _as_wavelengths(wavelength_nm)
    method_key = method.strip().lower().replace("-", "").replace("_", "")
    if method_key == "normal":
        values = gaussian_values(
            wavelengths,
            amplitude=amplitude,
            center=peak_wavelength,
            sigma=width,
        )
    elif method_key == "fwhm":
        values = gaussian_values_from_fwhm(
            wavelengths,
            amplitude=amplitude,
            center=peak_wavelength,
            fwhm=width,
        )
    else:
        raise ValueError("method must be 'normal' or 'fwhm'")

    return {"wavelength": wavelengths, column: values}


def _as_component_values(
    value: np.ndarray | List[float] | tuple[float, ...] | float,
    *,
    size: int,
    name: str,
) -> np.ndarray:
    """Return component values, allowing scalar broadcast or exact length."""
    values = np.asarray(value, dtype=np.float64)
    if values.ndim == 0:
        return np.full(size, float(values), dtype=np.float64)
    if values.ndim != 1 or values.size != size:
        raise ValueError(f"{name} must be a scalar or a one-dimensional array of length {size}")
    return values


def multi_gaussian_spd(
    wavelength_nm: np.ndarray | None = None,
    peak_wavelengths: np.ndarray | List[float] | tuple[float, ...] = (450.0, 550.0, 650.0),
    widths: np.ndarray | List[float] | tuple[float, ...] | float = 25.0,
    amplitudes: np.ndarray | List[float] | tuple[float, ...] | float | None = None,
    method: str = "normal",
    column: str = "spd",
) -> GeneratedDict:
    """Generate an idealised multi-Gaussian spectral distribution.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres.
    peak_wavelengths
        Component centre wavelengths in nanometres.
    widths
        Scalar shared width or one width per component.
    amplitudes
        Optional scalar shared amplitude or one amplitude per component.
    method
        Width interpretation, ``"normal"`` or ``"fwhm"``.
    column
        Name of the generated value column.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"`` and summed ``column``.

    Notes
    -----
    Component arrays must either be scalar or match ``peak_wavelengths`` in
    length. Short arrays are rejected instead of being silently repeated.
    """
    wavelengths = _as_wavelengths(wavelength_nm)
    peaks = np.asarray(peak_wavelengths, dtype=np.float64)
    if peaks.ndim != 1 or peaks.size == 0:
        raise ValueError("peak_wavelengths must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(peaks)):
        raise ValueError("peak_wavelengths must contain finite values")

    widths_arr = _as_component_values(widths, size=peaks.size, name="widths")
    if np.any(widths_arr <= 0) or not np.all(np.isfinite(widths_arr)):
        raise ValueError("widths must contain finite positive values")

    if amplitudes is None:
        amplitudes_arr = np.ones(peaks.shape, dtype=np.float64)
    else:
        amplitudes_arr = _as_component_values(amplitudes, size=peaks.size, name="amplitudes")
    if not np.all(np.isfinite(amplitudes_arr)):
        raise ValueError("amplitudes must contain finite values")

    method_key = method.strip().lower().replace("-", "").replace("_", "")
    values = np.zeros(wavelengths.shape, dtype=np.float64)
    for peak, width, amplitude in zip(peaks, widths_arr, amplitudes_arr):
        if method_key == "normal":
            component = gaussian_values(
                wavelengths,
                amplitude=float(amplitude),
                center=float(peak),
                sigma=float(width),
            )
        elif method_key == "fwhm":
            component = gaussian_values_from_fwhm(
                wavelengths,
                amplitude=float(amplitude),
                center=float(peak),
                fwhm=float(width),
            )
        else:
            raise ValueError("method must be 'normal' or 'fwhm'")
        values = values + component

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

register(GeneratorEntry(
    category="ideal",
    name="multi_gaussian",
    description="Idealised multi-Gaussian spectral distribution",
    generate_fn=multi_gaussian_spd,
    parameters=("peak_wavelengths", "widths", "amplitudes", "method", "wavelength_nm", "column"),
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))


def generate_ideal(name: str, **kwargs) -> GeneratedDict:
    """Generate a registered idealised spectral distribution."""
    return generate("ideal", name, **kwargs)


def list_ideal_generators() -> List[str]:
    """List registered ideal spectral generators."""
    return list_generators("ideal")
