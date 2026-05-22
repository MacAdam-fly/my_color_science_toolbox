"""Core chromatic adaptation helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.constants.illuminants_XYZ import D65_XYZ
from color.utils.arrays import as_last_axis_triplets
from color.utils.methods import canonical_method_name

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


def matrix_chromatic_adaptation_von_kries(
    source_white_XYZ: Sequence[float] | np.ndarray,
    target_white_XYZ: Sequence[float] | np.ndarray,
    *,
    transform: str | None = "Bradford",
) -> np.ndarray:
    """Return a Von Kries style chromatic adaptation matrix."""
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
    """Adapt XYZ values from a source whitepoint to a target whitepoint."""
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    matrix = matrix_chromatic_adaptation_von_kries(
        source_white_XYZ,
        target_white_XYZ,
        transform=transform,
    )
    return xyz @ matrix.T


def adapt_to_D65(
    XYZ: Sequence[float] | np.ndarray,
    source_white_XYZ: Sequence[float] | np.ndarray,
    *,
    transform: str | None = "Bradford",
) -> np.ndarray:
    """Adapt XYZ values from *source_white_XYZ* to the D65 whitepoint."""
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
    """Adapt D65-referred XYZ values to *target_white_XYZ*."""
    return chromatic_adaptation_XYZ(
        XYZ_D65_referred,
        source_white_XYZ=D65_XYZ,
        target_white_XYZ=target_white_XYZ,
        transform=transform,
    )


__all__ = [
    "matrix_chromatic_adaptation_von_kries",
    "chromatic_adaptation_XYZ",
    "adapt_to_D65",
    "adapt_from_D65",
]
