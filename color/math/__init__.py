"""Numerical methods for fitting, interpolation, and simulation."""

from __future__ import annotations

from .extrapolation import Extrapolator, extrapolate_1d
from .gaussian import gaussian_values, gaussian_values_from_fwhm, sigma_from_fwhm
from .interpolation import Interpolator, interpolate_1d, is_uniform, resolve_interpolator

__all__ = [
    "Interpolator",  # supported interpolation method name
    "interpolate_1d",  # interpolate one-dimensional sampled data
    "is_uniform",  # test whether sample positions are uniformly spaced
    "resolve_interpolator",  # normalize an interpolator name or object
]

__all__ += [
    "Extrapolator",  # supported extrapolation method name
    "extrapolate_1d",  # extrapolate one-dimensional sampled data
]

__all__ += [
    "gaussian_values",  # evaluate a Gaussian curve
    "gaussian_values_from_fwhm",  # evaluate a Gaussian curve from FWHM width
    "sigma_from_fwhm",  # convert Gaussian FWHM to standard deviation
]
