"""Tests for chromaticity helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import (
    emission_to_XYZ,
    XYZ_to_upvp1976,
    XYZ_to_uv1960,
    XYZ_to_xy,
    XYZ_to_xyY,
    upvp1976_to_xy,
    uv1960_to_xy,
    xyY_to_XYZ,
    xy_to_upvp1976,
    xy_to_uv1960,
)
from color.spectra import SpectralShape, from_dataset


def test_XYZ_to_xyY_single():
    xyY = XYZ_to_xyY([95.047, 100.0, 108.883])

    np.testing.assert_allclose(
        xyY,
        [0.31272661, 0.32902313, 100.0],
        rtol=1e-7,
    )


def test_xyY_to_XYZ_single():
    XYZ = xyY_to_XYZ([0.31272661, 0.32902313, 100.0])

    np.testing.assert_allclose(XYZ, [95.047, 100.0, 108.883], rtol=1e-6)


def test_round_trip_multi_row():
    XYZ = np.array([
        [95.047, 100.0, 108.883],
        [41.24, 21.26, 1.93],
    ])

    result = xyY_to_XYZ(XYZ_to_xyY(XYZ))

    np.testing.assert_allclose(result, XYZ)


def test_round_trip_image_like_array():
    XYZ = np.array([
        [
            [95.047, 100.0, 108.883],
            [41.24, 21.26, 1.93],
        ],
        [
            [10.0, 20.0, 30.0],
            [0.1, 0.2, 0.3],
        ],
    ])

    xyY = XYZ_to_xyY(XYZ)
    result = xyY_to_XYZ(xyY)
    xy = XYZ_to_xy(XYZ)

    assert xyY.shape == (2, 2, 3)
    assert result.shape == (2, 2, 3)
    assert xy.shape == (2, 2, 2)
    np.testing.assert_allclose(result, XYZ)


def test_XYZ_to_xy():
    xy = XYZ_to_xy([95.047, 100.0, 108.883])

    np.testing.assert_allclose(xy, [0.31272661, 0.32902313], rtol=1e-7)


def test_xy_to_uv1960_and_back():
    xy = np.array([
        [0.31270, 0.32900],
        [0.54369555, 0.32107941],
    ])

    uv = xy_to_uv1960(xy)
    recovered = uv1960_to_xy(uv)

    assert uv.shape == xy.shape
    np.testing.assert_allclose(recovered, xy, atol=1e-12)


def test_XYZ_to_uv1960_matches_xy_path():
    XYZ = np.array([95.047, 100.0, 108.883])

    np.testing.assert_allclose(
        XYZ_to_uv1960(XYZ),
        xy_to_uv1960(XYZ_to_xy(XYZ)),
        atol=1e-12,
    )


def test_xy_to_upvp1976_and_back():
    xy = np.array([
        [0.31270, 0.32900],
        [0.54369555, 0.32107941],
    ])

    upvp = xy_to_upvp1976(xy)
    recovered = upvp1976_to_xy(upvp)

    assert upvp.shape == xy.shape
    np.testing.assert_allclose(recovered, xy, atol=1e-12)


def test_XYZ_to_upvp1976_matches_xy_path_and_uv1960_relation():
    XYZ = np.array([95.047, 100.0, 108.883])
    uv = XYZ_to_uv1960(XYZ)
    upvp = XYZ_to_upvp1976(XYZ)

    np.testing.assert_allclose(upvp, xy_to_upvp1976(XYZ_to_xy(XYZ)), atol=1e-12)
    np.testing.assert_allclose(upvp[..., 0], uv[..., 0], atol=1e-12)
    np.testing.assert_allclose(upvp[..., 1], 1.5 * uv[..., 1], atol=1e-12)


def test_zero_xyz_uses_fallback_xy_and_preserves_y():
    xyY = XYZ_to_xyY([0.0, 0.0, 0.0], fallback_xy=(0.3127, 0.3290))

    np.testing.assert_allclose(xyY, [0.3127, 0.3290, 0.0])


def test_xyY_to_XYZ_with_zero_y_returns_black_with_input_Y():
    XYZ = xyY_to_XYZ([0.3127, 0.0, 10.0])

    np.testing.assert_allclose(XYZ, [0.0, 10.0, 0.0])


def test_rejects_invalid_triplet_shape():
    with pytest.raises(ValueError, match="3 values"):
        XYZ_to_xyY([1.0, 2.0])


def test_rejects_invalid_fallback_xy():
    with pytest.raises(ValueError, match="fallback_xy"):
        XYZ_to_xyY([0.0, 0.0, 0.0], fallback_xy=(0.0,))


def test_d65_dataset_xy_smoke():
    shape = SpectralShape(360, 780, 1)
    d65 = from_dataset("illuminants", "D65").align(shape)

    xy = XYZ_to_xy(emission_to_XYZ(d65, shape=shape))

    np.testing.assert_allclose(xy, [0.3127, 0.3290], atol=5e-5)
