"""Convenience spectral conversions to XYZ and LMS responses."""

from __future__ import annotations

from typing import Union

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)

from .lms import emission_to_lms, reflectance_to_lms
from .spectral_responses import SpectralInput
from .xyz import emission_to_xyz, reflectance_to_xyz


ResponseSource = Union[str, MultiSpectralDistribution]
IlluminantSource = Union[str, SpectralDistribution]

DEFAULT_CMFS = "cie1931_xyz_1nm"
DEFAULT_FUNDAMENTALS = "cie2006_lms2_linE_1nm"
DEFAULT_ILLUMINANT = "D65"


def _load_cmfs(cmfs: ResponseSource) -> MultiSpectralDistribution:
    """Return XYZ colour matching functions from an object or dataset name."""
    if isinstance(cmfs, MultiSpectralDistribution):
        return cmfs
    return from_dataset("standard_observers.cmfs", cmfs)


def _load_fundamentals(
    fundamentals: ResponseSource,
    *,
    fill_nan: float | None,
) -> MultiSpectralDistribution:
    """Return cone fundamentals from an object or dataset name."""
    if isinstance(fundamentals, MultiSpectralDistribution):
        return fundamentals
    return from_dataset(
        "standard_observers.cone_fundamentals",
        fundamentals,
        fill_nan=fill_nan,
    )


def _load_illuminant(illuminant: IlluminantSource) -> SpectralDistribution:
    """Return an illuminant SPD from an object or dataset name."""
    if isinstance(illuminant, SpectralDistribution):
        return illuminant
    return from_dataset("illuminants", illuminant)


def emission_to_XYZ(
    emission: SpectralInput,
    *,
    cmfs: ResponseSource = "cie1931_xyz_1nm",
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert self-luminous spectral data to XYZ.

    By default, this uses ``standard_observers.cmfs/cie1931_xyz_1nm``.
    """
    return emission_to_xyz(emission, _load_cmfs(cmfs), shape=shape, k=k)


def reflectance_to_XYZ(
    reflectance: SpectralInput,
    *,
    illuminant: IlluminantSource = "D65",
    cmfs: ResponseSource = "cie1931_xyz_1nm",
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert reflectance data to XYZ.

    By default, this uses ``illuminants/D65`` and
    ``standard_observers.cmfs/cie1931_xyz_1nm``.
    """
    return reflectance_to_xyz(
        reflectance,
        _load_illuminant(illuminant),
        _load_cmfs(cmfs),
        shape=shape,
        k=k,
    )


def emission_to_LMS(
    emission: SpectralInput,
    *,
    fundamentals: ResponseSource = "cie2006_lms2_linE_1nm",
    shape: SpectralShape | None = None,
    k: float | None = None,
    fill_nan: float | None = 0.0,
) -> np.ndarray:
    """Convert self-luminous spectral data to LMS.

    By default, this uses
    ``standard_observers.cone_fundamentals/cie2006_lms2_linE_1nm`` with
    ``fill_nan=0.0``.
    """
    return emission_to_lms(
        emission,
        _load_fundamentals(fundamentals, fill_nan=fill_nan),
        shape=shape,
        k=k,
    )


def reflectance_to_LMS(
    reflectance: SpectralInput,
    *,
    illuminant: IlluminantSource = "D65",
    fundamentals: ResponseSource = "cie2006_lms2_linE_1nm",
    shape: SpectralShape | None = None,
    k: float | None = None,
    fill_nan: float | None = 0.0,
    normalisation_channel: str | int | None = None,
) -> np.ndarray:
    """Convert reflectance data to LMS.

    By default, this uses ``illuminants/D65`` and
    ``standard_observers.cone_fundamentals/cie2006_lms2_linE_1nm`` with
    ``fill_nan=0.0``.
    """
    return reflectance_to_lms(
        reflectance,
        _load_illuminant(illuminant),
        _load_fundamentals(fundamentals, fill_nan=fill_nan),
        shape=shape,
        k=k,
        normalisation_channel=normalisation_channel,
    )


__all__ = [
    "DEFAULT_CMFS",
    "DEFAULT_FUNDAMENTALS",
    "DEFAULT_ILLUMINANT",
    "emission_to_XYZ",
    "reflectance_to_XYZ",
    "emission_to_LMS",
    "reflectance_to_LMS",
]
