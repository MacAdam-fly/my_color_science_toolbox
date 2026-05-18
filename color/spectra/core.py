"""Compatibility exports for spectral object wrappers."""

from __future__ import annotations

from .convert import from_columns, from_dataset
from .distribution import SpectralDistribution
from .multi_distribution import MultiSpectralDistribution
from .shape import SpectralShape

__all__ = [
    "SpectralShape",
    "SpectralDistribution",
    "MultiSpectralDistribution",
    "from_columns",
    "from_dataset",
]
