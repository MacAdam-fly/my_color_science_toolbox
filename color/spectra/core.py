"""Compatibility exports for spectral object wrappers."""

from __future__ import annotations

from .convert import (
    from_D65_illuminant,
    from_asano2016_individual_cone_fundamentals,
    from_cie1931_xyz_cmfs,
    from_cie1964_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_cie2006_lms_10degree_fundamentals,
    from_cie2012_xyz_2degree_cmfs,
    from_cie2012_xyz_10degree_cmfs,
    from_columns,
    from_dataset,
    from_stockman_rider_2023_individual_cone_fundamentals,
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
    "from_D65_illuminant",
    "from_cie1931_xyz_cmfs",
    "from_cie1964_xyz_cmfs",
    "from_cie2012_xyz_2degree_cmfs",
    "from_cie2012_xyz_10degree_cmfs",
    "from_cie2006_lms_2degree_fundamentals",
    "from_cie2006_lms_10degree_fundamentals",
    "from_stockman_rider_2023_individual_cone_fundamentals",
    "from_asano2016_individual_cone_fundamentals",
]
