"""Tests for CIE xyY helpers exposed by color.spaces."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import XYZ_to_xy as colorimetry_XYZ_to_xy
from color.colorimetry import XYZ_to_xyY as colorimetry_XYZ_to_xyY
from color.colorimetry import xyY_to_XYZ as colorimetry_xyY_to_XYZ
from color.spaces import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ, xyY_to_xy


def test_XYZ_to_xyY_matches_colorimetry():
    XYZ = np.array([0.95047, 1.0, 1.08883])

    np.testing.assert_allclose(XYZ_to_xyY(XYZ), colorimetry_XYZ_to_xyY(XYZ))


def test_xyY_to_XYZ_matches_colorimetry():
    xyY = np.array([0.31272661, 0.32902313, 1.0])

    np.testing.assert_allclose(xyY_to_XYZ(xyY), colorimetry_xyY_to_XYZ(xyY))


def test_XYZ_xyY_round_trip_batch():
    XYZ = np.array([
        [[0.95047, 1.0, 1.08883], [0.4124, 0.2126, 0.0193]],
        [[0.1, 0.2, 0.3], [0.02, 0.03, 0.04]],
    ])

    xyY = XYZ_to_xyY(XYZ)
    recovered = xyY_to_XYZ(xyY)

    assert xyY.shape == XYZ.shape
    np.testing.assert_allclose(recovered, XYZ)


def test_XYZ_to_xy_matches_colorimetry_and_returns_two_channels():
    XYZ = np.array([[0.95047, 1.0, 1.08883], [0.4124, 0.2126, 0.0193]])

    xy = XYZ_to_xy(XYZ)

    assert xy.shape == (2, 2)
    np.testing.assert_allclose(xy, colorimetry_XYZ_to_xy(XYZ))


def test_xyY_to_xy_returns_first_two_channels():
    xyY = np.array([
        [0.3127, 0.3290, 1.0],
        [0.64, 0.33, 0.2],
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
