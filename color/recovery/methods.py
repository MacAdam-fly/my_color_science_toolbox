"""Recovery method registries."""

from __future__ import annotations

from color.utils.methods import build_method_index, resolve_method

from .solvers import solve_bounded_least_squares


SPECTRUM_RECOVERY_METHODS = {
    "bounded_least_squares": solve_bounded_least_squares,
}

REFLECTANCE_RECOVERY_METHODS = {
    "bounded_least_squares": solve_bounded_least_squares,
}

_METHOD_ALIASES = {
    "bounded_least_squares": (
        "bounded least squares",
        "BoundedLeastSquares",
        "boundedlsq",
    ),
}

_SPECTRUM_METHOD_INDEX = build_method_index(_METHOD_ALIASES)
_REFLECTANCE_METHOD_INDEX = build_method_index(_METHOD_ALIASES)


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
