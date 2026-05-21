"""Tests for Lab, Luv, Oklab and their cylindrical derivatives."""

from __future__ import annotations

import numpy as np
import pytest

from color.constants import D50_XYZ, D65_XYZ
from color.spaces import (
    DEFAULT_WHITEPOINT_XYZ,
    Lab_to_LCHab,
    Lab_to_XYZ,
    LCHab_to_Lab,
    LCHuv_to_Luv,
    Luv_to_LCHuv,
    Luv_to_XYZ,
    Oklab_to_Oklch,
    Oklab_to_XYZ,
    Oklch_to_Oklab,
    SpaceSpec,
    XYZ_to_Lab,
    XYZ_to_Luv,
    XYZ_to_Oklab,
    convert_color,
)


def _whitepoint_xy(whitepoint_XYZ):
    whitepoint = np.asarray(whitepoint_XYZ, dtype=np.float64)
    return whitepoint[:2] / np.sum(whitepoint)


def test_default_whitepoint_is_D65_reference_domain():
    np.testing.assert_allclose(DEFAULT_WHITEPOINT_XYZ, D65_XYZ)
    assert not DEFAULT_WHITEPOINT_XYZ.flags.writeable


def test_Lab_matches_colour_reference():
    colour = pytest.importorskip("colour")
    XYZ = np.array([20.0, 30.0, 40.0])
    illuminant = _whitepoint_xy(DEFAULT_WHITEPOINT_XYZ)

    np.testing.assert_allclose(
        XYZ_to_Lab(XYZ),
        colour.XYZ_to_Lab(XYZ / 100.0, illuminant=illuminant),
        atol=1e-10,
    )


def test_Luv_matches_colour_reference():
    colour = pytest.importorskip("colour")
    XYZ = np.array([20.0, 30.0, 40.0])
    illuminant = _whitepoint_xy(DEFAULT_WHITEPOINT_XYZ)

    np.testing.assert_allclose(
        XYZ_to_Luv(XYZ),
        colour.XYZ_to_Luv(XYZ / 100.0, illuminant=illuminant),
        atol=1e-10,
    )


def test_Oklab_matches_colour_reference():
    colour = pytest.importorskip("colour")
    XYZ = np.array([20.0, 30.0, 40.0])

    np.testing.assert_allclose(
        XYZ_to_Oklab(XYZ_D65_referred=XYZ),
        colour.XYZ_to_Oklab(XYZ / 100.0),
        atol=1e-10,
    )


@pytest.mark.parametrize(
    "forward, inverse",
    [
        (XYZ_to_Lab, Lab_to_XYZ),
        (XYZ_to_Luv, Luv_to_XYZ),
        (XYZ_to_Oklab, Oklab_to_XYZ),
    ],
)
def test_XYZ_round_trip_single_and_batch(forward, inverse):
    XYZ = np.array([
        [20.0, 30.0, 40.0],
        [5.0, 10.0, 2.0],
    ])

    values = forward(XYZ)
    recovered = inverse(values)

    assert values.shape == XYZ.shape
    np.testing.assert_allclose(recovered, XYZ, atol=1e-5)


@pytest.mark.parametrize(
    "to_lch, from_lch, value",
    [
        (Lab_to_LCHab, LCHab_to_Lab, np.array([50.0, 20.0, -30.0])),
        (Luv_to_LCHuv, LCHuv_to_Luv, np.array([50.0, 20.0, -30.0])),
        (Oklab_to_Oklch, Oklch_to_Oklab, np.array([0.5, 0.1, -0.2])),
    ],
)
def test_cylindrical_round_trip(to_lch, from_lch, value):
    lch = to_lch(value)
    recovered = from_lch(lch)

    assert lch.shape == value.shape
    assert 0.0 <= lch[-1] < 360.0
    np.testing.assert_allclose(recovered, value, atol=1e-12)


def test_custom_whitepoint_changes_Lab_and_round_trips():
    XYZ = np.array([20.0, 30.0, 40.0])
    whitepoint = D50_XYZ

    Lab = XYZ_to_Lab(XYZ, whitepoint_XYZ=whitepoint)
    recovered = Lab_to_XYZ(Lab, whitepoint_XYZ=whitepoint)

    assert not np.allclose(Lab, XYZ_to_Lab(XYZ))
    np.testing.assert_allclose(recovered, XYZ)


def test_Luv_black_round_trip():
    Luv = XYZ_to_Luv([0.0, 0.0, 0.0])

    np.testing.assert_allclose(Luv, [0.0, 0.0, 0.0])
    np.testing.assert_allclose(Luv_to_XYZ(Luv), [0.0, 0.0, 0.0])


@pytest.mark.parametrize("function", [XYZ_to_Lab, Lab_to_XYZ, XYZ_to_Luv, Luv_to_XYZ])
def test_rejects_invalid_whitepoint(function):
    with pytest.raises(ValueError, match="whitepoint_XYZ"):
        function([20.0, 30.0, 40.0], whitepoint_XYZ=[1.0, 1.0])
    with pytest.raises(ValueError, match="positive"):
        function([20.0, 30.0, 40.0], whitepoint_XYZ=[1.0, 0.0, 1.0])


@pytest.mark.parametrize("function", [XYZ_to_Lab, XYZ_to_Luv, XYZ_to_Oklab])
def test_rejects_invalid_colour_values(function):
    with pytest.raises(ValueError, match="3 values"):
        function([20.0, 30.0])
    with pytest.raises(ValueError, match="finite"):
        function([20.0, np.nan, 40.0])


def test_convert_color_uses_source_and_target_space_spec_parameters():
    XYZ = np.array([20.0, 30.0, 40.0])
    Lab_D50 = XYZ_to_Lab(XYZ, whitepoint_XYZ=D50_XYZ)

    result = convert_color(
        Lab_D50,
        SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
        SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
    )
    expected = XYZ_to_Luv(XYZ, whitepoint_XYZ=D65_XYZ)

    np.testing.assert_allclose(result, expected, atol=1e-10)


def test_convert_color_derived_to_derived_path():
    XYZ = np.array([20.0, 30.0, 40.0])
    LCHab = convert_color(
        XYZ,
        "XYZ",
        SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
    )

    Oklch = convert_color(
        LCHab,
        SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
        "Oklch",
    )
    recovered = convert_color(Oklch, "Oklch", "XYZ")

    np.testing.assert_allclose(recovered, XYZ, atol=1e-5)


def test_convert_color_RGB_to_Lab():
    RGB = np.array([0.2, 0.4, 0.6])
    Lab = convert_color(
        RGB,
        "sRGB",
        SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ),
    )

    assert Lab.shape == (3,)
    np.testing.assert_allclose(
        convert_color(Lab, SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ), "XYZ"),
        convert_color(RGB, "sRGB", "XYZ"),
    )
