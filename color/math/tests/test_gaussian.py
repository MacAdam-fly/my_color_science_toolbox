"""Tests for Gaussian curve helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.math import gaussian_values, gaussian_values_from_fwhm, sigma_from_fwhm


def test_gaussian_values_matches_formula() -> None:
    x = np.array([0.0, 1.0, 2.0])
    result = gaussian_values(x, amplitude=2.0, center=1.0, sigma=0.5)
    expected = 2.0 * np.exp(-0.5 * ((x - 1.0) / 0.5) ** 2)

    np.testing.assert_allclose(result, expected)


def test_sigma_from_fwhm_matches_formula() -> None:
    fwhm = 50.0
    expected = fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    assert sigma_from_fwhm(fwhm) == pytest.approx(expected)


def test_gaussian_values_from_fwhm_matches_sigma_form() -> None:
    x = np.array([530.0, 555.0, 580.0])
    fwhm = 50.0

    result = gaussian_values_from_fwhm(x, amplitude=1.0, center=555.0, fwhm=fwhm)
    expected = gaussian_values(
        x,
        amplitude=1.0,
        center=555.0,
        sigma=sigma_from_fwhm(fwhm),
    )

    np.testing.assert_allclose(result, expected)
    assert result[1] == pytest.approx(1.0)
    assert result[0] == pytest.approx(0.5)
    assert result[2] == pytest.approx(0.5)


@pytest.mark.parametrize("sigma", [0.0, -1.0, np.inf, np.nan])
def test_gaussian_values_rejects_invalid_sigma(sigma: float) -> None:
    with pytest.raises(ValueError, match="sigma"):
        gaussian_values(np.array([0.0]), sigma=sigma)


@pytest.mark.parametrize("fwhm", [0.0, -1.0, np.inf, np.nan])
def test_sigma_from_fwhm_rejects_invalid_fwhm(fwhm: float) -> None:
    with pytest.raises(ValueError, match="fwhm"):
        sigma_from_fwhm(fwhm)
