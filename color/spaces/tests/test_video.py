"""Tests for explicit video signal encoding helpers."""

from __future__ import annotations

import numpy as np
import pytest

import color.spaces as spaces
import color.spaces.video as video
from color.spaces import (
    convert_color,
    get_colourspace_node,
    list_colourspace_nodes,
)
from color.spaces.video import (
    ICtCp_to_RGB_BT2020,
    RGB_BT2020_to_ICtCp,
    RGB_to_YCbCr,
    YCbCr_to_RGB,
    code_value_range,
    eotf_ST2084,
    eotf_inverse_ST2084,
    matrix_YCbCr,
    offset_YCbCr,
    oetf_ARIBSTDB67,
    oetf_inverse_ARIBSTDB67,
    ranges_YCbCr,
)


def test_ST2084_transfer_functions_match_reference_values():
    np.testing.assert_allclose(
        eotf_ST2084([0.0, 0.25, 0.5, 0.75, 1.0]),
        [
            0.0,
            5.154176009833007,
            92.24570899406527,
            983.3778555870275,
            10000.0,
        ],
        atol=1e-10,
    )
    np.testing.assert_allclose(
        eotf_inverse_ST2084([0.0, 100.0, 1000.0, 4000.0, 10000.0]),
        [
            7.309559025783966e-07,
            0.508078421517399,
            0.751827096247041,
            0.9025723933109373,
            1.0,
        ],
        atol=1e-12,
    )
    np.testing.assert_allclose(
        eotf_inverse_ST2084([0.0, 100.0, 1000.0], L_p=1000),
        [7.309559025783966e-07, 0.751827096247041, 1.0],
        atol=1e-12,
    )


def test_HLG_transfer_functions_match_reference_values():
    scene = np.array([0.0, 0.25, 1.0, 3.0, 12.0])
    signal = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

    np.testing.assert_allclose(
        oetf_ARIBSTDB67(scene),
        [
            0.0,
            0.25,
            0.5,
            0.7385492680658274,
            0.9999999955365686,
        ],
        atol=1e-12,
    )
    np.testing.assert_allclose(
        oetf_inverse_ARIBSTDB67(signal),
        [0.0, 0.25, 1.0, 3.179550717436802, 12.000000292399305],
        atol=1e-12,
    )
    np.testing.assert_allclose(oetf_inverse_ARIBSTDB67(oetf_ARIBSTDB67(scene)), scene, atol=5e-7)


def test_transfer_functions_reject_invalid_domain_values():
    for function in (
        eotf_ST2084,
        eotf_inverse_ST2084,
        oetf_ARIBSTDB67,
        oetf_inverse_ARIBSTDB67,
    ):
        with pytest.raises(ValueError, match="non-negative"):
            function([-1.0])
        with pytest.raises(ValueError, match="finite"):
            function([np.nan])

    with pytest.raises(ValueError, match="L_p"):
        eotf_ST2084([0.5], L_p=0)
    with pytest.raises(ValueError, match="L_p"):
        eotf_inverse_ST2084([100.0], L_p=0)
    with pytest.raises(ValueError, match="r"):
        oetf_ARIBSTDB67([0.5], r=0)
    with pytest.raises(ValueError, match="r"):
        oetf_inverse_ARIBSTDB67([0.5], r=0)


def test_ICtCp_matches_reference_values():
    RGB = np.array([0.45620519, 0.03081071, 0.04091952])
    ICtCp = RGB_BT2020_to_ICtCp(RGB)

    np.testing.assert_allclose(
        ICtCp,
        [0.073513639962436, 0.004752526733527, 0.093515955305992],
        atol=1e-14,
    )
    np.testing.assert_allclose(ICtCp_to_RGB_BT2020(ICtCp), RGB, atol=1e-12)


def test_ICtCp_preserves_batch_shape_and_rejects_invalid_inputs():
    RGB = np.array(
        [
            [0.45620519, 0.03081071, 0.04091952],
            [1.0, 1.0, 1.0],
        ]
    )

    ICtCp = RGB_BT2020_to_ICtCp(RGB)

    assert ICtCp.shape == RGB.shape
    np.testing.assert_allclose(ICtCp_to_RGB_BT2020(ICtCp), RGB, atol=2e-11)

    with pytest.raises(ValueError, match="3 values on the last axis"):
        RGB_BT2020_to_ICtCp([1.0, 2.0])
    with pytest.raises(ValueError, match="finite"):
        RGB_BT2020_to_ICtCp([1.0, np.nan, 0.0])
    with pytest.raises(ValueError, match="L_p"):
        RGB_BT2020_to_ICtCp([1.0, 1.0, 1.0], L_p=0)


