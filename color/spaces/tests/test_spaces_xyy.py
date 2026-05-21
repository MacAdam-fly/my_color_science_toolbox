"""Tests for CIE xyY helpers exposed by color.spaces."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import XYZ_to_xy as colorimetry_XYZ_to_xy
from color.colorimetry import XYZ_to_upvp1976 as colorimetry_XYZ_to_upvp1976
from color.colorimetry import XYZ_to_uv1960 as colorimetry_XYZ_to_uv1960
from color.colorimetry import XYZ_to_xyY as colorimetry_XYZ_to_xyY
from color.colorimetry import xy_to_upvp1976 as colorimetry_xy_to_upvp1976
from color.colorimetry import xy_to_uv1960 as colorimetry_xy_to_uv1960
from color.colorimetry import xyY_to_XYZ as colorimetry_xyY_to_XYZ
from color.spaces import (
    XYZ_to_upvp1976,
    XYZ_to_uv1960,
    XYZ_to_xy,
    XYZ_to_xyY,
    xyY_to_XYZ,
    xyY_to_xy,
    xy_to_upvp1976,
    xy_to_uv1960,
)


def test_XYZ_to_xyY_matches_colorimetry():
    XYZ = np.array([95.047, 100.0, 108.883])

    np.testing.assert_allclose(XYZ_to_xyY(XYZ), colorimetry_XYZ_to_xyY(XYZ))


def test_xyY_to_XYZ_matches_colorimetry():
    xyY = np.array([0.31272661, 0.32902313, 100.0])

    np.testing.assert_allclose(xyY_to_XYZ(xyY), colorimetry_xyY_to_XYZ(xyY))


def test_XYZ_xyY_round_trip_batch():
    XYZ = np.array([
        [[95.047, 100.0, 108.883], [41.24, 21.26, 1.93]],
        [[10.0, 20.0, 30.0], [2.0, 3.0, 4.0]],
    ])

    xyY = XYZ_to_xyY(XYZ)
    recovered = xyY_to_XYZ(xyY)

    assert xyY.shape == XYZ.shape
    np.testing.assert_allclose(recovered, XYZ)


def test_XYZ_to_xy_matches_colorimetry_and_returns_two_channels():
    XYZ = np.array([[95.047, 100.0, 108.883], [41.24, 21.26, 1.93]])

    xy = XYZ_to_xy(XYZ)

    assert xy.shape == (2, 2)
    np.testing.assert_allclose(xy, colorimetry_XYZ_to_xy(XYZ))


def test_xyY_to_xy_returns_first_two_channels():
    xyY = np.array([
        [0.3127, 0.3290, 100.0],
        [0.64, 0.33, 20.0],
    ])

    xy = xyY_to_xy(xyY)

    np.testing.assert_allclose(xy, xyY[:, :2])
    assert not np.shares_memory(xy, xyY)


def test_XYZ_to_xyY_zero_uses_fallback_xy():
    result = XYZ_to_xyY([0.0, 0.0, 0.0], fallback_xy=(0.3127, 0.3290))

    np.testing.assert_allclose(result, [0.3127, 0.3290, 0.0])


def test_xyY_to_xy_rejects_invalid_shape():
    with pytest.raises(ValueError, match="3 values"):
        xyY_to_xy([0.3127, 0.3290])


def test_spaces_exports_chromaticity_helpers():
    XYZ = np.array([95.047, 100.0, 108.883])
    xy = XYZ_to_xy(XYZ)

    np.testing.assert_allclose(XYZ_to_uv1960(XYZ), colorimetry_XYZ_to_uv1960(XYZ))
    np.testing.assert_allclose(xy_to_uv1960(xy), colorimetry_xy_to_uv1960(xy))
    np.testing.assert_allclose(XYZ_to_upvp1976(XYZ), colorimetry_XYZ_to_upvp1976(XYZ))
    np.testing.assert_allclose(xy_to_upvp1976(xy), colorimetry_xy_to_upvp1976(xy))
