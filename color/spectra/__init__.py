"""Spectral object wrappers for static colour-science datasets."""

from __future__ import annotations

from .convert import (
    from_D65_illuminant,
    from_alpha_opic_action_spectra,
    from_asano2016_individual_cone_fundamentals,
    from_cie1931_xyz_cmfs,
    from_cie1964_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_cie2006_lms_10degree_fundamentals,
    from_cie2012_xyz_2degree_cmfs,
    from_cie2012_xyz_10degree_cmfs,
    from_columns,
    from_dataset,
    from_iprgc_melanopic,
    from_stockman_rider_2023_individual_cone_fundamentals,
)
from .distribution import SpectralDistribution
from .multi_distribution import MultiSpectralDistribution
from .shape import SpectralShape

__all__ = [
    "SpectralShape",  # regular wavelength sampling shape
    "SpectralDistribution",  # single-channel spectral distribution
    "MultiSpectralDistribution",  # multi-channel spectral distribution
]

__all__ += [
    "from_columns",  # wrap raw column arrays as spectral objects
    "from_dataset",  # load a dataset and wrap it as a spectral object
]

__all__ += [
    "from_D65_illuminant",  # wrap CIE standard illuminant D65
    "from_cie1931_xyz_cmfs",  # wrap CIE 1931 XYZ CMFs
    "from_cie1964_xyz_cmfs",  # wrap CIE 1964 XYZ CMFs
    "from_cie2012_xyz_2degree_cmfs",  # wrap CIE 2012 2-degree XYZ CMFs
    "from_cie2012_xyz_10degree_cmfs",  # wrap CIE 2012 10-degree XYZ CMFs
    "from_cie2006_lms_2degree_fundamentals",  # wrap CIE 2006 2-degree LMS fundamentals
    "from_cie2006_lms_10degree_fundamentals",  # wrap CIE 2006 10-degree LMS fundamentals
    "from_iprgc_melanopic",  # wrap CIE S 026 melanopic / ipRGC action spectrum
    "from_alpha_opic_action_spectra",  # compose the five CIE S 026 alpha-opic action spectra
]

__all__ += [
    "from_stockman_rider_2023_individual_cone_fundamentals",  # wrap Stockman/Rider LMS fundamentals
    "from_asano2016_individual_cone_fundamentals",  # wrap Asano 2016 LMS fundamentals
]
