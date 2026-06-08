"""Recovery method registries."""

from __future__ import annotations

from color.utils.methods import build_method_index, resolve_method

from .dictionary import solve_dictionary_reflectance
from .meng2015 import solve_meng2015_reflectance
from .pca import solve_pca_reflectance
from .solvers import solve_bounded_least_squares


SPECTRUM_RECOVERY_METHODS = {
    "bounded_least_squares": solve_bounded_least_squares,
}

REFLECTANCE_RECOVERY_METHODS = {
    "bounded_least_squares": solve_bounded_least_squares,
    "dictionary": solve_dictionary_reflectance,
    "meng2015": solve_meng2015_reflectance,
    "pca": solve_pca_reflectance,
}

_SPECTRUM_METHOD_ALIASES = {
    "bounded_least_squares": (
        "bounded least squares",
        "BoundedLeastSquares",
        "boundedlsq",
    ),
}

_REFLECTANCE_METHOD_ALIASES = {
    **_SPECTRUM_METHOD_ALIASES,
    "dictionary": (
        "dict",
        "convex_dictionary",
        "dictionary recovery",
    ),
    "meng2015": (
        "Meng 2015",
        "Meng et al. 2015",
        "Meng",
    ),
    "pca": (
        "PCA",
        "principal_components",
        "principal component analysis",
    ),
}

_SPECTRUM_METHOD_INDEX = build_method_index(_SPECTRUM_METHOD_ALIASES)
_REFLECTANCE_METHOD_INDEX = build_method_index(_REFLECTANCE_METHOD_ALIASES)


def resolve_spectrum_recovery_method(method: str):
    """Resolve a spectrum recovery method name to a solver."""
    return resolve_method(method, _SPECTRUM_METHOD_INDEX, SPECTRUM_RECOVERY_METHODS)


def resolve_reflectance_recovery_method(method: str):
    """Resolve a reflectance recovery method name to a solver."""
    return resolve_method(
        method,
        _REFLECTANCE_METHOD_INDEX,
        REFLECTANCE_RECOVERY_METHODS,
    )


__all__ = [
    "SPECTRUM_RECOVERY_METHODS",
    "REFLECTANCE_RECOVERY_METHODS",
    "resolve_spectrum_recovery_method",
    "resolve_reflectance_recovery_method",
]
