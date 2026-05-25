"""Shared helpers for correlated colour temperature modules."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_float_array as _as_float_array
from color.utils.arrays import as_last_axis_pairs as _as_last_axis_pairs
from color.utils.names import canonical_method_name


def as_finite_array(
    value: float | Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Return *value* as a finite float array."""
    return _as_float_array(value, name=name)


def as_last_axis_pairs(
    value: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Return *value* as a finite float array with two values on the last axis."""
    return _as_last_axis_pairs(value, name=name)


def scalar_or_array(value: np.ndarray) -> float | np.ndarray:
    """Return a Python float for scalar arrays, otherwise the array itself."""
    if value.shape == ():
        return float(value)
    return value


def normalize_method(method: str) -> str:
    """Return a compact method key."""
    return canonical_method_name(method)
