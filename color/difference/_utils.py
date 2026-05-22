"""Shared utilities for colour-difference calculations."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def as_triplet_array(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def broadcast_triplets(
    value_1: Sequence[float] | np.ndarray,
    value_2: Sequence[float] | np.ndarray,
    *,
    name_1: str,
    name_2: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and broadcast two generic triplet arrays."""
    arr_1 = as_triplet_array(value_1, name=name_1)
    arr_2 = as_triplet_array(value_2, name=name_2)
    try:
        return np.broadcast_arrays(arr_1, arr_2)
    except ValueError as exc:
        raise ValueError(
            f"{name_1} and {name_2} could not be broadcast together: "
            f"{arr_1.shape} and {arr_2.shape}"
        ) from exc


def as_float_result(value: np.ndarray) -> np.ndarray | np.float64:
    """Return NumPy scalar for scalar outputs, otherwise an array."""
    return np.asarray(value, dtype=np.float64)[()]


__all__ = [
    "as_triplet_array",
    "broadcast_triplets",
    "as_float_result",
]
