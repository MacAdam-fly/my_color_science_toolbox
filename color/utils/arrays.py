"""Shared NumPy array helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def as_float_array(
    value: Sequence[float] | np.ndarray,
    *,
    name: str = "value",
    finite: bool = True,
) -> np.ndarray:
    """Return *value* as a floating NumPy array."""
    arr = np.asarray(value, dtype=np.float64)
    if finite and not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def as_float_result(value: np.ndarray) -> np.ndarray | np.float64:
    """Return NumPy scalar for scalar outputs, otherwise an array."""
    return np.asarray(value, dtype=np.float64)[()]


def as_last_axis(
    value: Sequence[float] | np.ndarray,
    size: int,
    *,
    name: str = "value",
    finite: bool = True,
) -> np.ndarray:
    """Return *value* as a finite array with *size* values on the last axis."""
    arr = as_float_array(value, name=name, finite=finite)
    if arr.shape == () or arr.shape[-1] != size:
        raise ValueError(f"{name} must have {size} values on the last axis")
    return arr


def as_last_axis_triplets(
    value: Sequence[float] | np.ndarray,
    *,
    name: str = "value",
    finite: bool = True,
) -> np.ndarray:
    """Return *value* as an array with three values on the last axis."""
    return as_last_axis(value, 3, name=name, finite=finite)


def as_last_axis_pairs(
    value: Sequence[float] | np.ndarray,
    *,
    name: str = "value",
    finite: bool = True,
) -> np.ndarray:
    """Return *value* as an array with two values on the last axis."""
    return as_last_axis(value, 2, name=name, finite=finite)


def broadcast_last_axis(
    value_1: Sequence[float] | np.ndarray,
    value_2: Sequence[float] | np.ndarray,
    size: int,
    *,
    name_1: str = "value_1",
    name_2: str = "value_2",
    finite: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and broadcast two arrays with *size* values on the last axis."""
    arr_1 = as_last_axis(value_1, size, name=name_1, finite=finite)
    arr_2 = as_last_axis(value_2, size, name=name_2, finite=finite)
    try:
        return np.broadcast_arrays(arr_1, arr_2)
    except ValueError as exc:
        raise ValueError(
            f"{name_1} and {name_2} could not be broadcast together: "
            f"{arr_1.shape} and {arr_2.shape}"
        ) from exc


def broadcast_triplets(
    value_1: Sequence[float] | np.ndarray,
    value_2: Sequence[float] | np.ndarray,
    *,
    name_1: str = "value_1",
    name_2: str = "value_2",
    finite: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and broadcast two triplet arrays."""
    return broadcast_last_axis(
        value_1,
        value_2,
        3,
        name_1=name_1,
        name_2=name_2,
        finite=finite,
    )


def broadcast_pairs(
    value_1: Sequence[float] | np.ndarray,
    value_2: Sequence[float] | np.ndarray,
    *,
    name_1: str = "value_1",
    name_2: str = "value_2",
    finite: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and broadcast two pair arrays."""
    return broadcast_last_axis(
        value_1,
        value_2,
        2,
        name_1=name_1,
        name_2=name_2,
        finite=finite,
    )


def split_last_axis(value: Sequence[float] | np.ndarray) -> tuple[np.ndarray, ...]:
    """Split an array into a tuple of arrays along the last axis."""
    arr = np.asarray(value)
    if arr.shape == ():
        raise ValueError("value must have at least one axis")
    return tuple(arr[..., index] for index in range(arr.shape[-1]))


__all__ = [
    "as_float_array",
    "as_float_result",
    "as_last_axis",
    "as_last_axis_triplets",
    "as_last_axis_pairs",
    "broadcast_last_axis",
    "broadcast_triplets",
    "broadcast_pairs",
    "split_last_axis",
]
