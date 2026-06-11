"""Formula-generated blackbody radiation spectra."""

from __future__ import annotations

from typing import List

import numpy as np

from ._registry import GeneratedDict, GeneratorEntry, generate, list_generators, register


_H = 6.62607015e-34
_C = 2.99792458e8
_K = 1.380649e-23
_C1 = 2.0 * np.pi * _H * _C**2
_C2 = _H * _C / _K


def blackbody_spd(
    wavelength_nm: np.ndarray | None = None,
    temperature: float = 6500.0,
) -> GeneratedDict:
    """Compute Planck blackbody spectral radiance.

    Parameters
    ----------
    wavelength_nm
        Wavelength samples in nanometres. Defaults to ``300-830 nm`` at
        ``1 nm`` spacing.
    temperature
        Blackbody temperature in kelvin.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"`` and ``"radiance"`` columns.

    Notes
    -----
    The returned radiance is not peak-normalised and is not scaled to
    ``Y=100``. Downstream colour values therefore preserve the physical scale
    implied by Planck's law.
    """
    if temperature <= 0:
        raise ValueError(f"temperature must be positive, got {temperature}")

    if wavelength_nm is None:
        wavelength_nm = np.arange(300, 831, 1.0, dtype=np.float64)
    else:
        wavelength_nm = np.asarray(wavelength_nm, dtype=np.float64)

    wl_m = wavelength_nm * 1e-9
    exponent = _C2 / (wl_m * temperature)
    radiance = _C1 / (wl_m**5 * (np.exp(exponent) - 1.0))
    return {"wavelength": wavelength_nm, "radiance": radiance}


register(GeneratorEntry(
    category="blackbody",
    name="blackbody_spd",
    description="Planck blackbody spectral radiance at arbitrary temperature",
    generate_fn=blackbody_spd,
    parameters=("temperature", "wavelength_nm"),
    metadata={
        "quantity": "spectral_radiance",
        "wavelength_unit": "nm",
        "reference": "Planck law",
    },
))


def generate_blackbody(name: str = "blackbody_spd", **kwargs) -> GeneratedDict:
    """Generate registered blackbody radiation spectral data."""
    return generate("blackbody", name, **kwargs)


def list_blackbody_generators() -> List[str]:
    """List registered blackbody generators."""
    return list_generators("blackbody")
