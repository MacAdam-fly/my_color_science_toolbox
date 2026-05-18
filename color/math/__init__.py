"""Numerical methods for fitting, interpolation, and simulation."""

from __future__ import annotations

from .extrapolation import Extrapolator, extrapolate_1d
from .interpolation import Interpolator, interpolate_1d, is_uniform, resolve_interpolator

__all__ = [
    "Interpolator",
    "Extrapolator",
    "interpolate_1d",
    "extrapolate_1d",
    "is_uniform",
    "resolve_interpolator",
]
