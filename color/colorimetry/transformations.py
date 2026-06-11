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
from color.utils.arrays import as_last_axis_triplets


Observer = Literal[2, 10]


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
    """Convert CIE 2006 LMS values to XYZ with a fixed observer matrix.

    Parameters
    ----------
    LMS
        LMS values with final-axis shape ``(..., 3)``.
    observer
        CIE 2006 observer field size, either ``2`` or ``10`` degrees.

    Returns
    -------
    ndarray
        XYZ values with the same leading shape as ``LMS``.

    Notes
    -----
    This is a direct matrix transform between already-computed responses and
    XYZ. It is not a spectral integration and does not choose illuminants or
    colour matching functions.

    Examples
    --------
    >>> LMS_to_XYZ([1.0, 1.0, 1.0]).shape
    (3,)
    """
    lms = as_last_axis_triplets(LMS, name="LMS")
    matrix = _matrix_for_observer(observer, inverse=False)
    return lms @ matrix.T


def XYZ_to_LMS(
    XYZ: Sequence[float] | np.ndarray,
    *,
    observer: Observer = 2,
) -> np.ndarray:
    """Convert XYZ values to CIE 2006 LMS with a fixed observer matrix.

    Parameters
    ----------
    XYZ
        XYZ values with final-axis shape ``(..., 3)``.
    observer
        CIE 2006 observer field size, either ``2`` or ``10`` degrees.

    Returns
    -------
    ndarray
        LMS values with the same leading shape as ``XYZ``.

    Notes
    -----
    This is a direct matrix transform, not the same operation as
    ``emission_to_LMS`` or ``reflectance_to_LMS``.

    Examples
    --------
    >>> XYZ_to_LMS([95.047, 100.0, 108.883]).shape
    (3,)
    """
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    matrix = _matrix_for_observer(observer, inverse=True)
    return xyz @ matrix.T


__all__ = [
    "LMS_to_XYZ",
    "XYZ_to_LMS",
]
