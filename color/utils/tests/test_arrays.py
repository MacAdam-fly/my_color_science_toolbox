"""Tests for shared array utilities."""

from __future__ import annotations

import numpy as np
import pytest

from color.utils.arrays import (
    as_float_array,
    as_float_result,
    as_last_axis,
    as_last_axis_pairs,
    as_last_axis_triplets,
    broadcast_last_axis,
    broadcast_pairs,
    broadcast_triplets,
    split_last_axis,
)


def test_as_float_array_converts_dtype():
    arr = as_float_array([1, 2, 3])

    assert arr.dtype == np.float64
    np.testing.assert_array_equal(arr, np.array([1.0, 2.0, 3.0]))


def test_as_float_array_rejects_non_finite_by_default():
    with pytest.raises(ValueError, match="finite"):
        as_float_array([1.0, np.nan], name="sample")


def test_as_float_array_can_allow_non_finite():
    arr = as_float_array([1.0, np.nan], finite=False)

    assert np.isnan(arr[1])


def test_as_float_result_returns_scalar_or_array():
    scalar = as_float_result(np.array(1.5))
    array = as_float_result(np.array([1.0, 2.0]))

    assert np.isscalar(scalar)
    np.testing.assert_array_equal(array, np.array([1.0, 2.0]))


def test_as_last_axis_validates_size():
    arr = as_last_axis([[1, 2], [3, 4]], 2, name="xy")

    assert arr.shape == (2, 2)
    with pytest.raises(ValueError, match="2 values"):
        as_last_axis([1, 2, 3], 2, name="xy")


def test_as_last_axis_triplets_and_pairs():
    np.testing.assert_array_equal(
        as_last_axis_triplets([1, 2, 3]),
        np.array([1.0, 2.0, 3.0]),
    )
    np.testing.assert_array_equal(
        as_last_axis_pairs([1, 2]),
        np.array([1.0, 2.0]),
    )


def test_broadcast_last_axis_success_and_failure():
    a, b = broadcast_last_axis(np.zeros((2, 3)), np.ones(3), 3)

    assert a.shape == (2, 3)
    assert b.shape == (2, 3)
    with pytest.raises(ValueError, match="could not be broadcast"):
        broadcast_last_axis(np.zeros((2, 3)), np.zeros((4, 3)), 3)


def test_broadcast_triplets_and_pairs():
    triplet_a, triplet_b = broadcast_triplets(np.zeros((2, 3)), np.ones(3))
    pair_a, pair_b = broadcast_pairs(np.zeros((2, 2)), np.ones(2))

    assert triplet_a.shape == triplet_b.shape == (2, 3)
    assert pair_a.shape == pair_b.shape == (2, 2)


def test_split_last_axis():
    channels = split_last_axis(np.array([[1, 2, 3], [4, 5, 6]]))

    assert len(channels) == 3
    np.testing.assert_array_equal(channels[0], np.array([1, 4]))
    np.testing.assert_array_equal(channels[1], np.array([2, 5]))
    np.testing.assert_array_equal(channels[2], np.array([3, 6]))


def test_split_last_axis_rejects_scalar():
    with pytest.raises(ValueError, match="at least one axis"):
        split_last_axis(np.array(1.0))
