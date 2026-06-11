"""Tests for CAM02-UCS, CAM02-LCD and CAM02-SCD spaces."""

from __future__ import annotations

import numpy as np
import pytest

from color.constants import D65_XYZ
from color.spaces import (
    CAM02LCD_to_JMh_CIECAM02,
    CAM02LCD_to_XYZ,
    CAM02SCD_to_JMh_CIECAM02,
    CAM02SCD_to_XYZ,
    CAM02UCS_to_JMh_CIECAM02,
    CAM02UCS_to_XYZ,
    JMh_CIECAM02_to_CAM02LCD,
    JMh_CIECAM02_to_CAM02SCD,
    JMh_CIECAM02_to_CAM02UCS,
    SpaceSpec,
    XYZ_to_CAM02LCD,
    XYZ_to_CAM02SCD,
    XYZ_to_CAM02UCS,
    convert_color,
)


XYZ = np.array([19.01, 20.0, 21.78])
XYZ_W = np.array([95.05, 100.0, 108.88])
VIEWING = {"XYZ_w": XYZ_W, "L_A": 318.31, "Y_b": 20.0}
JMh = np.array([41.7310911325, 0.108842175669, 219.048432658])


@pytest.mark.parametrize(
    "forward, inverse, expected",
    [
        (
            JMh_CIECAM02_to_CAM02UCS,
            CAM02UCS_to_JMh_CIECAM02,
            np.array([54.90433134171842, -0.084423616607959, -0.068483138796220]),
        ),
        (
            JMh_CIECAM02_to_CAM02LCD,
            CAM02LCD_to_JMh_CIECAM02,
            np.array([54.90433134171842, -0.084503954944839, -0.068548308018960]),
        ),
        (
            JMh_CIECAM02_to_CAM02SCD,
            CAM02SCD_to_JMh_CIECAM02,
            np.array([54.90433134171842, -0.084361780279910, -0.068432978118360]),
        ),
    ],
)
def test_JMh_CAM02_spaces_match_reference_values(forward, inverse, expected):
    result = forward(JMh)

    np.testing.assert_allclose(result, expected, atol=1e-10)
    np.testing.assert_allclose(inverse(result), JMh, atol=1e-9)


@pytest.mark.parametrize(
    "forward, inverse, expected",
    [
        (
            XYZ_to_CAM02UCS,
            CAM02UCS_to_XYZ,
            np.array([54.904331341732586, -0.084423616607675, -0.068483138796829]),
        ),
        (
            XYZ_to_CAM02LCD,
            CAM02LCD_to_XYZ,
            np.array([54.904331341732586, -0.084503954944555, -0.068548308019569]),
        ),
        (
            XYZ_to_CAM02SCD,
            CAM02SCD_to_XYZ,
            np.array([54.904331341732586, -0.084361780279626, -0.068432978118968]),
        ),
    ],
)
def test_XYZ_CAM02_spaces_match_reference_values_and_round_trip(forward, inverse, expected):
    result = forward(XYZ, **VIEWING)

    np.testing.assert_allclose(result, expected, atol=1e-10)
    np.testing.assert_allclose(inverse(result, **VIEWING), XYZ, atol=1e-10)


def test_XYZ_CAM02_spaces_preserve_batch_shape():
    values = np.array(
        [
            [19.01, 20.0, 21.78],
            [57.06, 43.06, 31.96],
        ]
    )

    cam = XYZ_to_CAM02UCS(values, **VIEWING)
    recovered = CAM02UCS_to_XYZ(cam, **VIEWING)

    assert cam.shape == values.shape
    np.testing.assert_allclose(recovered, values, atol=1e-9)


def test_convert_color_routes_CAM02_spaces():
    cam = convert_color(XYZ, "XYZ", SpaceSpec("CAM02-UCS", **VIEWING))
    recovered = convert_color(cam, SpaceSpec("CAM02-UCS", **VIEWING), "XYZ")
    lcd = convert_color(
        cam,
        SpaceSpec("CAM02-UCS", **VIEWING),
        SpaceSpec("CAM02-LCD", **VIEWING),
    )

    np.testing.assert_allclose(cam, XYZ_to_CAM02UCS(XYZ, **VIEWING))
    np.testing.assert_allclose(recovered, XYZ, atol=1e-10)
    np.testing.assert_allclose(lcd, XYZ_to_CAM02LCD(XYZ, **VIEWING), atol=1e-10)


def test_convert_color_routes_rgb_to_CAM02_and_back():
    RGB = np.array([0.2, 0.4, 0.6])

    cam = convert_color(RGB, "sRGB", SpaceSpec("CAM02-UCS", XYZ_w=D65_XYZ))
    recovered = convert_color(cam, SpaceSpec("CAM02-UCS", XYZ_w=D65_XYZ), "sRGB")

    assert cam.shape == (3,)
    np.testing.assert_allclose(recovered, RGB, atol=1e-10)


def test_viewing_conditions_change_result():
    average = XYZ_to_CAM02UCS(XYZ, **VIEWING, surround="Average")
    dim = XYZ_to_CAM02UCS(XYZ, **VIEWING, surround="Dim")

    assert not np.allclose(average, dim)


@pytest.mark.parametrize("function", [XYZ_to_CAM02UCS, CAM02UCS_to_XYZ])
def test_CAM02_spaces_reject_invalid_values(function):
    with pytest.raises(ValueError, match="3"):
        function([1.0, 2.0], **VIEWING)
    with pytest.raises(ValueError, match="finite"):
        function([1.0, np.nan, 3.0], **VIEWING)


def test_CAM02_spaces_reject_invalid_viewing_conditions():
    with pytest.raises(ValueError, match="surround"):
        XYZ_to_CAM02UCS(XYZ, **VIEWING, surround="Unknown")
    with pytest.raises(ValueError, match="XYZ_w"):
        XYZ_to_CAM02UCS(XYZ, XYZ_w=[95.0, 100.0])
