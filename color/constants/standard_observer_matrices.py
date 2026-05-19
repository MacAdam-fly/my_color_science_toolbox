"""Standard-observer LMS and XYZ conversion matrices."""

from __future__ import annotations

import numpy as np


LMS_2_DEGREE_TO_XYZ_2_DEGREE = np.array(
    [
        [1.94735469, -1.41445123, 0.36476327],
        [0.68990272, 0.34832189, 0.00000000],
        [0.00000000, 0.00000000, 1.93485343],
    ],
    dtype=float,
)
XYZ_2_DEGREE_TO_LMS_2_DEGREE = np.linalg.inv(LMS_2_DEGREE_TO_XYZ_2_DEGREE)

LMS_10_DEGREE_TO_XYZ_10_DEGREE = np.array(
    [
        [1.93986443, -1.34664359, 0.43044935],
        [0.69283932, 0.34967567, 0.00000000],
        [0.00000000, 0.00000000, 2.14687945],
    ],
    dtype=float,
)
XYZ_10_DEGREE_TO_LMS_10_DEGREE = np.linalg.inv(LMS_10_DEGREE_TO_XYZ_10_DEGREE)


__all__ = [
    "LMS_2_DEGREE_TO_XYZ_2_DEGREE",
    "XYZ_2_DEGREE_TO_LMS_2_DEGREE",
    "LMS_10_DEGREE_TO_XYZ_10_DEGREE",
    "XYZ_10_DEGREE_TO_LMS_10_DEGREE",
]
