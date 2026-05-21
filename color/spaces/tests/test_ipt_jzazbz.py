"""Tests for IPT and Jzazbz colour spaces."""

from __future__ import annotations

import numpy as np
import pytest

from color.spaces import (
    IPT_hue_angle,
    IPT_to_XYZ,
    JzCzhz_to_Jzazbz,
    Jzazbz_to_JzCzhz,
    Jzazbz_to_XYZ,
    XYZ_to_IPT,
    XYZ_to_Jzazbz,
    convert_color,
)


REFERENCE_XYZ = np.array([20.654008, 12.197225, 5.136952])


def test_IPT_matches_colour_reference():
    colour = pytest.importorskip("colour")

    np.testing.assert_allclose(
        XYZ_to_IPT(XYZ_D65_referred=REFERENCE_XYZ),
        colour.XYZ_to_IPT(REFERENCE_XYZ / 100.0),
        atol=1e-10,
    )


def test_IPT_to_XYZ_matches_colour_reference():
    colour = pytest.importorskip("colour")
    IPT = np.array([0.38426191, 0.38487306, 0.18886838])

    np.testing.assert_allclose(
        IPT_to_XYZ(IPT),
        100.0 * colour.IPT_to_XYZ(IPT),
        atol=1e-6,
    )


def test_Jzazbz_matches_colour_reference():
    colour = pytest.importorskip("colour")

    np.testing.assert_allclose(
        XYZ_to_Jzazbz(XYZ_D65_referred=REFERENCE_XYZ),
        colour.XYZ_to_Jzazbz(REFERENCE_XYZ / 100.0),
        atol=1e-10,
    )


def test_Jzazbz_to_XYZ_matches_colour_reference():
    colour = pytest.importorskip("colour")
    Jzazbz = np.array([0.00535048, 0.00924302, 0.00526007])

    np.testing.assert_allclose(
        Jzazbz_to_XYZ(Jzazbz),
        100.0 * colour.Jzazbz_to_XYZ(Jzazbz),
        atol=1e-5,
    )


@pytest.mark.parametrize(
    "forward, inverse",
    [
        (XYZ_to_IPT, IPT_to_XYZ),
        (XYZ_to_Jzazbz, Jzazbz_to_XYZ),
    ],
)
def test_round_trip_single_and_batch(forward, inverse):
    XYZ = np.array([
        [20.654008, 12.197225, 5.136952],
        [14.222010, 23.042768, 10.495772],
        [96.907232, 100.000000, 112.179215],
    ])

    values = forward(XYZ)
    recovered = inverse(values)

    assert values.shape == XYZ.shape
    np.testing.assert_allclose(recovered, XYZ, atol=1e-5)


def test_IPT_hue_angle_returns_degrees():
    IPT = np.array([
        [0.96907232, 1.0, 1.12179215],
        [0.5, -0.2, 0.1],
    ])

    hue = IPT_hue_angle(IPT)

    assert hue.shape == (2,)
    assert np.all((0.0 <= hue) & (hue < 360.0))


def test_convert_color_routes_IPT_and_Jzazbz():
    XYZ = REFERENCE_XYZ

    IPT = convert_color(XYZ, "XYZ", "IPT")
    np.testing.assert_allclose(convert_color(IPT, "IPT", "XYZ"), XYZ, atol=1e-5)

    Jzazbz = convert_color([0.25, 0.5, 0.75], "sRGB", "Jzazbz")
    Oklab = convert_color(Jzazbz, "Jzazbz", "Oklab")

    assert Jzazbz.shape == (3,)
    assert Oklab.shape == (3,)
    assert np.all(np.isfinite(Jzazbz))
    assert np.all(np.isfinite(Oklab))


def test_Jzazbz_to_JzCzhz_round_trip_single_and_batch():
    Jzazbz = np.array([
        [0.00535048, 0.00924302, 0.00526007],
        [0.01200000, -0.00300000, 0.00600000],
        [0.02000000, 0.00000000, -0.00400000],
    ])

    JzCzhz = Jzazbz_to_JzCzhz(Jzazbz)
    recovered = JzCzhz_to_Jzazbz(JzCzhz)

    assert JzCzhz.shape == Jzazbz.shape
    assert np.all((0.0 <= JzCzhz[..., 2]) & (JzCzhz[..., 2] < 360.0))
    np.testing.assert_allclose(recovered, Jzazbz, atol=1e-14)


def test_convert_color_routes_JzCzhz():
    Jzazbz = XYZ_to_Jzazbz(REFERENCE_XYZ)

    JzCzhz = convert_color(Jzazbz, "Jzazbz", "JzCzhz")
    XYZ = convert_color(JzCzhz, "JzCzhz", "XYZ")

    assert JzCzhz.shape == (3,)
    np.testing.assert_allclose(JzCzhz_to_Jzazbz(JzCzhz), Jzazbz, atol=1e-14)
    np.testing.assert_allclose(XYZ, REFERENCE_XYZ, atol=2e-5)


@pytest.mark.parametrize(
    "function",
    [
        XYZ_to_IPT,
        IPT_to_XYZ,
        IPT_hue_angle,
        XYZ_to_Jzazbz,
        Jzazbz_to_XYZ,
        Jzazbz_to_JzCzhz,
        JzCzhz_to_Jzazbz,
    ],
)
def test_invalid_shape_raises(function):
    with pytest.raises(ValueError, match="3 values on the last axis"):
        function([1.0, 2.0])


@pytest.mark.parametrize(
    "function",
    [
        XYZ_to_IPT,
        IPT_to_XYZ,
        IPT_hue_angle,
        XYZ_to_Jzazbz,
        Jzazbz_to_XYZ,
        Jzazbz_to_JzCzhz,
        JzCzhz_to_Jzazbz,
    ],
)
def test_nonfinite_input_raises(function):
    with pytest.raises(ValueError, match="finite"):
        function([1.0, np.nan, 3.0])
