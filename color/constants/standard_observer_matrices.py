"""Standard-observer LMS and XYZ conversion matrix constants.

These constants transform CIE 2006 standard-observer response values between
LMS and XYZ.
"""

from __future__ import annotations

import numpy as np


def _readonly_matrix(values: list[list[float]]) -> np.ndarray:
    matrix = np.array(values, dtype=np.float64)
    matrix.setflags(write=False)
    return matrix


def _readonly_inverse(matrix: np.ndarray) -> np.ndarray:
    inverse = np.linalg.inv(matrix)
    inverse.setflags(write=False)
    return inverse


LMS_2_DEGREE_TO_XYZ_2_DEGREE = _readonly_matrix(
    [
        [1.94735469, -1.41445123, 0.36476327],
        [0.68990272, 0.34832189, 0.00000000],
        [0.00000000, 0.00000000, 1.93485343],
    ]
)
XYZ_2_DEGREE_TO_LMS_2_DEGREE = _readonly_inverse(LMS_2_DEGREE_TO_XYZ_2_DEGREE)

LMS_10_DEGREE_TO_XYZ_10_DEGREE = _readonly_matrix(
    [
        [1.93986443, -1.34664359, 0.43044935],
        [0.69283932, 0.34967567, 0.00000000],
        [0.00000000, 0.00000000, 2.14687945],
    ]
)
XYZ_10_DEGREE_TO_LMS_10_DEGREE = _readonly_inverse(LMS_10_DEGREE_TO_XYZ_10_DEGREE)


__all__ = [
    "LMS_2_DEGREE_TO_XYZ_2_DEGREE",
    "XYZ_2_DEGREE_TO_LMS_2_DEGREE",
    "LMS_10_DEGREE_TO_XYZ_10_DEGREE",
    "XYZ_10_DEGREE_TO_LMS_10_DEGREE",
]
