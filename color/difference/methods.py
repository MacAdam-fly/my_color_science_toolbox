"""Delta E method registry and dispatch."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any, Sequence

import numpy as np

from .appearance_delta_e import (
    delta_E_CAM02LCD,
    delta_E_CAM02SCD,
    delta_E_CAM02UCS,
    delta_E_CAM16LCD,
    delta_E_CAM16SCD,
    delta_E_CAM16UCS,
)
from .lab_delta_e import (
    delta_E_CIE1976,
    delta_E_CIE1994,
    delta_E_CIE2000,
    delta_E_CMC,
)
from .jzazbz_delta_e import delta_E_Jzazbz
from .oklab_delta_e import delta_E_Oklab


DeltaEFunction = Callable[..., Any]


def _canonical_method(name: str) -> str:
    """Return a normalized method key."""
    return "".join(character for character in name.casefold() if character.isalnum())


_METHOD_ALIASES = {
    "CIE 1976": ("cie1976",),
    "CIE 1994": ("cie1994",),
    "CIE 2000": ("cie2000", "CIEDE2000"),
    "CMC": (),
    "CAM02-UCS": ("CAM02UCS", "CAM02 UCS"),
    "CAM02-LCD": ("CAM02LCD", "CAM02 LCD"),
    "CAM02-SCD": ("CAM02SCD", "CAM02 SCD"),
    "CAM16-UCS": ("CAM16UCS", "CAM16 UCS"),
    "CAM16-LCD": ("CAM16LCD", "CAM16 LCD"),
    "CAM16-SCD": ("CAM16SCD", "CAM16 SCD"),
    "Oklab": ("OKLab", "OKLAB"),
    "Jzazbz": ("JzAzBz",),
}

_METHOD_FUNCTIONS: dict[str, DeltaEFunction] = {
    "CIE 1976": delta_E_CIE1976,
    "CIE 1994": delta_E_CIE1994,
    "CIE 2000": delta_E_CIE2000,
    "CMC": delta_E_CMC,
    "CAM02-UCS": delta_E_CAM02UCS,
    "CAM02-LCD": delta_E_CAM02LCD,
    "CAM02-SCD": delta_E_CAM02SCD,
    "CAM16-UCS": delta_E_CAM16UCS,
    "CAM16-LCD": delta_E_CAM16LCD,
    "CAM16-SCD": delta_E_CAM16SCD,
    "Oklab": delta_E_Oklab,
    "Jzazbz": delta_E_Jzazbz,
}

_METHOD_INDEX: dict[str, str] = {}
for _name, _aliases in _METHOD_ALIASES.items():
    for _alias in (_name, *_aliases):
        _METHOD_INDEX[_canonical_method(_alias)] = _name

DELTA_E_METHODS: Mapping[str, DeltaEFunction] = MappingProxyType(_METHOD_FUNCTIONS)


def _filter_kwargs(function: DeltaEFunction, kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Return kwargs accepted by *function*, matching colour's dispatch style."""
    signature = inspect.signature(function)
    return {key: value for key, value in kwargs.items() if key in signature.parameters}


def delta_E(
    a: Sequence[float] | np.ndarray,
    b: Sequence[float] | np.ndarray,
    method: str = "CIE 2000",
    **kwargs: Any,
) -> np.ndarray | np.float64:
    """Return Delta E between two arrays using a registered method."""
    key = _canonical_method(method)
    if key not in _METHOD_INDEX:
        available = ", ".join(DELTA_E_METHODS)
        raise ValueError(f"unknown delta E method {method!r}. Available: {available}")

    canonical_name = _METHOD_INDEX[key]
    function = DELTA_E_METHODS[canonical_name]
    return function(a, b, **_filter_kwargs(function, kwargs))


__all__ = [
    "DELTA_E_METHODS",
    "delta_E",
]
