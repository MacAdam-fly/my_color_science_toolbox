"""Numerical methods for fitting, interpolation, and simulation."""

from __future__ import annotations

from .extrapolation import Extrapolator, extrapolate_1d
from .interpolation import Interpolator, interpolate_1d, is_uniform, resolve_interpolator

__all__ = [
    "Interpolator",  # supported interpolation method name
    "Extrapolator",  # supported extrapolation method name
    "interpolate_1d",  # interpolate one-dimensional sampled data
    "extrapolate_1d",  # extrapolate one-dimensional sampled data
    "is_uniform",  # test whether sample positions are uniformly spaced
    "resolve_interpolator",  # normalize an interpolator name or object
]
