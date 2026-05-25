"""Explicit numeric scale conversion helpers."""

from __future__ import annotations

from typing import Literal, Sequence

import numpy as np

from .arrays import as_float_array, as_float_result
from .names import canonical_method_name

Scale = Literal["reference", "1", "100"]
AngleScale = Literal["reference", "1", "100", "degrees"]

_SCALE_ALIASES = {
    "reference": "reference",
    "ref": "reference",
    "1": "1",
    "unit": "1",
    "normalised": "1",
    "normalized": "1",
    "01": "1",
    "0to1": "1",
    "100": "100",
    "percent": "100",
    "percentage": "100",
    "0to100": "100",
}

_ANGLE_SCALE_ALIASES = {
    **_SCALE_ALIASES,
    "degree": "degrees",
    "degrees": "degrees",
    "deg": "degrees",
}


def _canonical_scale(scale: str, *, allow_degrees: bool = False) -> str:
    """Return the canonical scale name."""
    aliases = _ANGLE_SCALE_ALIASES if allow_degrees else _SCALE_ALIASES
    key = canonical_method_name(scale)
    if key not in aliases:
        names = ", ".join(sorted(set(aliases.values())))
        raise ValueError(f"scale must be one of: {names}")
    return aliases[key]


def _copy_float(value, *, name: str) -> np.ndarray:
    """Return *value* as a finite float array copy."""
    return as_float_array(value, name=name).copy()


def _scale_result(value, multiplier) -> np.ndarray | np.float64:
    """Return *value* multiplied by *multiplier* with scalar shape preserved."""
    return as_float_result(value * as_float_array(multiplier, name="scale_factor"))


def to_domain_1(
    value: float | Sequence[float] | np.ndarray,
    *,
    source_scale: Scale | str = "100",
    scale_factor: float | Sequence[float] | np.ndarray = 100.0,
    name: str = "value",
) -> np.ndarray | np.float64:
    """Convert values from *source_scale* to the numeric ``[0, 1]`` domain."""
    arr = _copy_float(value, name=name)
    source = _canonical_scale(source_scale)
    if source == "100":
        return _scale_result(arr, 1.0 / as_float_array(scale_factor, name="scale_factor"))
    return as_float_result(arr)


def to_domain_100(
    value: float | Sequence[float] | np.ndarray,
    *,
    source_scale: Scale | str = "1",
    scale_factor: float | Sequence[float] | np.ndarray = 100.0,
    name: str = "value",
) -> np.ndarray | np.float64:
    """Convert values from *source_scale* to the numeric ``[0, 100]`` domain."""
    arr = _copy_float(value, name=name)
    source = _canonical_scale(source_scale)
    if source == "1":
        return _scale_result(arr, scale_factor)
    return as_float_result(arr)


def from_range_1(
    value: float | Sequence[float] | np.ndarray,
    *,
    target_scale: Scale | str = "100",
    scale_factor: float | Sequence[float] | np.ndarray = 100.0,
    name: str = "value",
) -> np.ndarray | np.float64:
    """Convert values from the numeric ``[0, 1]`` range to *target_scale*."""
    arr = _copy_float(value, name=name)
    target = _canonical_scale(target_scale)
    if target == "100":
        return _scale_result(arr, scale_factor)
    return as_float_result(arr)


def from_range_100(
    value: float | Sequence[float] | np.ndarray,
    *,
    target_scale: Scale | str = "1",
    scale_factor: float | Sequence[float] | np.ndarray = 100.0,
    name: str = "value",
) -> np.ndarray | np.float64:
    """Convert values from the numeric ``[0, 100]`` range to *target_scale*."""
    arr = _copy_float(value, name=name)
    target = _canonical_scale(target_scale)
    if target == "1":
        return _scale_result(arr, 1.0 / as_float_array(scale_factor, name="scale_factor"))
    return as_float_result(arr)


def to_domain_degrees(
    value: float | Sequence[float] | np.ndarray,
    *,
    source_scale: AngleScale | str = "1",
    scale_factor: float | Sequence[float] | np.ndarray = 360.0,
    name: str = "value",
) -> np.ndarray | np.float64:
    """Convert values from *source_scale* to degrees."""
    arr = _copy_float(value, name=name)
    source = _canonical_scale(source_scale, allow_degrees=True)
    if source == "1":
        return _scale_result(arr, scale_factor)
    if source == "100":
        return _scale_result(arr, as_float_array(scale_factor, name="scale_factor") / 100.0)
    return as_float_result(arr)


def from_range_degrees(
    value: float | Sequence[float] | np.ndarray,
    *,
    target_scale: AngleScale | str = "1",
    scale_factor: float | Sequence[float] | np.ndarray = 360.0,
    name: str = "value",
) -> np.ndarray | np.float64:
    """Convert values from degrees to *target_scale*."""
    arr = _copy_float(value, name=name)
    target = _canonical_scale(target_scale, allow_degrees=True)
    factor = as_float_array(scale_factor, name="scale_factor")
    if target == "1":
        return _scale_result(arr, 1.0 / factor)
    if target == "100":
        return _scale_result(arr, 100.0 / factor)
    return as_float_result(arr)


__all__ = [
    "Scale",
    "AngleScale",
    "to_domain_1",
    "to_domain_100",
    "from_range_1",
    "from_range_100",
    "to_domain_degrees",
    "from_range_degrees",
]
