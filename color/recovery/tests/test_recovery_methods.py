"""Tests for recovery method registries."""

from __future__ import annotations

import pytest

from color.recovery.burns2019 import solve_burns2019_reflectance
from color.recovery.dictionary import solve_dictionary_reflectance
from color.recovery.methods import (
    REFLECTANCE_RECOVERY_METHODS,
    SPECTRUM_RECOVERY_METHODS,
    resolve_reflectance_recovery_method,
    resolve_spectrum_recovery_method,
)
from color.recovery.meng2015 import solve_meng2015_reflectance
from color.recovery.pca import solve_pca_reflectance
from color.recovery.solvers import solve_bounded_least_squares


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
    assert "auto_gaussian" in SPECTRUM_RECOVERY_METHODS
    assert "auto_gaussian" not in REFLECTANCE_RECOVERY_METHODS
    assert "burns2019" not in SPECTRUM_RECOVERY_METHODS
    assert "burns2019" in REFLECTANCE_RECOVERY_METHODS
    assert "dictionary" not in SPECTRUM_RECOVERY_METHODS
    assert "dictionary" in REFLECTANCE_RECOVERY_METHODS
    assert "gaussian" in SPECTRUM_RECOVERY_METHODS
    assert "gaussian" not in REFLECTANCE_RECOVERY_METHODS
    assert "meng2015" not in SPECTRUM_RECOVERY_METHODS
    assert "meng2015" in REFLECTANCE_RECOVERY_METHODS
    assert "multi_gaussian" in SPECTRUM_RECOVERY_METHODS
    assert "multi_gaussian" not in REFLECTANCE_RECOVERY_METHODS
    assert "pca" not in SPECTRUM_RECOVERY_METHODS
    assert "pca" in REFLECTANCE_RECOVERY_METHODS


@pytest.mark.parametrize(
    "method",
    [
        "dictionary",
        "dict",
        "convex_dictionary",
        "dictionary recovery",
    ],
)
def test_reflectance_dictionary_method_aliases(method: str) -> None:
    name, solver = resolve_reflectance_recovery_method(method)
    assert name == "dictionary"
    assert solver is solve_dictionary_reflectance


@pytest.mark.parametrize(
    "method",
    [
        "burns2019",
        "Burns 2019",
        "Burns",
        "smoothest_bounded",
        "smoothest bounded",
    ],
)
def test_reflectance_burns2019_method_aliases(method: str) -> None:
    name, solver = resolve_reflectance_recovery_method(method)
    assert name == "burns2019"
    assert solver is solve_burns2019_reflectance


@pytest.mark.parametrize(
    "method",
    [
        "pca",
        "PCA",
        "principal_components",
        "principal component analysis",
    ],
)
def test_reflectance_pca_method_aliases(method: str) -> None:
    name, solver = resolve_reflectance_recovery_method(method)
    assert name == "pca"
    assert solver is solve_pca_reflectance


@pytest.mark.parametrize(
    "method",
    [
        "meng2015",
        "Meng 2015",
        "Meng et al. 2015",
        "Meng",
    ],
)
def test_reflectance_meng2015_method_aliases(method: str) -> None:
    name, solver = resolve_reflectance_recovery_method(method)
    assert name == "meng2015"
    assert solver is solve_meng2015_reflectance


def test_unknown_recovery_method_raises() -> None:
    with pytest.raises(ValueError):
        resolve_spectrum_recovery_method("burns2019")
    with pytest.raises(ValueError):
        resolve_spectrum_recovery_method("pca")
    with pytest.raises(ValueError):
        resolve_spectrum_recovery_method("dictionary")
    with pytest.raises(ValueError):
        resolve_spectrum_recovery_method("meng2015")
    with pytest.raises(ValueError):
        resolve_reflectance_recovery_method("basis")
