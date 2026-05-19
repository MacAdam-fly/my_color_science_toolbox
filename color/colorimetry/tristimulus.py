"""XYZ tristimulus value computations from spectral data."""

from __future__ import annotations

from typing import Union

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)

from .integration import SpectralInput, _validate_responses, integrate_responses


ResponseSource = Union[str, MultiSpectralDistribution]
IlluminantSource = Union[str, SpectralDistribution]

DEFAULT_CMFS = "cie1931_xyz_1nm"
DEFAULT_ILLUMINANT = "D65"


def _load_cmfs(cmfs: ResponseSource) -> MultiSpectralDistribution:
    """Return XYZ colour matching functions from an object or dataset name."""
    if isinstance(cmfs, MultiSpectralDistribution):
        return cmfs
    return from_dataset("standard_observers.cmfs", cmfs)


def _load_illuminant(illuminant: IlluminantSource) -> SpectralDistribution:
    """Return an illuminant SPD from an object or dataset name."""
    if isinstance(illuminant, SpectralDistribution):
        return illuminant
    return from_dataset("illuminants", illuminant)


def emission_to_xyz(
    spd: SpectralInput,
    cmfs: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert self-luminous spectral data to XYZ tristimulus values."""
    _validate_responses(cmfs, expected_labels=("X", "Y", "Z"))
    return integrate_responses(spd, cmfs, mode="emission", shape=shape, k=k)


def reflectance_to_xyz(
    reflectance: SpectralInput,
    illuminant: SpectralDistribution,
    cmfs: MultiSpectralDistribution,
    *,
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Convert reflectance data under an illuminant to XYZ tristimulus values."""
    _validate_responses(cmfs, expected_labels=("X", "Y", "Z"))
    return integrate_responses(
        reflectance,
        cmfs,
        mode="reflectance",
        illuminant=illuminant,
        shape=shape,
        k=k,
        normalisation_channel="Y",
    )


def emission_to_XYZ(
    emission: SpectralInput,
    *,
    cmfs: ResponseSource = DEFAULT_CMFS,
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
    illuminant: IlluminantSource = DEFAULT_ILLUMINANT,
    cmfs: ResponseSource = DEFAULT_CMFS,
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


__all__ = [
    "DEFAULT_CMFS",
    "DEFAULT_ILLUMINANT",
    "emission_to_xyz",
    "reflectance_to_xyz",
    "emission_to_XYZ",
    "reflectance_to_XYZ",
]
