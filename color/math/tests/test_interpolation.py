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


@pytest.mark.parametrize(
    ("x", "y", "target", "expected"),
    [
        (
            np.arange(400, 461, 10, dtype=float),
            np.array([0.02, 0.05, 0.11, 0.22, 0.38, 0.55, 0.71]),
            np.array([405, 415, 425, 435, 445, 455], dtype=float),
            np.array(
                [
                    0.03296276913875598,
                    0.07463217703349283,
                    0.158046875,
                    0.296015625,
                    0.46565266148325357,
                    0.6310967404306221,
                ]
            ),
        ),
        (
            np.arange(0, 8, dtype=float),
            np.array([5.92, 9.37, 10.8135, 4.51, 69.59, 27.8007, 86.05, 42.0]),
            np.array([0, 0.25, 0.5, 0.75, 1.5, 3.2, 5.8, 7], dtype=float),
            np.array(
                [
                    5.9200000000001864,
                    6.729516121107766,
                    7.218502560556223,
                    7.8140625146017255,
                    12.235688333582534,
                    14.841160480000015,
                    77.13156897607655,
                    41.99999999999997,
                ]
            ),
        ),
        (
            np.arange(400, 461, 10, dtype=float),
            np.array([0.0, 0.1, 0.3, 0.6, 0.7, 1.0, 0.8]),
            np.array([400, 401, 409, 451, 459, 460], dtype=float),
            np.array(
                [
                    3.3306690738754696e-16,
                    0.008187619617224877,
                    0.08753824162679436,
                    1.0072386184210524,
                    0.8338759868421054,
                    0.80000000000000004,
                ]
            ),
        ),
    ],
)
def test_sprague_matches_fixed_reference_values(x, y, target, expected):
    result = interpolate_1d(x, y, target, method="sprague")
    np.testing.assert_allclose(result, expected, rtol=1e-12, atol=1e-12)
