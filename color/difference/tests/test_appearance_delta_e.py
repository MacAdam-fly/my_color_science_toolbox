"""Tests for appearance-uniform colour-difference formulas."""

from __future__ import annotations

import numpy as np
import pytest

from color.difference import (
    delta_E_CAM02LCD,
    delta_E_CAM02SCD,
    delta_E_CAM02UCS,
    delta_E_CAM16LCD,
    delta_E_CAM16SCD,
    delta_E_CAM16UCS,
)
from color.spaces import convert_color

colour = pytest.importorskip("colour")


JPAPBP_1 = np.array([54.90433134, -0.08450395, -0.06854831], dtype=np.float64)
JPAPBP_2 = np.array([54.80352754, -3.96940084, -13.57591013], dtype=np.float64)
JPAPBP_BATCH_1 = np.array(
    [
        [54.90433134, -0.08450395, -0.06854831],
        [62.12848174, 8.12165042, 22.44110157],
        [38.44219611, -18.90221743, 9.50210491],
    ],
    dtype=np.float64,
)
JPAPBP_BATCH_2 = np.array(
    [
        [54.80352754, -3.96940084, -13.57591013],
        [60.02111984, 4.25010411, 18.10888174],
        [42.11987112, -14.44887752, 11.24566250],
    ],
    dtype=np.float64,
)
SRGB_1 = np.array(
    [
        [0.72, 0.12, 0.10],
        [0.12, 0.54, 0.18],
        [0.14, 0.24, 0.82],
    ],
    dtype=np.float64,
)
SRGB_2 = np.array(
    [
        [0.75, 0.15, 0.12],
        [0.10, 0.50, 0.22],
        [0.18, 0.28, 0.78],
    ],
    dtype=np.float64,
)


def assert_matches_colour(function, reference, *args):
    result = function(*args)
    expected = reference(*args)
    np.testing.assert_allclose(result, expected, rtol=1e-10, atol=1e-10)


@pytest.mark.parametrize(
    ("function", "reference"),
    [
        (delta_E_CAM02UCS, colour.difference.delta_E_CAM02UCS),
        (delta_E_CAM02LCD, colour.difference.delta_E_CAM02LCD),
        (delta_E_CAM02SCD, colour.difference.delta_E_CAM02SCD),
        (delta_E_CAM16UCS, colour.difference.delta_E_CAM16UCS),
        (delta_E_CAM16LCD, colour.difference.delta_E_CAM16LCD),
        (delta_E_CAM16SCD, colour.difference.delta_E_CAM16SCD),
    ],
)
def test_delta_e_cam_uniform_spaces_match_colour(function, reference):
    assert_matches_colour(function, reference, JPAPBP_BATCH_1, JPAPBP_BATCH_2)


def test_single_point_returns_scalar():
    assert np.isscalar(delta_E_CAM02UCS(JPAPBP_1, JPAPBP_2))


def test_batch_and_broadcast_shapes():
    result = delta_E_CAM16UCS(JPAPBP_BATCH_1, JPAPBP_BATCH_2)
    broadcast_result = delta_E_CAM16UCS(JPAPBP_BATCH_1, JPAPBP_2)

    assert result.shape == (3,)
    assert broadcast_result.shape == (3,)
    np.testing.assert_allclose(
        broadcast_result,
        colour.difference.delta_E_CAM16UCS(JPAPBP_BATCH_1, JPAPBP_2),
        rtol=1e-10,
        atol=1e-10,
    )


def test_invalid_shape_raises():
    with pytest.raises(ValueError, match="3 values"):
        delta_E_CAM02UCS([54.0, -0.1], JPAPBP_2)


def test_non_finite_input_raises():
    with pytest.raises(ValueError, match="finite"):
        delta_E_CAM16UCS([54.0, np.nan, -0.1], JPAPBP_2)


def test_non_broadcastable_input_raises():
    with pytest.raises(ValueError, match="could not be broadcast"):
        delta_E_CAM16LCD(np.zeros((2, 3)), np.zeros((4, 3)))


def test_cam_uniform_space_workflow_from_spaces():
    cam02_ucs_1 = convert_color(SRGB_1, "sRGB", "CAM02-UCS")
    cam02_ucs_2 = convert_color(SRGB_2, "sRGB", "CAM02-UCS")
    cam02_lcd_1 = convert_color(SRGB_1, "sRGB", "CAM02-LCD")
    cam02_lcd_2 = convert_color(SRGB_2, "sRGB", "CAM02-LCD")
    cam02_scd_1 = convert_color(SRGB_1, "sRGB", "CAM02-SCD")
    cam02_scd_2 = convert_color(SRGB_2, "sRGB", "CAM02-SCD")
    cam16_ucs_1 = convert_color(SRGB_1, "sRGB", "CAM16-UCS")
    cam16_ucs_2 = convert_color(SRGB_2, "sRGB", "CAM16-UCS")

    cam02_ucs = delta_E_CAM02UCS(cam02_ucs_1, cam02_ucs_2)
    cam02_lcd = delta_E_CAM02LCD(cam02_lcd_1, cam02_lcd_2)
    cam02_scd = delta_E_CAM02SCD(cam02_scd_1, cam02_scd_2)
    cam16_ucs = delta_E_CAM16UCS(cam16_ucs_1, cam16_ucs_2)

    assert cam02_ucs.shape == (3,)
    assert cam16_ucs.shape == (3,)
    assert np.all(np.isfinite(cam02_ucs))
    assert np.all(np.isfinite(cam16_ucs))
    assert not np.allclose(cam02_ucs, cam02_lcd)
    assert not np.allclose(cam02_ucs, cam02_scd)
