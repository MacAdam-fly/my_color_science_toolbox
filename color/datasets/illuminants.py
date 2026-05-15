"""Standard illuminant spectral power distributions.

Provides file-based access to CIE A, D65, fluorescent (F1–F12), and
pre-tabulated daylight/blackbody data, **plus** on-the-fly computation of:

* **Blackbody radiation** at any temperature via Planck's law.
* **CIE D-series (daylight)** at any correlated colour temperature (4000–25000 K)
  via the CIE method (Wyszecki & Stiles, *Color Science*, §3.3.4).

Usage::

    from color.datasets.illuminants import get_illuminant, list_illuminants

    # File-based
    d65 = get_illuminant('D65')

    # Computed
    bb = get_illuminant('blackbody', temperature=6500)
    d50 = get_illuminant('daylight', cct=5000)
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from ._registry import DatasetEntry, register, register_computed, SpectralDict
from ._utils import data_dir

# ---------------------------------------------------------------------------
# Physical constants for Planck's law
# ---------------------------------------------------------------------------

_H = 6.62607015e-34   # Planck constant (J·s)
_C = 2.99792458e8     # Speed of light (m/s)
_K = 1.380649e-23     # Boltzmann constant (J/K)
_C1 = 2.0 * np.pi * _H * _C ** 2   # first radiation constant
_C2 = _H * _C / _K                   # second radiation constant


# ---------------------------------------------------------------------------
# Computed: Blackbody radiation (Planck's law)
# ---------------------------------------------------------------------------

def _blackbody(
    wavelength_nm: np.ndarray | None = None,
    temperature: float = 6500.0,
) -> SpectralDict:
    """Compute Planck spectral radiance at *temperature* (K).

    Parameters
    ----------
    wavelength_nm : array, optional
        Wavelengths in nm.  Defaults to 300–830 nm, 1 nm step.
    temperature : float
        Blackbody temperature in kelvin.
    """
    from ._utils import attest

    attest(temperature > 0, f"temperature must be positive, got {temperature}")

    if wavelength_nm is None:
        wavelength_nm = np.arange(300, 831, 1.0, dtype=np.float64)
    wl_m = wavelength_nm * 1e-9  # nm → m
    # Planck spectral radiance: L(λ) = c1 / (λ⁵ (exp(c2/λT) − 1))
    exponent = _C2 / (wl_m * temperature)
    radiance = _C1 / (wl_m ** 5 * (np.exp(exponent) - 1.0))
    return {"wavelength": wavelength_nm, "radiance": radiance}


# ---------------------------------------------------------------------------
# Computed: CIE D-series daylight
# ---------------------------------------------------------------------------

def _daylight(
    wavelength_nm: np.ndarray | None = None,
    cct: float = 6500.0,
) -> SpectralDict:
    """Compute CIE D-series relative spectral power distribution.

    Implements the CIE method for correlated colour temperatures from
    4000 K to 25000 K (Wyszecki & Stiles, *Color Science*, §3.3.4).

    Parameters
    ----------
    wavelength_nm : array, optional
        Wavelengths in nm.  Defaults to 300–830 nm, 5 nm step.
    cct : float
        Correlated colour temperature in kelvin (4000–25000).
    """
    if not 4000 <= cct <= 25000:
        raise ValueError(
            f"CCT must be between 4000 and 25000 K, got {cct}"
        )

    if wavelength_nm is None:
        wavelength_nm = np.arange(300, 831, 10.0, dtype=np.float64)

    # --- CIE chromaticity of D-series illuminant from CCT ---
    # 1. CCT → chromaticity (xD, yD)
    if cct <= 7000:
        xD = -4.6070e9 / cct ** 3 + 2.9678e6 / cct ** 2 + 0.09911e3 / cct + 0.244063
    else:
        xD = -2.0064e9 / cct ** 3 + 1.9018e6 / cct ** 2 + 0.24748e3 / cct + 0.237040

    yD = -3.0 * xD ** 2 + 2.870 * xD - 0.275

    # 2. Spectral components M1, M2
    M = 0.0241 + 0.2562 * xD - 0.7341 * yD
    M1 = (-1.3515 - 1.7703 * xD + 5.9114 * yD) / M
    M2 = (0.0300 - 31.4424 * xD + 30.0717 * yD) / M

    # 3. Basis functions S0(λ), S1(λ), S2(λ) — CIE standard
    #    Tabulated at 10 nm intervals, 300–830 nm (54 points)
    #    Source: Wyszecki & Stiles, Table IV(3.3.4)
    _wl_basis = np.arange(300, 831, 10.0, dtype=np.float64)

    # fmt: off
    S0 = np.array([
        0.04, 6.00, 29.60, 55.30, 57.30, 61.80, 61.50, 68.80, 63.40, 65.80,
        94.80, 104.80, 105.90, 96.80, 113.90, 125.60, 125.50, 121.30, 121.30,
        113.50, 113.10, 110.80, 106.50, 108.80, 105.30, 104.40, 100.00, 96.00,
        95.10, 89.10, 90.50, 90.30, 88.40, 84.00, 85.10, 81.90, 82.60, 84.90,
        81.30, 71.90, 74.30, 76.40, 63.30, 71.70, 77.00, 65.20, 47.70, 68.60,
        65.00, 66.00, 61.00, 53.30, 58.90, 61.90,
    ], dtype=np.float64)

    S1 = np.array([
        0.02, 4.50, 22.40, 42.00, 40.60, 41.60, 38.00, 42.40, 38.50, 35.00,
        43.40, 46.30, 43.90, 37.10, 36.70, 35.90, 32.60, 27.90, 24.30, 20.10,
        16.20, 13.20, 8.60, 6.10, 4.20, 1.90, 0.00, -1.60, -3.50, -3.50,
        -5.80, -7.20, -8.60, -9.50, -10.90, -10.70, -12.00, -14.00, -13.60,
        -12.00, -13.30, -12.90, -10.60, -11.60, -12.20, -10.20, -7.80, -11.20,
        -10.40, -10.60, -9.70, -8.30, -9.30, -9.80,
    ], dtype=np.float64)

    S2 = np.array([
        0.00, 2.00, 4.00, 8.50, 7.80, 6.70, 5.30, 6.10, 2.00, 1.20,
        -1.10, -0.50, -0.70, -1.20, -2.60, -2.90, -2.80, -2.60, -2.60, -1.80,
        -1.50, -1.30, -1.20, -1.00, -0.50, -0.30, 0.00, 0.20, 0.50, 2.10,
        3.20, 4.10, 4.70, 5.10, 6.70, 7.30, 8.60, 9.80, 10.20, 8.30,
        9.60, 8.50, 7.00, 7.60, 8.00, 6.70, 5.20, 7.40, 6.80, 7.00,
        6.40, 5.50, 6.10, 6.50,
    ], dtype=np.float64)
    # fmt: on

    # 4. Interpolate S0, S1, S2 to requested wavelengths
    s0 = np.interp(wavelength_nm, _wl_basis, S0)
    s1 = np.interp(wavelength_nm, _wl_basis, S1)
    s2 = np.interp(wavelength_nm, _wl_basis, S2)

    spd = s0 + M1 * s1 + M2 * s2
    spd = np.clip(spd, 0.0, None)

    return {"wavelength": wavelength_nm, "spd": spd}


# ---------------------------------------------------------------------------
# Register file-based illuminants
# ---------------------------------------------------------------------------

_ILLUM_DIR = str(data_dir("illuminants"))

register(DatasetEntry(
    category="illuminants",
    name="A",
    description="CIE Illuminant A — typical incandescent/tungsten (~2856 K)",
    source="CVRL / CIE 15:2004",
    file_path=f"{_ILLUM_DIR}/illuminant_A.csv",
))

register(DatasetEntry(
    category="illuminants",
    name="D65",
    description="CIE Illuminant D65 — average daylight (~6504 K)",
    source="CVRL / CIE 15:2004",
    file_path=f"{_ILLUM_DIR}/illuminant_D65.csv",
))

register(DatasetEntry(
    category="illuminants",
    name="fluorescents",
    description="CIE F1–F12 fluorescent lamp spectral power distributions",
    source="RIT Munsell Color Science Lab",
    file_path=f"{_ILLUM_DIR}/Fluorescents.xls",
    columns=("wavelength", "F1", "F2", "F3", "F4", "F5", "F6",
             "F7", "F8", "F9", "F10", "F11", "F12"),
    metadata={"header": 1},
))

# ---------------------------------------------------------------------------
# Register computed illuminants
# ---------------------------------------------------------------------------

register_computed(
    category="illuminants",
    name="blackbody",
    compute_fn=_blackbody,
    description="Planck blackbody spectral radiance at arbitrary temperature",
    metadata={"parameters": ["temperature", "wavelength_nm"]},
)

register_computed(
    category="illuminants",
    name="daylight",
    compute_fn=_daylight,
    description="CIE D-series daylight SPD at arbitrary CCT (4000–25000 K)",
    metadata={"parameters": ["cct", "wavelength_nm"]},
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_illuminant(name: str, **kwargs: Any) -> SpectralDict:
    """Load or compute an illuminant spectral distribution.

    Parameters
    ----------
    name : str
        Dataset identifier.  File-based: ``'A'``, ``'D65'``, ``'fluorescents'``.
        Computed: ``'blackbody'``, ``'daylight'``.
    **kwargs
        Forwarded to computed datasets (e.g. ``temperature=6500``, ``cct=5000``).

    Returns
    -------
    dict[str, ndarray]
        ``{'wavelength': ..., 'spd': ...}`` (or ``'radiance'`` for blackbody).
    """
    from ._registry import get
    return get("illuminants", name, **kwargs)


def list_illuminants() -> List[str]:
    """List all registered illuminant names."""
    from ._registry import list_datasets
    return list_datasets("illuminants")
