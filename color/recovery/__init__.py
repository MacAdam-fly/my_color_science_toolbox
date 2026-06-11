"""Reflectance recovery from colour stimuli."""

from __future__ import annotations

from .library import ReflectanceLibrary, load_reflectance_library
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

