"""Colorimetric computations from spectral object wrappers."""

from __future__ import annotations

from .chromaticity import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ
from .cone_responses import (
    DEFAULT_FUNDAMENTALS,
    DEFAULT_ILLUMINANT,
    emission_to_LMS,
)
from .cone_responses import reflectance_to_LMS
from .lightness import Lstar_to_Y, Y_to_Lstar
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
from .tristimulus import DEFAULT_CMFS, emission_to_XYZ, reflectance_to_XYZ
from .transformations import LMS_to_XYZ, XYZ_to_LMS

# Spectral-conversion defaults.
__all__ = [
    "DEFAULT_CMFS",
    "DEFAULT_FUNDAMENTALS",
    "DEFAULT_ILLUMINANT",
]

# Photometry defaults.
__all__ += [
    "DEFAULT_PHOTOPIC_LEF",
    "DEFAULT_SCOTOPIC_LEF",
    "DEFAULT_PHOTOPIC_K_M",
    "DEFAULT_SCOTOPIC_K_M",
]

# Chromaticity conversions.
__all__ += [
    "XYZ_to_xyY",
    "xyY_to_XYZ",
    "XYZ_to_xy",
]

# CIE 1976 lightness conversions.
__all__ += [
    "Y_to_Lstar",
    "Lstar_to_Y",
]

# Direct colour-response transformations.
__all__ += [
    "LMS_to_XYZ",
    "XYZ_to_LMS",
]

# Spectral to colorimetric-response conversions.
__all__ += [
    "emission_to_XYZ",
    "reflectance_to_XYZ",
    "emission_to_LMS",
    "reflectance_to_LMS",
]

# Luminous efficiency functions.
__all__ += [
    "photopic_luminous_efficiency_function",
    "scotopic_luminous_efficiency_function",
]

# Generic photometric quantities.
__all__ += [
    "luminous_flux",
    "luminous_efficiency",
    "luminous_efficacy",
]

# Safe photopic and scotopic photometric wrappers.
__all__ += [
    "photopic_luminous_flux",
    "scotopic_luminous_flux",
    "photopic_luminous_efficiency",
    "scotopic_luminous_efficiency",
    "photopic_luminous_efficacy",
    "scotopic_luminous_efficacy",
]
