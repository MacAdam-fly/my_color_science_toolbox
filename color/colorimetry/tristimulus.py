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
    return integrate_responses(
        spd,
        cmfs,
        mode="emission",
        shape=shape,
        k=k,
    )


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
    """Integrate a self-luminous spectrum to CIE XYZ tristimulus values.

    Parameters
    ----------
    emission
        Emission SPD as a ``SpectralDistribution`` or
        ``MultiSpectralDistribution``.
    cmfs
        XYZ colour matching functions, either as a dataset name or a
        ``MultiSpectralDistribution`` with ``("X", "Y", "Z")`` labels.
    shape
        Optional spectral shape used to align the SPD and CMFs before
        integration.
    k
        Optional scale factor. If omitted, no photometric or ``Y=100``
        normalisation is applied.

    Returns
    -------
    ndarray
        XYZ values. Single-channel input returns ``(3,)``; multi-channel
        input returns ``(n, 3)``.

    Notes
    -----
    This is the self-luminous route. It integrates ``SPD * CMFs`` and does
    not automatically normalise the result to ``Y=100``. The output scale is
    determined by the SPD values, wavelength sampling and optional ``k``.

    Examples
    --------
    >>> from color.generators import blackbody_spd
    >>> from color.spectra import from_columns
    >>> sd = from_columns(blackbody_spd(temperature=6500), y="radiance")
    >>> emission_to_XYZ(sd).shape
    (3,)
    """
    return emission_to_xyz(
        emission,
        _load_cmfs(cmfs),
        shape=shape,
        k=k,
    )


def reflectance_to_XYZ(
    reflectance: SpectralInput,
    *,
    illuminant: IlluminantSource = DEFAULT_ILLUMINANT,
    cmfs: ResponseSource = DEFAULT_CMFS,
    shape: SpectralShape | None = None,
    k: float | None = None,
) -> np.ndarray:
    """Integrate a reflectance spectrum under an illuminant to CIE XYZ.

    Parameters
    ----------
    reflectance
        Reflectance factor spectrum as a ``SpectralDistribution`` or
        ``MultiSpectralDistribution``.
    illuminant
        Illuminant SPD, either as a dataset name such as ``"D65"`` or a
        ``SpectralDistribution``.
    cmfs
        XYZ colour matching functions, either as a dataset name or a
        ``MultiSpectralDistribution`` with ``("X", "Y", "Z")`` labels.
    shape
        Optional spectral shape used to align reflectance, illuminant and
        CMFs before integration.
    k
        Optional scale factor. If omitted, the normalisation factor is chosen
        so a perfect reflecting diffuser has ``Y=100``.

    Returns
    -------
    ndarray
        XYZ values on the project's usual ``Y=100`` reflectance reference
        scale. Single-channel input returns ``(3,)``; multi-channel input
        returns ``(n, 3)``.

    Notes
    -----
    This is the object-colour route. It integrates
    ``reflectance * illuminant * CMFs`` and normalises the reference white to
    ``Y=100`` unless ``k`` is explicitly supplied. The input reflectance
    object is not modified.

    Examples
    --------
    >>> from color.datasets import get_color_card
    >>> from color.spectra import from_columns
    >>> raw = get_color_card("pmc")
    >>> patch = from_columns(raw, y="Blue Sky")
    >>> reflectance_to_XYZ(patch, illuminant="D65").shape
    (3,)
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
