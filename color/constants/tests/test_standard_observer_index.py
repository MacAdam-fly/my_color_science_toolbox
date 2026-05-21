from __future__ import annotations

from color import constants
from color.colorimetry import standard_observer_matrices as colorimetry_matrices
from color.constants import standard_observer_matrices


def test_standard_observer_matrices_are_available_from_constants_top_level() -> None:
    assert (
        constants.LMS_2_DEGREE_TO_XYZ_2_DEGREE
        is standard_observer_matrices.LMS_2_DEGREE_TO_XYZ_2_DEGREE
    )
    assert (
        constants.XYZ_2_DEGREE_TO_LMS_2_DEGREE
        is standard_observer_matrices.XYZ_2_DEGREE_TO_LMS_2_DEGREE
    )
    assert (
        constants.LMS_10_DEGREE_TO_XYZ_10_DEGREE
        is standard_observer_matrices.LMS_10_DEGREE_TO_XYZ_10_DEGREE
    )
    assert (
        constants.XYZ_10_DEGREE_TO_LMS_10_DEGREE
        is standard_observer_matrices.XYZ_10_DEGREE_TO_LMS_10_DEGREE
    )


def test_colorimetry_module_reexports_constants_objects() -> None:
    assert (
        colorimetry_matrices.LMS_2_DEGREE_TO_XYZ_2_DEGREE
        is standard_observer_matrices.LMS_2_DEGREE_TO_XYZ_2_DEGREE
    )
    assert (
        colorimetry_matrices.XYZ_2_DEGREE_TO_LMS_2_DEGREE
        is standard_observer_matrices.XYZ_2_DEGREE_TO_LMS_2_DEGREE
    )
    assert (
        colorimetry_matrices.LMS_10_DEGREE_TO_XYZ_10_DEGREE
        is standard_observer_matrices.LMS_10_DEGREE_TO_XYZ_10_DEGREE
    )
    assert (
        colorimetry_matrices.XYZ_10_DEGREE_TO_LMS_10_DEGREE
        is standard_observer_matrices.XYZ_10_DEGREE_TO_LMS_10_DEGREE
    )
