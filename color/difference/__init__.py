"""Colour difference metrics."""

from __future__ import annotations

from .appearance_delta_e import (
    delta_E_CAM02LCD,
    delta_E_CAM02SCD,
    delta_E_CAM02UCS,
    delta_E_CAM16LCD,
    delta_E_CAM16SCD,
    delta_E_CAM16UCS,
)
from .lab_delta_e import (
    JND_CIE1976,
    delta_E_CIE1976,
    delta_E_CIE1994,
    delta_E_CIE2000,
    delta_E_CMC,
)
from .jzazbz_delta_e import delta_E_Jzazbz
from .methods import delta_E
from .oklab_delta_e import delta_E_Oklab

__all__ = [
    "JND_CIE1976",  # approximate CIE 1976 just noticeable difference
    "delta_E_CIE1976",  # compute CIE 1976 Lab colour difference
    "delta_E_CIE1994",  # compute CIE 1994 Lab colour difference
    "delta_E_CIE2000",  # compute CIEDE2000 Lab colour difference
    "delta_E_CMC",  # compute CMC l:c Lab colour difference
]

__all__ += [
    "delta_E_CAM02UCS",  # compute CAM02-UCS colour difference
    "delta_E_CAM02LCD",  # compute CAM02-LCD colour difference
    "delta_E_CAM02SCD",  # compute CAM02-SCD colour difference
    "delta_E_CAM16UCS",  # compute CAM16-UCS colour difference
    "delta_E_CAM16LCD",  # compute CAM16-LCD colour difference
    "delta_E_CAM16SCD",  # compute CAM16-SCD colour difference
]

__all__ += [
    "delta_E_Oklab",  # compute Oklab coordinate distance
    "delta_E_Jzazbz",  # compute Jzazbz coordinate distance
]

__all__ += [
    "delta_E",  # dispatch to a registered delta E method
]
