"""Reflectance recovery from colour stimuli."""

from __future__ import annotations

from .matrix import reflectance_recovery_matrix, response_recovery_matrix
from .library import ReflectanceLibrary, load_reflectance_library
from .methods import (
    REFLECTANCE_RECOVERY_METHODS,
    SPECTRUM_RECOVERY_METHODS,
    resolve_reflectance_recovery_method,
    resolve_spectrum_recovery_method,
)
from .options import (
    AutoGaussianRecoveryOptions,
    BoundedLeastSquaresOptions,
    Burns2019RecoveryOptions,
    DictionaryReflectanceOptions,
    GaussianRecoveryOptions,
    Meng2015RecoveryOptions,
    MultiGaussianRecoveryOptions,
    PCAReflectanceOptions,
)
from .reflectance import recover_reflectance_from_XYZ, recover_reflectance_from_xyY
from .solvers import second_difference_matrix, solve_bounded_least_squares
from .spectrum import (
    recover_spectrum_from_LMS,
    recover_spectrum_from_responses,
    recover_spectrum_from_XYZ,
    recover_spectrum_from_xyY,
)

__all__ = [
    "recover_spectrum_from_responses",  # recover an effective spectrum from any three-channel responses
    "recover_spectrum_from_XYZ",  # recover an effective spectrum from XYZ values
    "recover_spectrum_from_xyY",  # recover an effective spectrum from xyY values
    "recover_spectrum_from_LMS",  # recover an effective spectrum from LMS responses
]

__all__ += [
    "recover_reflectance_from_XYZ",  # recover bounded smooth reflectance from XYZ
    "recover_reflectance_from_xyY",  # recover bounded smooth reflectance from xyY
]

__all__ += [
    "ReflectanceLibrary",  # aligned reflectance sample matrix for recovery methods
    "load_reflectance_library",  # load UEF reflectance datasets as one library
]

__all__ += [
    "BoundedLeastSquaresOptions",  # options for bounded smooth least-squares recovery
    "GaussianRecoveryOptions",  # options for single-Gaussian spectrum recovery
    "MultiGaussianRecoveryOptions",  # options for multi-Gaussian spectrum recovery
    "AutoGaussianRecoveryOptions",  # options for automatic Gaussian spectrum recovery
    "Burns2019RecoveryOptions",  # options for Burns 2019 reflectance recovery
    "Meng2015RecoveryOptions",  # options for Meng 2015 reflectance recovery
    "PCAReflectanceOptions",  # options for PCA reflectance recovery
    "DictionaryReflectanceOptions",  # options for dictionary reflectance recovery
]

__all__ += [
    "response_recovery_matrix",  # build the spectrum-to-response linear matrix
    "reflectance_recovery_matrix",  # build the reflectance-to-XYZ linear matrix
    "second_difference_matrix",  # build the smoothness regularisation matrix
    "solve_bounded_least_squares",  # shared bounded smooth least-squares solver
]

__all__ += [
    "SPECTRUM_RECOVERY_METHODS",  # registered effective-spectrum recovery methods
    "REFLECTANCE_RECOVERY_METHODS",  # registered reflectance recovery methods
    "resolve_spectrum_recovery_method",  # resolve an effective-spectrum recovery method
    "resolve_reflectance_recovery_method",  # resolve a reflectance recovery method
]
