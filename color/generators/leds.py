"""Formula-generated LED spectra."""

from __future__ import annotations

from typing import List

import numpy as np

from ._registry import GeneratedDict, GeneratorEntry, generate, list_generators, register
from .ideal import _as_wavelengths


def single_led_spd(
    wavelength_nm: np.ndarray | None = None,
    peak_wavelength: float = 555.0,
    half_spectral_width: float = 25.0,
    amplitude: float = 1.0,
    column: str = "spd",
) -> GeneratedDict:
    """Generate a single LED SPD using the Ohno 2005 model.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres. Defaults to ``360-780 nm`` at
        ``1 nm`` spacing.
    peak_wavelength
        LED peak wavelength in nanometres.
    half_spectral_width
        Ohno-model half spectral width; must be positive.
    amplitude
        Peak power multiplier.
    column
        Name of the generated value column.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"`` and ``column``.

    Notes
    -----
    This is an empirical LED model, not a standard Gaussian. Use
    ``gaussian_spd`` for a pure mathematical Gaussian curve.
    """
    if half_spectral_width <= 0:
        raise ValueError(
            f"half_spectral_width must be positive, got {half_spectral_width}"
        )

    wavelengths = _as_wavelengths(wavelength_nm)
    values = np.exp(-(((wavelengths - peak_wavelength) / half_spectral_width) ** 2))
    values = amplitude * ((values + 2.0 * values**5) / 3.0)
    return {"wavelength": wavelengths, column: values}


def multi_led_spd(
    wavelength_nm: np.ndarray | None = None,
    peak_wavelengths: np.ndarray | List[float] | tuple[float, ...] = (457.0, 530.0, 615.0),
    half_spectral_widths: np.ndarray | List[float] | tuple[float, ...] = (20.0, 30.0, 20.0),
    peak_power_ratios: np.ndarray | List[float] | tuple[float, ...] | None = None,
    column: str = "spd",
) -> GeneratedDict:
    """Generate a multi-LED SPD by summing Ohno 2005 components.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres.
    peak_wavelengths
        LED peak wavelengths in nanometres.
    half_spectral_widths
        Half spectral widths. Values are resized to the peak array shape.
    peak_power_ratios
        Optional component power multipliers. Values are resized to the peak
        array shape.
    column
        Name of the generated value column.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"`` and summed ``column``.

    Notes
    -----
    This function preserves the existing LED API behavior where width and
    power arrays are resized to match peak wavelengths.
    """
    wavelengths = _as_wavelengths(wavelength_nm)
    peaks = np.asarray(peak_wavelengths, dtype=np.float64)
    widths = np.resize(np.asarray(half_spectral_widths, dtype=np.float64), peaks.shape)
    if peaks.ndim != 1 or peaks.size == 0:
        raise ValueError("peak_wavelengths must be a non-empty one-dimensional array")
    if np.any(widths <= 0):
        raise ValueError("half_spectral_widths must contain only positive values")

    if peak_power_ratios is None:
        ratios = np.ones(peaks.shape, dtype=np.float64)
    else:
        ratios = np.resize(np.asarray(peak_power_ratios, dtype=np.float64), peaks.shape)

    values = np.zeros(wavelengths.shape, dtype=np.float64)
    for peak, width, ratio in zip(peaks, widths, ratios):
        component = single_led_spd(
            wavelength_nm=wavelengths,
            peak_wavelength=float(peak),
            half_spectral_width=float(width),
            amplitude=float(ratio),
            column=column,
        )
        values = values + component[column]

    return {"wavelength": wavelengths, column: values}


register(GeneratorEntry(
    category="leds",
    name="single",
    description="Single LED SPD using the Ohno 2005 model",
    generate_fn=single_led_spd,
    parameters=("peak_wavelength", "half_spectral_width", "amplitude", "wavelength_nm", "column"),
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
        "reference": "Ohno 2005",
    },
))

register(GeneratorEntry(
    category="leds",
    name="multi",
    description="Multi-LED SPD using summed Ohno 2005 components",
    generate_fn=multi_led_spd,
    parameters=(
        "peak_wavelengths",
        "half_spectral_widths",
        "peak_power_ratios",
        "wavelength_nm",
        "column",
    ),
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
        "reference": "Ohno 2005",
    },
))


def generate_led(name: str, **kwargs) -> GeneratedDict:
    """Generate registered LED spectral data."""
    return generate("leds", name, **kwargs)


def list_led_generators() -> List[str]:
    """List registered LED generators."""
    return list_generators("leds")
