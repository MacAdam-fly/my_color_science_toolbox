"""Tests for sampled-data quadrature helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.math import integrate_samples, quadrature_weights


def test_quadrature_weights_rectangle_and_trapezoid() -> None:
    wavelengths = np.array([400.0, 500.0, 600.0])

    np.testing.assert_allclose(
        quadrature_weights(wavelengths, interval=100.0, quadrature="rectangle"),
        [100.0, 100.0, 100.0],
    )
    np.testing.assert_allclose(
        quadrature_weights(wavelengths, interval=100.0, quadrature="trapezoid"),
        [50.0, 100.0, 50.0],
    )


def test_integrate_samples_rectangle_and_trapezoid() -> None:
    wavelengths = np.array([400.0, 500.0, 600.0])
    values = np.array([1.0, 2.0, 3.0])

    assert integrate_samples(
        values,
        wavelengths,
        interval=100.0,
        quadrature="rectangle",
    ) == pytest.approx(600.0)
    assert integrate_samples(
        values,
        wavelengths,
        interval=100.0,
        quadrature="trapezoid",
    ) == pytest.approx(400.0)


def test_invalid_quadrature_raises() -> None:
    wavelengths = np.array([400.0, 500.0, 600.0])

    with pytest.raises(ValueError, match="unsupported quadrature"):
        quadrature_weights(wavelengths, quadrature="simpson")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="unsupported quadrature"):
        integrate_samples(
            np.ones(3),
            wavelengths,
            quadrature="simpson",  # type: ignore[arg-type]
        )
