"""Colorimetric computations from spectral object wrappers."""

from __future__ import annotations

from .chromaticity import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ
from .photometry import (
    DEFAULT_PHOTOPIC_K_M,
    DEFAULT_PHOTOPIC_LEF,
    DEFAULT_SCOTOPIC_K_M,
    DEFAULT_SCOTOPIC_LEF,
    luminous_efficacy,
    luminous_efficiency,
    luminous_flux,
    photopic_luminous_efficacy,
    photopic_luminous_efficiency,
    photopic_luminous_efficiency_function,
    photopic_luminous_flux,
    scotopic_luminous_efficacy,
    scotopic_luminous_efficiency,
    scotopic_luminous_efficiency_function,
    scotopic_luminous_flux,
)
from .spectral_conversion import (
    DEFAULT_CMFS,
    DEFAULT_FUNDAMENTALS,
    DEFAULT_ILLUMINANT,
    emission_to_LMS,
    emission_to_XYZ,
    reflectance_to_LMS,
    reflectance_to_XYZ,
)

__all__ = [
    "DEFAULT_CMFS",
    "DEFAULT_FUNDAMENTALS",
    "DEFAULT_ILLUMINANT",
    "DEFAULT_PHOTOPIC_LEF",
    "DEFAULT_SCOTOPIC_LEF",
    "DEFAULT_PHOTOPIC_K_M",
    "DEFAULT_SCOTOPIC_K_M",
    "XYZ_to_xyY",
    "xyY_to_XYZ",
    "XYZ_to_xy",
    "emission_to_XYZ",
    "reflectance_to_XYZ",
    "emission_to_LMS",
    "reflectance_to_LMS",
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
