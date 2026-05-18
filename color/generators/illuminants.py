"""Formula-generated CIE illuminant spectra."""

from __future__ import annotations

from typing import List

import numpy as np

from ._registry import GeneratedDict, GeneratorEntry, generate, list_generators, register


def illuminant_a_spd(
    wavelength_nm: np.ndarray | None = None,
) -> GeneratedDict:
    """Compute CIE Standard Illuminant A relative spectral power distribution."""
    if wavelength_nm is None:
        wavelength_nm = np.arange(300, 831, 1.0, dtype=np.float64)
    else:
        wavelength_nm = np.asarray(wavelength_nm, dtype=np.float64)

    spd = (
        100.0
        * (560.0 / wavelength_nm) ** 5
        * (
            np.expm1((1.435 * 10**7) / (2848.0 * 560.0))
            / np.expm1((1.435 * 10**7) / (2848.0 * wavelength_nm))
        )
    )
    return {"wavelength": wavelength_nm, "spd": spd}


def daylight_spd(
    wavelength_nm: np.ndarray | None = None,
    cct: float = 6500.0,
) -> GeneratedDict:
    """Compute CIE D-series relative spectral power distribution."""
    if not 4000 <= cct <= 25000:
        raise ValueError(f"CCT must be between 4000 and 25000 K, got {cct}")

    if wavelength_nm is None:
        wavelength_nm = np.arange(300, 831, 10.0, dtype=np.float64)
    else:
        wavelength_nm = np.asarray(wavelength_nm, dtype=np.float64)

    if cct <= 7000:
        xD = -4.6070e9 / cct**3 + 2.9678e6 / cct**2 + 0.09911e3 / cct + 0.244063
    else:
        xD = -2.0064e9 / cct**3 + 1.9018e6 / cct**2 + 0.24748e3 / cct + 0.237040

    yD = -3.0 * xD**2 + 2.870 * xD - 0.275

    M = 0.0241 + 0.2562 * xD - 0.7341 * yD
    M1 = (-1.3515 - 1.7703 * xD + 5.9114 * yD) / M
    M2 = (0.0300 - 31.4424 * xD + 30.0717 * yD) / M

    wl_basis = np.arange(300, 831, 10.0, dtype=np.float64)
    s0_basis = np.array([
        0.04, 6.00, 29.60, 55.30, 57.30, 61.80, 61.50, 68.80, 63.40, 65.80,
        94.80, 104.80, 105.90, 96.80, 113.90, 125.60, 125.50, 121.30, 121.30,
        113.50, 113.10, 110.80, 106.50, 108.80, 105.30, 104.40, 100.00, 96.00,
        95.10, 89.10, 90.50, 90.30, 88.40, 84.00, 85.10, 81.90, 82.60, 84.90,
        81.30, 71.90, 74.30, 76.40, 63.30, 71.70, 77.00, 65.20, 47.70, 68.60,
        65.00, 66.00, 61.00, 53.30, 58.90, 61.90,
    ], dtype=np.float64)
    s1_basis = np.array([
        0.02, 4.50, 22.40, 42.00, 40.60, 41.60, 38.00, 42.40, 38.50, 35.00,
        43.40, 46.30, 43.90, 37.10, 36.70, 35.90, 32.60, 27.90, 24.30, 20.10,
        16.20, 13.20, 8.60, 6.10, 4.20, 1.90, 0.00, -1.60, -3.50, -3.50,
        -5.80, -7.20, -8.60, -9.50, -10.90, -10.70, -12.00, -14.00, -13.60,
        -12.00, -13.30, -12.90, -10.60, -11.60, -12.20, -10.20, -7.80, -11.20,
        -10.40, -10.60, -9.70, -8.30, -9.30, -9.80,
    ], dtype=np.float64)
    s2_basis = np.array([
        0.00, 2.00, 4.00, 8.50, 7.80, 6.70, 5.30, 6.10, 2.00, 1.20,
        -1.10, -0.50, -0.70, -1.20, -2.60, -2.90, -2.80, -2.60, -2.60, -1.80,
        -1.50, -1.30, -1.20, -1.00, -0.50, -0.30, 0.00, 0.20, 0.50, 2.10,
        3.20, 4.10, 4.70, 5.10, 6.70, 7.30, 8.60, 9.80, 10.20, 8.30,
        9.60, 8.50, 7.00, 7.60, 8.00, 6.70, 5.20, 7.40, 6.80, 7.00,
        6.40, 5.50, 6.10, 6.50,
    ], dtype=np.float64)

    s0 = np.interp(wavelength_nm, wl_basis, s0_basis)
    s1 = np.interp(wavelength_nm, wl_basis, s1_basis)
    s2 = np.interp(wavelength_nm, wl_basis, s2_basis)

    spd = s0 + M1 * s1 + M2 * s2
    spd = np.clip(spd, 0.0, None)

    return {"wavelength": wavelength_nm, "spd": spd}


register(GeneratorEntry(
    category="illuminants",
    name="A",
    description="CIE Standard Illuminant A",
    generate_fn=illuminant_a_spd,
    parameters=("wavelength_nm",),
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
        "reference": "CIE Standard Illuminant A",
    },
))

register(GeneratorEntry(
    category="illuminants",
    name="cie_d_daylight",
    description="CIE D-series daylight SPD at arbitrary CCT",
    generate_fn=daylight_spd,
    parameters=("cct", "wavelength_nm"),
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
        "reference": "CIE D-series daylight model",
    },
))


def generate_illuminant(name: str, **kwargs) -> GeneratedDict:
    """Generate a CIE illuminant spectral distribution."""
    return generate("illuminants", name, **kwargs)


def list_illuminant_generators() -> List[str]:
    """List registered illuminant generators."""
    return list_generators("illuminants")
