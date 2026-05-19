"""Tests for CIE 1976 lightness helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import Lstar_to_Y, Y_to_Lstar


def test_Y_to_Lstar_scalar():
    Lstar = Y_to_Lstar(100.0)

    assert Lstar == pytest.approx(100.0)


def test_Lstar_to_Y_scalar():
    Y = Lstar_to_Y(100.0)

    assert Y == pytest.approx(100.0)


def test_round_trip_array():
    Y = np.array([0.0, 1.0, 12.19722535, 50.0, 100.0])

    result = Lstar_to_Y(Y_to_Lstar(Y))

    np.testing.assert_allclose(result, Y, rtol=1e-7, atol=1e-9)


def test_image_like_array_shape_preserved():
    Y = np.array([
        [0.0, 18.0],
        [50.0, 100.0],
    ])

    Lstar = Y_to_Lstar(Y)
    Y_roundtrip = Lstar_to_Y(Lstar)

    assert Lstar.shape == (2, 2)
    assert Y_roundtrip.shape == (2, 2)
    np.testing.assert_allclose(Y_roundtrip, Y)


def test_custom_white_reference():
    Lstar = Y_to_Lstar(95.0, Y_n=95.0)
    Y = Lstar_to_Y(Lstar, Y_n=95.0)

    assert Lstar == pytest.approx(100.0)
    assert Y == pytest.approx(95.0)


def test_Y_to_Lstar_rejects_negative_Y():
    with pytest.raises(ValueError, match="non-negative"):
        Y_to_Lstar(-1.0)


def test_Lstar_to_Y_rejects_negative_Lstar():
    with pytest.raises(ValueError, match="non-negative"):
        Lstar_to_Y(-0.1)


def test_rejects_non_positive_Y_n():
    with pytest.raises(ValueError, match="positive"):
        Y_to_Lstar(10.0, Y_n=0.0)

    with pytest.raises(ValueError, match="positive"):
        Lstar_to_Y(10.0, Y_n=0.0)
