"""Core chromatic adaptation helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.constants.illuminants_XYZ import D65_XYZ
from color.utils.arrays import as_last_axis_triplets
from color.utils.names import canonical_method_name

from .matrices import CHROMATIC_ADAPTATION_TRANSFORMS


def _as_whitepoint(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite positive XYZ whitepoint."""
    white = np.asarray(value, dtype=np.float64)
    if white.shape != (3,):
        raise ValueError(f"{name} must contain exactly 3 values")
    if not np.all(np.isfinite(white)):
        raise ValueError(f"{name} must be finite")
    if np.any(white <= 0):
        raise ValueError(f"{name} values must be positive")
    return white


def _canonical_transform(transform: str | None) -> str | None:
    """Return the canonical transform name."""
    if transform is None:
        return None
    if not isinstance(transform, str):
        raise TypeError("transform must be a string or None")

    key = canonical_method_name(transform)
    aliases = {
        "vonkries": "Von Kries",
        "bradford": "Bradford",
        "cat02": "CAT02",
        "cat16": "CAT16",
    }
    if key not in aliases:
        names = ", ".join(CHROMATIC_ADAPTATION_TRANSFORMS)
        raise ValueError(
            f"unknown chromatic adaptation transform {transform!r}; "
            f"expected one of: {names}"
        )
    return aliases[key]


def _canonical_zhai_transform(transform: str) -> str:
    """Return the canonical transform name supported by Zhai 2018."""
    canonical = _canonical_transform(transform)
    if canonical not in {"CAT02", "CAT16"}:
        raise ValueError(
            "Zhai 2018 chromatic adaptation supports only 'CAT02' and 'CAT16' "
            "response transforms."
        )
    return canonical


def matrix_chromatic_adaptation_von_kries(
    source_white_XYZ: Sequence[float] | np.ndarray,
    target_white_XYZ: Sequence[float] | np.ndarray,
    *,
    transform: str | None = "Bradford",
) -> np.ndarray:
    """Return a Von Kries-style chromatic adaptation matrix.

    Parameters
    ----------
    source_white_XYZ, target_white_XYZ
        Positive XYZ whitepoints on the same numeric scale.
    transform
        Chromatic adaptation transform name: ``"Von Kries"``,
        ``"Bradford"``, ``"CAT02"``, ``"CAT16"`` or ``None``.

    Returns
    -------
    ndarray
        ``(3, 3)`` matrix mapping source-white XYZ to target-white XYZ using
        row-vector application ``XYZ @ matrix.T``.

    Notes
    -----
    ``transform=None`` returns the identity matrix. This function adapts
    reference whites; it does not convert numeric scale such as
    ``[0, 1] <-> Y=100``.
    """
    canonical = _canonical_transform(transform)
    if canonical is None:
        return np.identity(3, dtype=np.float64)

    source_white = _as_whitepoint(source_white_XYZ, name="source_white_XYZ")
    target_white = _as_whitepoint(target_white_XYZ, name="target_white_XYZ")

    matrix = CHROMATIC_ADAPTATION_TRANSFORMS[canonical]
    source_cone = source_white @ matrix.T
    target_cone = target_white @ matrix.T
    scale = target_cone / source_cone

    return np.linalg.inv(matrix) @ np.diag(scale) @ matrix


def chromatic_adaptation_XYZ(
    XYZ: Sequence[float] | np.ndarray,
    source_white_XYZ: Sequence[float] | np.ndarray,
    target_white_XYZ: Sequence[float] | np.ndarray,
    *,
    transform: str | None = "Bradford",
) -> np.ndarray:
    """Adapt XYZ values from a source whitepoint to a target whitepoint.

    Parameters
    ----------
    XYZ
        XYZ values with final axis length 3.
    source_white_XYZ, target_white_XYZ
        Positive XYZ whitepoints on the same numeric scale.
    transform
        Von Kries-style transform name or ``None``.

    Returns
    -------
    ndarray
        Adapted XYZ values with the same leading shape as ``XYZ``.

    Notes
    -----
    This is an explicit adaptation step. It is not RGB transfer, not a colour
    space conversion formula, and not scale conversion.
    """
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    matrix = matrix_chromatic_adaptation_von_kries(
        source_white_XYZ,
        target_white_XYZ,
        transform=transform,
    )
    return xyz @ matrix.T


