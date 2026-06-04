"""Tests for recovery method registries."""

from __future__ import annotations

import pytest

from color.recovery import (
    REFLECTANCE_RECOVERY_METHODS,
    SPECTRUM_RECOVERY_METHODS,
    resolve_reflectance_recovery_method,
    resolve_spectrum_recovery_method,
    solve_bounded_least_squares,
)


@pytest.mark.parametrize(
    "method",
    [
        "bounded_least_squares",
        "bounded least squares",
        "BoundedLeastSquares",
    ],
)
def test_spectrum_method_aliases(method: str) -> None:
    name, solver = resolve_spectrum_recovery_method(method)
    assert name == "bounded_least_squares"
    assert solver is solve_bounded_least_squares


@pytest.mark.parametrize(
    "method",
    [
        "bounded_least_squares",
        "bounded least squares",
        "BoundedLeastSquares",
    ],
)
def test_reflectance_method_aliases(method: str) -> None:
    name, solver = resolve_reflectance_recovery_method(method)
    assert name == "bounded_least_squares"
    assert solver is solve_bounded_least_squares


def test_recovery_method_registries_are_separate() -> None:
    assert SPECTRUM_RECOVERY_METHODS is not REFLECTANCE_RECOVERY_METHODS
    assert "bounded_least_squares" in SPECTRUM_RECOVERY_METHODS
    assert "bounded_least_squares" in REFLECTANCE_RECOVERY_METHODS


def test_unknown_recovery_method_raises() -> None:
    with pytest.raises(ValueError):
        resolve_spectrum_recovery_method("basis")
    with pytest.raises(ValueError):
        resolve_reflectance_recovery_method("basis")
