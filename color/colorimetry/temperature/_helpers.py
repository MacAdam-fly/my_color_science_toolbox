"""Shared helpers for correlated colour temperature modules."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def as_finite_array(
    value: float | Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Return *value* as a finite float array."""
    arr = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def as_last_axis_pairs(
    value: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Return *value* as a finite float array with two values on the last axis."""
    arr = as_finite_array(value, name=name)
    if arr.shape == () or arr.shape[-1] != 2:
        raise ValueError(f"{name} must have 2 values on the last axis")
    return arr


def scalar_or_array(value: np.ndarray) -> float | np.ndarray:
    """Return a Python float for scalar arrays, otherwise the array itself."""
    if value.shape == ():
        return float(value)
    return value


def normalize_method(method: str) -> str:
    """Return a compact method key."""
    return method.lower().replace(" ", "").replace("_", "").replace("-", "")
