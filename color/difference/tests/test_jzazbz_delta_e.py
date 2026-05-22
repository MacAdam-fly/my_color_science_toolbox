"""Tests for Jzazbz colour difference."""

from __future__ import annotations

import numpy as np
import pytest

from color.difference import delta_E_Jzazbz
from color.spaces import convert_color


JZAZBZ_1 = np.array([0.010, 0.018, -0.012], dtype=np.float64)
JZAZBZ_2 = np.array([0.012, 0.011, -0.018], dtype=np.float64)
JZAZBZ_BATCH_1 = np.array(
    [
        [0.010, 0.018, -0.012],
        [0.015, -0.006, 0.008],
        [0.006, 0.004, -0.020],
    ],
    dtype=np.float64,
)
JZAZBZ_BATCH_2 = np.array(
    [
        [0.012, 0.011, -0.018],
        [0.013, -0.004, 0.005],
        [0.008, 0.007, -0.017],
    ],
    dtype=np.float64,
)
SRGB_1 = np.array([[0.72, 0.12, 0.10], [0.12, 0.54, 0.18]], dtype=np.float64)
SRGB_2 = np.array([[0.75, 0.15, 0.12], [0.10, 0.50, 0.22]], dtype=np.float64)


def test_delta_e_jzazbz_single_point_euclidean_distance():
    expected = np.linalg.norm(JZAZBZ_1 - JZAZBZ_2)
    np.testing.assert_allclose(delta_E_Jzazbz(JZAZBZ_1, JZAZBZ_2), expected)
    assert np.isscalar(delta_E_Jzazbz(JZAZBZ_1, JZAZBZ_2))


def test_delta_e_jzazbz_batch_and_broadcast_shapes():
    result = delta_E_Jzazbz(JZAZBZ_BATCH_1, JZAZBZ_BATCH_2)
    broadcast_result = delta_E_Jzazbz(JZAZBZ_BATCH_1, JZAZBZ_2)

    assert result.shape == (3,)
    assert broadcast_result.shape == (3,)
    np.testing.assert_allclose(
        result,
        np.linalg.norm(JZAZBZ_BATCH_1 - JZAZBZ_BATCH_2, axis=-1),
    )
    np.testing.assert_allclose(
        broadcast_result,
        np.linalg.norm(JZAZBZ_BATCH_1 - JZAZBZ_2, axis=-1),
    )


def test_delta_e_jzazbz_invalid_shape_raises():
    with pytest.raises(ValueError, match="3 values"):
        delta_E_Jzazbz([0.010, 0.018], JZAZBZ_2)


def test_delta_e_jzazbz_non_finite_input_raises():
    with pytest.raises(ValueError, match="finite"):
        delta_E_Jzazbz([0.010, np.nan, -0.012], JZAZBZ_2)


def test_delta_e_jzazbz_non_broadcastable_input_raises():
    with pytest.raises(ValueError, match="could not be broadcast"):
        delta_E_Jzazbz(np.zeros((2, 3)), np.zeros((4, 3)))


def test_delta_e_jzazbz_workflow_from_spaces():
    jzazbz_1 = convert_color(SRGB_1, "sRGB", "Jzazbz")
    jzazbz_2 = convert_color(SRGB_2, "sRGB", "Jzazbz")
    result = delta_E_Jzazbz(jzazbz_1, jzazbz_2)

    assert result.shape == (2,)
    assert np.all(np.isfinite(result))
    np.testing.assert_allclose(result, np.linalg.norm(jzazbz_1 - jzazbz_2, axis=-1))
