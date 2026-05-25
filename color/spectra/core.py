"""Compatibility exports for spectral object wrappers."""

from __future__ import annotations

from .convert import (
    from_cie1931_xyz_cmfs,
    from_cie1964_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_cie2006_lms_10degree_fundamentals,
    from_cie2012_xyz_2degree_cmfs,
    from_cie2012_xyz_10degree_cmfs,
    from_columns,
    from_dataset,
)
from .distribution import SpectralDistribution
from .multi_distribution import MultiSpectralDistribution
from .shape import SpectralShape

__all__ = [
    "SpectralShape",
    "SpectralDistribution",
    "MultiSpectralDistribution",
    "from_columns",
    "from_dataset",
    "from_cie1931_xyz_cmfs",
    "from_cie1964_xyz_cmfs",
    "from_cie2012_xyz_2degree_cmfs",
    "from_cie2012_xyz_10degree_cmfs",
    "from_cie2006_lms_2degree_fundamentals",
    "from_cie2006_lms_10degree_fundamentals",
]
