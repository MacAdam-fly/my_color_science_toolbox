"""Tests for interpolation helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.math import interpolate_1d, is_uniform, resolve_interpolator

pytestmark = pytest.mark.filterwarnings(
    "ignore:.*deprecated.*:pyparsing.exceptions.PyparsingDeprecationWarning"
)


def test_is_uniform():
    assert is_uniform(np.array([400, 410, 420]))
    assert not is_uniform(np.array([400, 410, 425]))


def test_resolve_interpolator():
    assert resolve_interpolator(np.arange(6), "auto") == "sprague"
    assert resolve_interpolator(np.array([0, 1, 2, 4]), "auto") == "cubic"
    assert resolve_interpolator(np.array([0, 1, 2]), "auto") == "linear"
    assert resolve_interpolator(np.arange(6), "pchip") == "pchip"
    assert resolve_interpolator(np.arange(6), "nearest") == "nearest"
    assert resolve_interpolator(np.arange(6), "linear") == "linear"


def test_linear_interpolate_1d():
    result = interpolate_1d(
        np.array([400, 500]),
        np.array([0.0, 1.0]),
        np.array([425, 450, 475]),
        method="linear",
    )
    np.testing.assert_allclose(result, [0.25, 0.5, 0.75])


def test_interpolate_1d_rejects_out_of_bounds_by_default():
    with pytest.raises(ValueError, match="outside"):
        interpolate_1d(
            np.array([400, 500]),
            np.array([0.0, 1.0]),
            np.array([350, 450]),
        )


def test_interpolate_1d_fill_value():
    result = interpolate_1d(
        np.array([400, 500]),
        np.array([0.0, 1.0]),
        np.array([350, 400, 550]),
        method="linear",
        bounds_error=False,
        fill_value=-1.0,
    )
    np.testing.assert_allclose(result, [-1.0, 0.0, -1.0])


def test_nearest_interpolate_1d():
    result = interpolate_1d(
        np.array([400, 500, 600]),
        np.array([0.0, 1.0, 2.0]),
        np.array([425, 475, 525]),
        method="nearest",
    )
    np.testing.assert_allclose(result, [0.0, 1.0, 1.0])


def test_pchip_interpolate_1d():
    result = interpolate_1d(
        np.array([400, 500, 600]),
        np.array([0.0, 1.0, 0.0]),
        np.array([450, 550]),
        method="pchip",
    )
    np.testing.assert_allclose(result, [0.75, 0.75])


def test_cubic_requires_enough_samples():
    with pytest.raises(ValueError, match="cubic interpolation requires"):
        interpolate_1d(
            np.array([400, 500, 600]),
            np.array([0.0, 1.0, 0.0]),
            np.array([450, 550]),
            method="cubic",
        )


def test_sprague_requires_uniform_samples():
    with pytest.raises(ValueError, match="uniform"):
        interpolate_1d(
            np.array([400, 410, 420, 435, 450, 460]),
            np.array([0.0, 0.1, 0.3, 0.6, 0.7, 1.0]),
            np.array([415, 425]),
            method="sprague",
        )


def test_sprague_interpolates_uniform_samples():
    result = interpolate_1d(
        np.array([400, 410, 420, 430, 440, 450], dtype=float),
        np.array([0.0, 0.1, 0.3, 0.6, 0.7, 1.0], dtype=float),
        np.array([415, 425], dtype=float),
        method="sprague",
    )
    assert result.shape == (2,)
    assert np.all(np.isfinite(result))
