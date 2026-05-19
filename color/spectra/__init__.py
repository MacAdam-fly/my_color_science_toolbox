"""Spectral object wrappers for static colour-science datasets."""

from __future__ import annotations

from .convert import from_columns, from_dataset
from .distribution import SpectralDistribution
from .multi_distribution import MultiSpectralDistribution
from .shape import SpectralShape

__all__ = [
    "SpectralShape",  # regular wavelength sampling shape
    "SpectralDistribution",  # single-channel spectral distribution
    "MultiSpectralDistribution",  # multi-channel spectral distribution
    "from_columns",  # wrap raw column arrays as spectral objects
    "from_dataset",  # load a dataset and wrap it as a spectral object
]
