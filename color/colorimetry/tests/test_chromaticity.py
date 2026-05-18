"""Tests for chromaticity helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import (
    XYZ_to_xy,
    XYZ_to_xyY,
    emission_to_xyz,
    xyY_to_XYZ,
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
    cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm").align(shape)
    d65 = from_dataset("illuminants", "D65").align(shape)

    xy = XYZ_to_xy(emission_to_xyz(d65, cmfs, shape=shape))

    np.testing.assert_allclose(xy, [0.3127, 0.3290], atol=5e-5)
