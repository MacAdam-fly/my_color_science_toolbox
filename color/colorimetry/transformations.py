"""Direct LMS and XYZ transformations for CIE 2006 standard observers."""

from __future__ import annotations

from typing import Literal, Sequence

import numpy as np

from color.constants.standard_observer_matrices import (
    LMS_2_DEGREE_TO_XYZ_2_DEGREE,
    LMS_10_DEGREE_TO_XYZ_10_DEGREE,
    XYZ_2_DEGREE_TO_LMS_2_DEGREE,
    XYZ_10_DEGREE_TO_LMS_10_DEGREE,
)


Observer = Literal[2, 10]


def _as_last_axis_triplets(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a float array with three values on the last axis."""
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape == () or arr.shape[-1] != 3:
        raise ValueError(f"{name} must have 3 values on the last axis")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def _matrix_for_observer(observer: Observer, *, inverse: bool) -> np.ndarray:
    """Return the requested CIE 2006 observer transformation matrix."""
    if observer == 2:
        return XYZ_2_DEGREE_TO_LMS_2_DEGREE if inverse else LMS_2_DEGREE_TO_XYZ_2_DEGREE
    if observer == 10:
        return XYZ_10_DEGREE_TO_LMS_10_DEGREE if inverse else LMS_10_DEGREE_TO_XYZ_10_DEGREE
    raise ValueError("observer must be 2 or 10")


def LMS_to_XYZ(
    LMS: Sequence[float] | np.ndarray,
    *,
    observer: Observer = 2,
) -> np.ndarray:
    """Convert LMS values to XYZ values for a CIE 2006 standard observer."""
    lms = _as_last_axis_triplets(LMS, name="LMS")
    matrix = _matrix_for_observer(observer, inverse=False)
    return lms @ matrix.T


def XYZ_to_LMS(
    XYZ: Sequence[float] | np.ndarray,
    *,
    observer: Observer = 2,
) -> np.ndarray:
    """Convert XYZ values to LMS values for a CIE 2006 standard observer."""
    xyz = _as_last_axis_triplets(XYZ, name="XYZ")
    matrix = _matrix_for_observer(observer, inverse=True)
    return xyz @ matrix.T


__all__ = [
    "LMS_to_XYZ",
    "XYZ_to_LMS",
]
