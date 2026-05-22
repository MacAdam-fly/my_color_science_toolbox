"""Tests for explicit scale conversion utilities."""

from __future__ import annotations

import numpy as np
import pytest

from color.utils.scale import (
    from_range_1,
    from_range_100,
    from_range_degrees,
    to_domain_1,
    to_domain_100,
    to_domain_degrees,
)


def test_to_domain_1_from_100():
    np.testing.assert_allclose(to_domain_1([0.0, 50.0, 100.0]), [0.0, 0.5, 1.0])


def test_to_domain_100_from_1():
    np.testing.assert_allclose(to_domain_100([0.0, 0.5, 1.0]), [0.0, 50.0, 100.0])


def test_from_range_1_to_100():
    np.testing.assert_allclose(from_range_1([0.0, 0.5, 1.0]), [0.0, 50.0, 100.0])


def test_from_range_100_to_1():
    np.testing.assert_allclose(from_range_100([0.0, 50.0, 100.0]), [0.0, 0.5, 1.0])


def test_reference_scale_is_no_op_copy():
    value = np.array([1.0, 2.0, 3.0])
    result = to_domain_100(value, source_scale="reference")
    np.testing.assert_allclose(result, value)
    assert result is not value


def test_scale_factor_can_broadcast():
    value = np.array([[1.0, 2.0, 3.0]])
    np.testing.assert_allclose(
        to_domain_100(value, scale_factor=[10.0, 100.0, 1000.0]),
        [[10.0, 200.0, 3000.0]],
    )


def test_angle_scale_conversions():
    np.testing.assert_allclose(to_domain_degrees([0.0, 0.5, 1.0]), [0.0, 180.0, 360.0])
    np.testing.assert_allclose(
        from_range_degrees([0.0, 180.0, 360.0]),
        [0.0, 0.5, 1.0],
    )
    np.testing.assert_allclose(
        to_domain_degrees([0.0, 50.0, 100.0], source_scale="100"),
        [0.0, 180.0, 360.0],
    )
    np.testing.assert_allclose(
        from_range_degrees([0.0, 180.0, 360.0], target_scale="100"),
        [0.0, 50.0, 100.0],
    )


def test_scalar_input_returns_numpy_scalar():
    assert np.asarray(to_domain_1(50.0)).shape == ()
    assert to_domain_1(50.0) == pytest.approx(0.5)


def test_aliases_are_supported():
    assert to_domain_1(50.0, source_scale="percent") == pytest.approx(0.5)
    assert to_domain_100(0.5, source_scale="normalized") == pytest.approx(50.0)
    assert from_range_degrees(180.0, target_scale="percent") == pytest.approx(50.0)


def test_invalid_scale_raises():
    with pytest.raises(ValueError, match="scale must be"):
        to_domain_1(1.0, source_scale="unknown")


def test_non_finite_values_raise():
    with pytest.raises(ValueError, match="value must be finite"):
        to_domain_1([1.0, np.nan])
