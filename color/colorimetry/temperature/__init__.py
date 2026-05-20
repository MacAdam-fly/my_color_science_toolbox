"""Correlated colour temperature helpers."""

from __future__ import annotations

from .analysis import TemperatureAnalysis, analyze_temperature
from .conversions import (
    CCT_to_mired,
    XYZ_to_uv1960,
    mired_to_CCT,
    uv1960_to_xy,
    xy_to_uv1960,
)
from .daylight import CCT_to_xy, CCT_to_xy_CIE_D
from .dispatch import CCT_Duv_to_xy, CCT_to_uv, uv_to_CCT, xy_to_CCT_Duv
from .mccamy1992 import xy_to_CCT, xy_to_CCT_McCamy1992
from .ohno2013 import (
    CCT_DEFAULT_SPACING_OHNO2013,
    CCT_MAXIMAL_OHNO2013,
    CCT_MINIMAL_OHNO2013,
    CCT_to_uv_Ohno2013,
    DEFAULT_CMFS_OHNO2013,
    planckian_table_Ohno2013,
    uv_to_CCT_Ohno2013,
)
from .robertson1968 import CCT_to_uv_Robertson1968, uv_to_CCT_Robertson1968

# Basic CCT unit conversions.
__all__ = [
    "CCT_to_mired",  # convert CCT in kelvins to mired
    "mired_to_CCT",  # convert mired to CCT in kelvins
]

# High-level temperature analysis.
__all__ += [
    "TemperatureAnalysis",  # result object for full CCT and Duv analysis
    "analyze_temperature",  # full CCT and Duv analysis from xy coordinates
]

# CIE xy, CIE 1960 UCS uv and CCT conversions.
__all__ += [
    "xy_to_CCT_McCamy1992",  # estimate CCT from xy using McCamy 1992
    "CCT_to_xy_CIE_D",  # compute CIE D-series daylight xy from CCT
    "xy_to_CCT",  # estimate CCT from xy using a named method
    "CCT_to_xy",  # compute xy from CCT using a named method
    "xy_to_uv1960",  # convert xy chromaticity coordinates to CIE 1960 uv
    "XYZ_to_uv1960",  # convert XYZ tristimulus values to CIE 1960 uv
    "uv1960_to_xy",  # convert CIE 1960 uv coordinates to xy
]

# Robertson 1968 CCT + Duv.
__all__ += [
    "uv_to_CCT_Robertson1968",  # compute CCT and Duv from uv using Robertson 1968
    "CCT_to_uv_Robertson1968",  # compute uv from CCT and Duv using Robertson 1968
]

# Ohno 2013 CCT + Duv.
__all__ += [
    "CCT_MINIMAL_OHNO2013",  # default lower CCT bound for Ohno 2013 tables
    "CCT_MAXIMAL_OHNO2013",  # default upper CCT bound for Ohno 2013 tables
    "CCT_DEFAULT_SPACING_OHNO2013",  # default multiplicative table spacing for Ohno 2013
    "DEFAULT_CMFS_OHNO2013",  # default CMFS dataset for Ohno 2013 computations
    "planckian_table_Ohno2013",  # generate the Planckian uv table used by Ohno 2013
    "uv_to_CCT_Ohno2013",  # compute CCT and Duv from uv using Ohno 2013
    "CCT_to_uv_Ohno2013",  # compute uv from CCT and Duv using Ohno 2013
]

# Named CCT + Duv dispatchers.
__all__ += [
    "uv_to_CCT",  # compute CCT and Duv from uv using a named method
    "CCT_to_uv",  # compute uv from CCT and Duv using a named method
    "xy_to_CCT_Duv",  # compute CCT and Duv from xy using a named method
    "CCT_Duv_to_xy",  # compute xy from CCT and Duv using a named method
]
