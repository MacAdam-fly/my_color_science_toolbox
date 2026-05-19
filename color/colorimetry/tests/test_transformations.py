"""Tests for direct LMS and XYZ transformations."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import LMS_to_XYZ, XYZ_to_LMS
from color.constants.standard_observer_matrices import (
    LMS_2_DEGREE_TO_XYZ_2_DEGREE,
    LMS_10_DEGREE_TO_XYZ_10_DEGREE,
)


def test_LMS_to_XYZ_2_degree_matches_matrix():
    LMS = np.array([0.2, 0.3, 0.4])

    XYZ = LMS_to_XYZ(LMS)

    np.testing.assert_allclose(XYZ, LMS_2_DEGREE_TO_XYZ_2_DEGREE @ LMS)


def test_LMS_to_XYZ_10_degree_matches_matrix():
    LMS = np.array([0.2, 0.3, 0.4])

    XYZ = LMS_to_XYZ(LMS, observer=10)

    np.testing.assert_allclose(XYZ, LMS_10_DEGREE_TO_XYZ_10_DEGREE @ LMS)


def test_XYZ_to_LMS_round_trip_array():
    XYZ = np.array([
        [0.5, 0.6, 0.7],
        [1.0, 0.8, 0.2],
    ])

    result = LMS_to_XYZ(XYZ_to_LMS(XYZ))

    np.testing.assert_allclose(result, XYZ)


def test_XYZ_to_LMS_round_trip_image_like_array():
    XYZ = np.array([
        [
            [0.5, 0.6, 0.7],
            [1.0, 0.8, 0.2],
        ],
        [
            [95.047, 100.0, 108.883],
            [41.24, 21.26, 1.93],
        ],
    ])

    LMS = XYZ_to_LMS(XYZ, observer=10)
    result = LMS_to_XYZ(LMS, observer=10)

    assert LMS.shape == XYZ.shape
    np.testing.assert_allclose(result, XYZ)


def test_rejects_invalid_triplet_shape():
    with pytest.raises(ValueError, match="3 values"):
        LMS_to_XYZ([1.0, 2.0])


def test_rejects_invalid_observer():
    with pytest.raises(ValueError, match="observer"):
        XYZ_to_LMS([1.0, 2.0, 3.0], observer=5)  # type: ignore[arg-type]
