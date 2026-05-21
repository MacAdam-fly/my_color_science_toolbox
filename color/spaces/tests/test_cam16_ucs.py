"""Tests for CAM16-UCS, CAM16-LCD and CAM16-SCD spaces."""

from __future__ import annotations

import numpy as np
import pytest

from color.constants import D65_XYZ
from color.spaces import (
    CAM16LCD_to_JMh_CIECAM16,
    CAM16LCD_to_XYZ,
    CAM16SCD_to_JMh_CIECAM16,
    CAM16SCD_to_XYZ,
    CAM16UCS_to_JMh_CIECAM16,
    CAM16UCS_to_XYZ,
    JMh_CIECAM16_to_CAM16LCD,
    JMh_CIECAM16_to_CAM16SCD,
    JMh_CIECAM16_to_CAM16UCS,
    SpaceSpec,
    XYZ_to_CAM16LCD,
    XYZ_to_CAM16SCD,
    XYZ_to_CAM16UCS,
    convert_color,
)


XYZ = np.array([19.01, 20.0, 21.78])
XYZ_W = np.array([95.05, 100.0, 108.88])
VIEWING = {"XYZ_w": XYZ_W, "L_A": 318.31, "Y_b": 20.0}
JMh = np.array([41.7310911325, 0.108842175669, 219.048432658])


@pytest.mark.parametrize(
    "forward, inverse, colour_forward, colour_inverse",
    [
        (
            JMh_CIECAM16_to_CAM16UCS,
            CAM16UCS_to_JMh_CIECAM16,
            "JMh_CAM16_to_CAM16UCS",
            "CAM16UCS_to_JMh_CAM16",
        ),
        (
            JMh_CIECAM16_to_CAM16LCD,
            CAM16LCD_to_JMh_CIECAM16,
            "JMh_CAM16_to_CAM16LCD",
            "CAM16LCD_to_JMh_CAM16",
        ),
        (
            JMh_CIECAM16_to_CAM16SCD,
            CAM16SCD_to_JMh_CIECAM16,
            "JMh_CAM16_to_CAM16SCD",
            "CAM16SCD_to_JMh_CAM16",
        ),
    ],
)
def test_JMh_CAM16_spaces_match_colour(forward, inverse, colour_forward, colour_inverse):
    colour = pytest.importorskip("colour")

    result = forward(JMh)
    expected = getattr(colour, colour_forward)(JMh)

    np.testing.assert_allclose(result, expected, atol=1e-10)
    np.testing.assert_allclose(inverse(result), getattr(colour, colour_inverse)(expected), atol=1e-10)
    np.testing.assert_allclose(inverse(result), JMh, atol=1e-9)


@pytest.mark.parametrize(
    "forward, inverse, colour_forward",
    [
        (XYZ_to_CAM16UCS, CAM16UCS_to_XYZ, "XYZ_to_CAM16UCS"),
        (XYZ_to_CAM16LCD, CAM16LCD_to_XYZ, "XYZ_to_CAM16LCD"),
        (XYZ_to_CAM16SCD, CAM16SCD_to_XYZ, "XYZ_to_CAM16SCD"),
    ],
)
def test_XYZ_CAM16_spaces_match_colour_and_round_trip(forward, inverse, colour_forward):
    colour = pytest.importorskip("colour")

    result = forward(XYZ, **VIEWING)
    expected = getattr(colour, colour_forward)(
        XYZ / 100.0,
        XYZ_w=XYZ_W / 100.0,
        L_A=318.31,
        Y_b=20.0,
    )

    np.testing.assert_allclose(result, expected, atol=1e-10)
    np.testing.assert_allclose(inverse(result, **VIEWING), XYZ, atol=1e-10)


def test_XYZ_CAM16_spaces_preserve_batch_shape():
    values = np.array(
        [
            [19.01, 20.0, 21.78],
            [57.06, 43.06, 31.96],
        ]
    )

    cam = XYZ_to_CAM16UCS(values, **VIEWING)
    recovered = CAM16UCS_to_XYZ(cam, **VIEWING)

    assert cam.shape == values.shape
    np.testing.assert_allclose(recovered, values, atol=1e-9)


def test_convert_color_routes_CAM16_spaces():
    cam = convert_color(XYZ, "XYZ", SpaceSpec("CAM16-UCS", **VIEWING))
    recovered = convert_color(cam, SpaceSpec("CAM16-UCS", **VIEWING), "XYZ")
    lcd = convert_color(
        cam,
        SpaceSpec("CAM16-UCS", **VIEWING),
        SpaceSpec("CAM16-LCD", **VIEWING),
    )

    np.testing.assert_allclose(cam, XYZ_to_CAM16UCS(XYZ, **VIEWING))
    np.testing.assert_allclose(recovered, XYZ, atol=1e-10)
    np.testing.assert_allclose(lcd, XYZ_to_CAM16LCD(XYZ, **VIEWING), atol=1e-10)


def test_convert_color_routes_rgb_to_CAM16_and_back():
    RGB = np.array([0.2, 0.4, 0.6])

    cam = convert_color(RGB, "sRGB", SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ))
    recovered = convert_color(cam, SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ), "sRGB")

    assert cam.shape == (3,)
    np.testing.assert_allclose(recovered, RGB, atol=1e-10)


def test_viewing_conditions_change_result():
    average = XYZ_to_CAM16UCS(XYZ, **VIEWING, surround="Average")
    dim = XYZ_to_CAM16UCS(XYZ, **VIEWING, surround="Dim")

    assert not np.allclose(average, dim)


@pytest.mark.parametrize("function", [XYZ_to_CAM16UCS, CAM16UCS_to_XYZ])
def test_CAM16_spaces_reject_invalid_values(function):
    with pytest.raises(ValueError, match="3"):
        function([1.0, 2.0], **VIEWING)
    with pytest.raises(ValueError, match="finite"):
        function([1.0, np.nan, 3.0], **VIEWING)


def test_CAM16_spaces_reject_invalid_viewing_conditions():
    with pytest.raises(ValueError, match="surround"):
        XYZ_to_CAM16UCS(XYZ, **VIEWING, surround="Unknown")
    with pytest.raises(ValueError, match="XYZ_w"):
        XYZ_to_CAM16UCS(XYZ, XYZ_w=[95.0, 100.0])
