"""Individual human cone fundamental generators."""

from __future__ import annotations

from .constants import STOCKMAN_RIDER_REFERENCE
from .generation import generate_individual_cone_fundamentals
from .templates import (
    cone_absorbance_spectra,
    lens_density_spectrum,
    macular_density_spectrum,
)

__all__ = [
    "STOCKMAN_RIDER_REFERENCE",  # Stockman/Rider 2023 model reference text
]

__all__ += [
    "macular_density_spectrum",  # generate macular pigment density spectrum
    "lens_density_spectrum",  # generate lens density spectrum
    "cone_absorbance_spectra",  # generate L/M/S photopigment absorbance spectra
]

__all__ += [
    "generate_individual_cone_fundamentals",  # generate individualised LMS cone fundamentals
]
