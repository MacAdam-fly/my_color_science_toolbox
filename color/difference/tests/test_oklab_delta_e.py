"""Tests for Oklab colour difference."""

from __future__ import annotations

import numpy as np
import pytest

from color.difference import delta_E_Oklab
from color.spaces import convert_color


OKLAB_1 = np.array([0.65, 0.12, -0.08], dtype=np.float64)
OKLAB_2 = np.array([0.58, 0.04, -0.11], dtype=np.float64)
OKLAB_BATCH_1 = np.array(
    [
        [0.65, 0.12, -0.08],
        [0.72, -0.04, 0.10],
        [0.42, 0.02, -0.18],
    ],
    dtype=np.float64,
)
OKLAB_BATCH_2 = np.array(
    [
        [0.58, 0.04, -0.11],
        [0.70, -0.01, 0.05],
        [0.46, 0.05, -0.15],
    ],
    dtype=np.float64,
)
SRGB_1 = np.array([[0.72, 0.12, 0.10], [0.12, 0.54, 0.18]], dtype=np.float64)
SRGB_2 = np.array([[0.75, 0.15, 0.12], [0.10, 0.50, 0.22]], dtype=np.float64)


def test_delta_e_oklab_single_point_euclidean_distance():
    expected = np.linalg.norm(OKLAB_1 - OKLAB_2)
    np.testing.assert_allclose(delta_E_Oklab(OKLAB_1, OKLAB_2), expected)
    assert np.isscalar(delta_E_Oklab(OKLAB_1, OKLAB_2))


def test_delta_e_oklab_batch_and_broadcast_shapes():
    result = delta_E_Oklab(OKLAB_BATCH_1, OKLAB_BATCH_2)
    broadcast_result = delta_E_Oklab(OKLAB_BATCH_1, OKLAB_2)

    assert result.shape == (3,)
    assert broadcast_result.shape == (3,)
    np.testing.assert_allclose(
        result,
        np.linalg.norm(OKLAB_BATCH_1 - OKLAB_BATCH_2, axis=-1),
    )
    np.testing.assert_allclose(
        broadcast_result,
        np.linalg.norm(OKLAB_BATCH_1 - OKLAB_2, axis=-1),
    )


def test_delta_e_oklab_invalid_shape_raises():
    with pytest.raises(ValueError, match="3 values"):
        delta_E_Oklab([0.65, 0.12], OKLAB_2)


def test_delta_e_oklab_non_finite_input_raises():
    with pytest.raises(ValueError, match="finite"):
        delta_E_Oklab([0.65, np.nan, -0.08], OKLAB_2)


def test_delta_e_oklab_non_broadcastable_input_raises():
    with pytest.raises(ValueError, match="could not be broadcast"):
        delta_E_Oklab(np.zeros((2, 3)), np.zeros((4, 3)))


def test_delta_e_oklab_workflow_from_spaces():
    oklab_1 = convert_color(SRGB_1, "sRGB", "Oklab")
    oklab_2 = convert_color(SRGB_2, "sRGB", "Oklab")
    result = delta_E_Oklab(oklab_1, oklab_2)

    assert result.shape == (2,)
    assert np.all(np.isfinite(result))
    np.testing.assert_allclose(result, np.linalg.norm(oklab_1 - oklab_2, axis=-1))