def test_YCbCr_matches_reference_values_and_round_trips():
    RGB = np.array([0.25, 0.5, 0.75])
    YCbCr = RGB_to_YCbCr(RGB)

    np.testing.assert_allclose(
        RGB_to_YCbCr([1.0, 1.0, 1.0]),
        [0.92156862745098, 0.501960784313725, 0.501960784313725],
        atol=1e-15,
    )
    np.testing.assert_allclose(
        YCbCr,
        [0.462012156862745, 0.636925638977298, 0.382088481824022],
        atol=1e-15,
    )
    np.testing.assert_allclose(YCbCr_to_RGB(YCbCr), RGB, atol=1e-14)


def test_YCbCr_full_range_and_integer_modes_match_reference_values():
    np.testing.assert_allclose(
        RGB_to_YCbCr([0.25, 0.5, 0.75], out_legal=False),
        [0.4649, 0.153643026514335, -0.136461772923546],
        atol=1e-15,
    )
    np.testing.assert_array_equal(
        RGB_to_YCbCr(
            np.array([102, 0, 51]),
            standard="BT.601",
            in_bits=8,
            in_int=True,
            out_legal=False,
            out_int=True,
        ),
        [36, 136, 175],
    )
    np.testing.assert_array_equal(
        RGB_to_YCbCr(
            [1023, 1023, 1023],
            in_bits=10,
            in_int=True,
            out_bits=10,
            out_legal=True,
            out_int=True,
        ),
        [940, 512, 512],
    )
    np.testing.assert_allclose(
        YCbCr_to_RGB([502, 512, 512], in_bits=10, in_legal=True, in_int=True),
        [0.5, 0.5, 0.5],
        atol=1e-3,
    )


def test_YCbCr_helpers_match_expected_ranges_and_matrix():
    np.testing.assert_allclose(code_value_range(10, True, True), [64.0, 940.0])
    np.testing.assert_allclose(ranges_YCbCr(10, True, True), [64.0, 940.0, 64.0, 960.0])
    np.testing.assert_allclose(offset_YCbCr(10, True, True), [64.0, 512.0, 512.0])
    np.testing.assert_allclose(
        matrix_YCbCr(bits=10, is_legal=True, is_int=True),
        [
            [1.1415525114155253e-03, 0.0, 1.7575892857142855e-03],
            [1.1415525114155255e-03, -2.0906726889581342e-04, -5.224601260386707e-04],
            [1.1415525114155255e-03, 2.070982142857143e-03, 0.0],
        ],
        atol=1e-18,
    )


def test_YCbCr_batch_custom_weights_and_invalid_inputs():
    RGB = np.array(
        [
            [0.25, 0.5, 0.75],
            [1.0, 1.0, 1.0],
        ]
    )

    YCbCr = RGB_to_YCbCr(RGB, standard=[0.2126, 0.0722])

    assert YCbCr.shape == RGB.shape
    np.testing.assert_allclose(YCbCr_to_RGB(YCbCr, standard="BT.709"), RGB, atol=1e-14)

    with pytest.raises(ValueError, match="unknown YCbCr standard"):
        RGB_to_YCbCr([0.0, 0.0, 0.0], standard="unknown")
    with pytest.raises(ValueError, match="weights"):
        RGB_to_YCbCr([0.0, 0.0, 0.0], standard=[0.7, 0.4])
    with pytest.raises(ValueError, match="3 values on the last axis"):
        YCbCr_to_RGB([0.0, 0.0])


def test_video_helpers_are_not_registered_generic_colour_spaces():
    names = list_colourspace_nodes()

    assert not hasattr(spaces, "RGB_BT2020_to_ICtCp")
    assert not hasattr(spaces, "RGB_to_YCbCr")
    assert not hasattr(spaces, "eotf_ST2084")
    assert "MATRIX_ICTCP_RGB_TO_LMS" not in video.__all__
    assert "ST2084_M1" not in video.__all__
    assert not hasattr(video, "MATRIX_ICTCP_RGB_TO_LMS")
    assert "ICtCp" not in names
    assert "YCbCr" not in names
    with pytest.raises(ValueError, match="unknown colour-space node"):
        get_colourspace_node("ICtCp")
    with pytest.raises(ValueError, match="unknown colour-space node"):
        get_colourspace_node("YCbCr")
    with pytest.raises(ValueError, match="unknown colour-space node"):
        convert_color([0.1, 0.2, 0.3], "ICtCp", "XYZ")
