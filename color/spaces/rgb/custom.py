"""Custom three-primary RGB colour-space constructors."""

from __future__ import annotations

from collections.abc import Sequence
import warnings

import numpy as np

from .colourspace import RGBColorSpace, RGBTransfer, _readonly_array
from .transfer import normalize_transfer


def _as_primaries_xy(value: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    primaries = np.asarray(value, dtype=np.float64)
    if primaries.shape != (3, 2):
        raise ValueError(f"primaries_xy must have shape (3, 2), got {primaries.shape}")
    if not np.all(np.isfinite(primaries)):
        raise ValueError("primaries_xy must be finite")
    if np.any(primaries[:, 1] <= 0):
        raise ValueError("primary y chromaticity values must be positive")
    return primaries


def _as_xyz_triplet(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    xyz = np.asarray(value, dtype=np.float64)
    if xyz.shape != (3,):
        raise ValueError(f"{name} must have shape (3,), got {xyz.shape}")
    if not np.all(np.isfinite(xyz)):
        raise ValueError(f"{name} must be finite")
    if xyz[1] <= 0:
        raise ValueError(f"{name} Y value must be positive")
    return xyz


def _whitepoint_from_xy(value: Sequence[float] | np.ndarray) -> np.ndarray:
    white_xy = np.asarray(value, dtype=np.float64)
    if white_xy.shape != (2,):
        raise ValueError(f"whitepoint_xy must have shape (2,), got {white_xy.shape}")
    if not np.all(np.isfinite(white_xy)):
        raise ValueError("whitepoint_xy must be finite")
    x, y = white_xy
    if y <= 0:
        raise ValueError("whitepoint_xy y value must be positive")
    return np.array([100.0 * x / y, 100.0, 100.0 * (1.0 - x - y) / y], dtype=np.float64)


def _xy_from_XYZ(value: np.ndarray, *, name: str) -> np.ndarray:
    denom = np.sum(value, axis=-1)
    if np.any(denom <= 0):
        raise ValueError(f"{name} XYZ values must have a positive X + Y + Z sum")
    return value[..., :2] / denom[..., None]


def _warn_if_non_Y100(whitepoint_XYZ: np.ndarray) -> None:
    """Warn when a custom RGB whitepoint is outside the project Y=100 domain."""
    if not np.isclose(whitepoint_XYZ[1], 100.0, rtol=1e-6, atol=1e-6):
        warnings.warn(
            "custom RGB colour-space whitepoint Y is not 100; RGB conversions will preserve "
            "the measured XYZ scale. Gamut calculations remain self-consistent, but spaces "
            "workflows usually expect the project Y=100 reference domain.",
            UserWarning,
            stacklevel=3,
        )


def _matrix_from_primaries_xy(primaries_xy: np.ndarray, whitepoint_XYZ: np.ndarray) -> np.ndarray:
    x = primaries_xy[:, 0]
    y = primaries_xy[:, 1]
    primary_matrix = np.array(
        [
            x / y,
            np.ones(3),
            (1.0 - x - y) / y,
        ],
        dtype=np.float64,
    )
    try:
        scales = np.linalg.solve(primary_matrix, whitepoint_XYZ)
    except np.linalg.LinAlgError as exc:
        raise ValueError("primaries_xy form a singular RGB to XYZ matrix") from exc
    if not np.all(np.isfinite(scales)) or np.any(scales <= 0):
        raise ValueError("whitepoint is not representable by positive RGB primary scales")
    return primary_matrix * scales[np.newaxis, :]


def _readonly_space(
    *,
    name: str,
    primaries_xy: np.ndarray,
    whitepoint_XYZ: np.ndarray,
    matrix_RGB_to_XYZ: np.ndarray,
    transfer: RGBTransfer,
    aliases: Sequence[str],
    white_name: str,
    reference: str,
) -> RGBColorSpace:
    try:
        matrix_XYZ_to_RGB = np.linalg.inv(matrix_RGB_to_XYZ)
    except np.linalg.LinAlgError as exc:
        raise ValueError("RGB to XYZ matrix is singular") from exc

    return RGBColorSpace(
        name=str(name),
        aliases=tuple(str(alias) for alias in aliases),
        primaries=_readonly_array(primaries_xy, shape=(3, 2), name="primaries"),
        white_xy=_readonly_array(_xy_from_XYZ(whitepoint_XYZ, name="whitepoint_XYZ"), shape=(2,), name="white_xy"),
        white_name=str(white_name),
        transfer=normalize_transfer(transfer),
        matrix_RGB_to_XYZ=_readonly_array(matrix_RGB_to_XYZ, shape=(3, 3), name="matrix_RGB_to_XYZ"),
        matrix_XYZ_to_RGB=_readonly_array(matrix_XYZ_to_RGB, shape=(3, 3), name="matrix_XYZ_to_RGB"),
        reference=str(reference),
    )


def RGB_colourspace_from_primaries_xy(
    name: str,
    primaries_xy: Sequence[Sequence[float]] | np.ndarray,
    *,
    whitepoint_xy: Sequence[float] | np.ndarray | None = None,
    whitepoint_XYZ: Sequence[float] | np.ndarray | None = None,
    transfer: RGBTransfer = "linear",
    aliases: Sequence[str] = (),
    white_name: str = "custom",
    reference: str = "",
) -> RGBColorSpace:
    """Create a three-primary RGB colour space from primary xy coordinates."""
    primaries = _as_primaries_xy(primaries_xy)
    if whitepoint_xy is None and whitepoint_XYZ is None:
        raise ValueError("either whitepoint_xy or whitepoint_XYZ must be provided")
    if whitepoint_xy is not None and whitepoint_XYZ is not None:
        raise ValueError("whitepoint_xy and whitepoint_XYZ cannot both be provided")

    if whitepoint_XYZ is None:
        white_XYZ = _whitepoint_from_xy(whitepoint_xy)  # type: ignore[arg-type]
    else:
        white_XYZ = _as_xyz_triplet(whitepoint_XYZ, name="whitepoint_XYZ")
        _warn_if_non_Y100(white_XYZ)

    matrix_RGB_to_XYZ = _matrix_from_primaries_xy(primaries, white_XYZ)
    return _readonly_space(
        name=name,
        primaries_xy=primaries,
        whitepoint_XYZ=white_XYZ,
        matrix_RGB_to_XYZ=matrix_RGB_to_XYZ,
        transfer=transfer,
        aliases=aliases,
        white_name=white_name,
        reference=reference,
    )


def RGB_colourspace_from_primaries_XYZ(
    name: str,
    primaries_XYZ: Sequence[Sequence[float]] | np.ndarray,
    *,
    transfer: RGBTransfer = "linear",
    aliases: Sequence[str] = (),
    white_name: str = "measured",
    reference: str = "",
    warn_if_non_Y100: bool = True,
) -> RGBColorSpace:
    """Create a three-primary RGB colour space from measured primary XYZ values."""
    primaries = np.asarray(primaries_XYZ, dtype=np.float64)
    if primaries.shape != (3, 3):
        raise ValueError(f"primaries_XYZ must have shape (3, 3), got {primaries.shape}")
    if not np.all(np.isfinite(primaries)):
        raise ValueError("primaries_XYZ must be finite")
    if np.any(np.sum(primaries, axis=1) <= 0):
        raise ValueError("each primary XYZ row must have a positive X + Y + Z sum")

    white_XYZ = np.sum(primaries, axis=0)
    if white_XYZ[1] <= 0:
        raise ValueError("summed primary whitepoint Y value must be positive")
    if warn_if_non_Y100:
        _warn_if_non_Y100(white_XYZ)

    return _readonly_space(
        name=name,
        primaries_xy=_xy_from_XYZ(primaries, name="primaries_XYZ"),
        whitepoint_XYZ=white_XYZ,
        matrix_RGB_to_XYZ=primaries.T,
        transfer=transfer,
        aliases=aliases,
        white_name=white_name,
        reference=reference,
    )


__all__ = [
    "RGB_colourspace_from_primaries_xy",
    "RGB_colourspace_from_primaries_XYZ",
]
