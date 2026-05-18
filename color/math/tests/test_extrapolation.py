"""Tests for extrapolation helpers."""

from __future__ import annotations

import numpy as np

from color.math import extrapolate_1d


def test_constant_extrapolate_1d():
    result = extrapolate_1d(
        np.array([400, 500]),
        np.array([0.0, 1.0]),
        np.array([350, 450, 550]),
        interpolator="linear",
        method="constant",
    )
    np.testing.assert_allclose(result, [0.0, 0.5, 1.0])


def test_fill_extrapolate_1d():
    result = extrapolate_1d(
        np.array([400, 500]),
        np.array([0.0, 1.0]),
        np.array([350, 450, 550]),
        interpolator="linear",
        method="fill",
        fill_value=-1.0,
    )
    np.testing.assert_allclose(result, [-1.0, 0.5, -1.0])


def test_linear_extrapolate_1d():
    result = extrapolate_1d(
        np.array([400, 500]),
        np.array([0.0, 1.0]),
        np.array([350, 450, 550]),
        interpolator="linear",
        method="linear",
    )
    np.testing.assert_allclose(result, [-0.5, 0.5, 1.5])


def test_left_right_override_extrapolate_1d():
    result = extrapolate_1d(
        np.array([400, 500]),
        np.array([0.0, 1.0]),
        np.array([350, 450, 550]),
        interpolator="linear",
        method="constant",
        left=-2.0,
        right=2.0,
    )
    np.testing.assert_allclose(result, [-2.0, 0.5, 2.0])