def chromatic_adaptation_Zhai2018(
    XYZ: Sequence[float] | np.ndarray,
    source_white_XYZ: Sequence[float] | np.ndarray,
    target_white_XYZ: Sequence[float] | np.ndarray,
    *,
    D_source: Sequence[float] | np.ndarray | float = 1.0,
    D_target: Sequence[float] | np.ndarray | float = 1.0,
    baseline_white_XYZ: Sequence[float] | np.ndarray | None = None,
    transform: str = "CAT02",
) -> np.ndarray:
    """Adapt XYZ values with the Zhai and Luo 2018 two-step CAT model.

    Parameters
    ----------
    XYZ
        XYZ values under ``source_white_XYZ`` with final axis length 3.
    source_white_XYZ, target_white_XYZ
        Positive source and target whitepoints on the same numeric scale as
        ``XYZ``.
    D_source, D_target
        Degree of adaptation for the source and target illuminants, normally
        in ``[0, 1]``. Scalars and broadcastable arrays are accepted.
    baseline_white_XYZ
        Equal-energy baseline illuminant. If omitted, an equal-energy
        whitepoint with the source whitepoint's ``Y`` scale is used.
    transform
        Response transform used by the two-step model: ``"CAT02"`` or
        ``"CAT16"``.

    Returns
    -------
    ndarray
        XYZ values adapted to ``target_white_XYZ``.

    Notes
    -----
    Zhai 2018 is not a replacement for ``transform="Bradford"`` style
    one-step adaptation. It is a higher-level two-step model that itself uses
    a CAT02 or CAT16 response transform and explicit adaptation degrees.
    """
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    source_white = _as_whitepoint(source_white_XYZ, name="source_white_XYZ")
    target_white = _as_whitepoint(target_white_XYZ, name="target_white_XYZ")
    if baseline_white_XYZ is None:
        baseline_white = np.full(3, source_white[1], dtype=np.float64)
    else:
        baseline_white = _as_whitepoint(baseline_white_XYZ, name="baseline_white_XYZ")

    D_source_array = np.asarray(D_source, dtype=np.float64)
    D_target_array = np.asarray(D_target, dtype=np.float64)
    if not np.all(np.isfinite(D_source_array)):
        raise ValueError("D_source must contain only finite values.")
    if not np.all(np.isfinite(D_target_array)):
        raise ValueError("D_target must contain only finite values.")
    if np.any((D_source_array < 0) | (D_source_array > 1)):
        raise ValueError("D_source must be in the [0, 1] interval.")
    if np.any((D_target_array < 0) | (D_target_array > 1)):
        raise ValueError("D_target must be in the [0, 1] interval.")

    canonical = _canonical_zhai_transform(transform)
    matrix = CHROMATIC_ADAPTATION_TRANSFORMS[canonical]

    source_Y = source_white[1]
    target_Y = target_white[1]
    baseline_Y = baseline_white[1]

    RGB = xyz @ matrix.T
    RGB_source_white = source_white @ matrix.T
    RGB_target_white = target_white @ matrix.T
    RGB_baseline_white = baseline_white @ matrix.T

    D_source_rgb = (
        D_source_array[..., None]
        * (source_Y / baseline_Y)
        * (RGB_baseline_white / RGB_source_white)
        + 1.0
        - D_source_array[..., None]
    )
    D_target_rgb = (
        D_target_array[..., None]
        * (target_Y / baseline_Y)
        * (RGB_baseline_white / RGB_target_white)
        + 1.0
        - D_target_array[..., None]
    )
    RGB_target = (D_source_rgb / D_target_rgb) * RGB
    inverse = np.linalg.inv(matrix)
    return RGB_target @ inverse.T


def adapt_to_D65(
    XYZ: Sequence[float] | np.ndarray,
    source_white_XYZ: Sequence[float] | np.ndarray,
    *,
    transform: str | None = "Bradford",
) -> np.ndarray:
    """Adapt XYZ values from ``source_white_XYZ`` to the D65 whitepoint."""
    return chromatic_adaptation_XYZ(
        XYZ,
        source_white_XYZ=source_white_XYZ,
        target_white_XYZ=D65_XYZ,
        transform=transform,
    )


def adapt_from_D65(
    XYZ_D65_referred: Sequence[float] | np.ndarray,
    target_white_XYZ: Sequence[float] | np.ndarray,
    *,
    transform: str | None = "Bradford",
) -> np.ndarray:
    """Adapt D65-referred XYZ values to ``target_white_XYZ``."""
    return chromatic_adaptation_XYZ(
        XYZ_D65_referred,
        source_white_XYZ=D65_XYZ,
        target_white_XYZ=target_white_XYZ,
        transform=transform,
    )


__all__ = [
    "matrix_chromatic_adaptation_von_kries",
    "chromatic_adaptation_XYZ",
    "chromatic_adaptation_Zhai2018",
    "adapt_to_D65",
    "adapt_from_D65",
]
