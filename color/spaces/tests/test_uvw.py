"""Tests for CIE 1964 U*V*W* helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.constants import D50_XYZ, D65_XYZ
from color.spaces import SpaceSpec, UVW_to_XYZ, XYZ_to_UVW, convert_color


def _whitepoint_xy(whitepoint_XYZ):
    whitepoint = np.asarray(whitepoint_XYZ, dtype=np.float64)
    return whitepoint[:2] / np.sum(whitepoint)


def test_XYZ_to_UVW_matches_colour_reference():
    colour = pytest.importorskip("colour")
    XYZ = np.array([20.654008, 12.197225, 5.136952])
    whitepoint_xy = np.array([0.31270, 0.32900])

    np.testing.assert_allclose(
        XYZ_to_UVW(XYZ, whitepoint_xy=whitepoint_xy),
        colour.XYZ_to_UVW(XYZ, illuminant=whitepoint_xy),
        atol=1e-8,
    )


def test_UVW_to_XYZ_matches_colour_reference():
    colour = pytest.importorskip("colour")
    UVW = np.array([94.55035725, 11.55536523, 40.54757405])
    whitepoint_xy = np.array([0.31270, 0.32900])

    np.testing.assert_allclose(
        UVW_to_XYZ(UVW, whitepoint_xy=whitepoint_xy),
        colour.UVW_to_XYZ(UVW, illuminant=whitepoint_xy),
        atol=1e-8,
    )


def test_UVW_round_trip_single_and_batch():
    XYZ = np.array([
        [20.654008, 12.197225, 5.136952],
        [14.222010, 23.042768, 10.495772],
    ])

    UVW = XYZ_to_UVW(XYZ, whitepoint_XYZ=D65_XYZ)
    recovered = UVW_to_XYZ(UVW, whitepoint_XYZ=D65_XYZ)

    assert UVW.shape == XYZ.shape
    np.testing.assert_allclose(recovered, XYZ, atol=1e-8)


def test_UVW_whitepoint_XYZ_and_xy_are_equivalent():
    XYZ = np.array([20.0, 30.0, 40.0])
    whitepoint_xy = _whitepoint_xy(D50_XYZ)

    np.testing.assert_allclose(
        XYZ_to_UVW(XYZ, whitepoint_XYZ=D50_XYZ),
        XYZ_to_UVW(XYZ, whitepoint_xy=whitepoint_xy),
        atol=1e-12,
    )


def test_convert_color_routes_UVW_with_space_spec():
    XYZ = np.array([20.654008, 12.197225, 5.136952])
    spec = SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ)

    UVW = convert_color(XYZ, "XYZ", spec)
    recovered = convert_color(UVW, spec, "XYZ")

    np.testing.assert_allclose(UVW, XYZ_to_UVW(XYZ, whitepoint_XYZ=D65_XYZ))
    np.testing.assert_allclose(recovered, XYZ, atol=1e-8)


def test_UVW_rejects_invalid_values_and_whitepoint_options():
    with pytest.raises(ValueError, match="3 values"):
        XYZ_to_UVW([1.0, 2.0])
    with pytest.raises(ValueError, match="finite"):
        UVW_to_XYZ([1.0, np.nan, 3.0])
    with pytest.raises(ValueError, match="cannot both"):
        XYZ_to_UVW([1.0, 2.0, 3.0], whitepoint_XYZ=D65_XYZ, whitepoint_xy=(0.3127, 0.3290))
    with pytest.raises(ValueError, match="2 values"):
        XYZ_to_UVW([1.0, 2.0, 3.0], whitepoint_xy=(0.3127,))
