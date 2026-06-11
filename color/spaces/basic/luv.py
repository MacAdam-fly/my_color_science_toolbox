"""CIE 1976 Luv, LCHuv and Lshuv colour-space helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.utils.arrays import as_last_axis_triplets

from .lab import DEFAULT_WHITEPOINT_XYZ, EPSILON, KAPPA
from ..node import ColorSpaceNode


def _as_whitepoint(whitepoint_XYZ: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return a valid reference whitepoint XYZ triplet."""
    whitepoint = np.asarray(whitepoint_XYZ, dtype=np.float64)
    if whitepoint.shape != (3,):
        raise ValueError("whitepoint_XYZ must have shape (3,)")
    if not np.all(np.isfinite(whitepoint)):
        raise ValueError("whitepoint_XYZ must be finite")
    if np.any(whitepoint <= 0):
        raise ValueError("whitepoint_XYZ values must be positive")
    return whitepoint


def _uv_prime(XYZ: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return CIE 1976 u' and v' coordinates from XYZ values."""
    denominator = XYZ[..., 0] + 15.0 * XYZ[..., 1] + 3.0 * XYZ[..., 2]
    u = np.zeros_like(denominator, dtype=np.float64)
    v = np.zeros_like(denominator, dtype=np.float64)
    nonzero = denominator != 0
    np.divide(4.0 * XYZ[..., 0], denominator, out=u, where=nonzero)
    np.divide(9.0 * XYZ[..., 1], denominator, out=v, where=nonzero)
    return u, v


def XYZ_to_Luv(
    XYZ: Sequence[float] | np.ndarray,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XYZ,
) -> np.ndarray:
    """Convert CIE XYZ values to CIE 1976 Luv values.

    ``XYZ`` and ``whitepoint_XYZ`` must share the same numeric scale, normally
    the project Y=100 scale. The final axis must contain ``X, Y, Z`` and batch
    dimensions are preserved.

    Parameters
    ----------
    XYZ
        XYZ tristimulus values with final axis ``(X, Y, Z)``.
    whitepoint_XYZ
        Reference whitepoint in the same numeric scale as ``XYZ``.

    Returns
    -------
    numpy.ndarray
        Luv values with final axis ``(L*, u*, v*)``.

    Notes
    -----
    The default whitepoint is the project D65 XYZ whitepoint on the Y=100
    scale. Luv uses CIE 1976 ``u'v'`` chromaticity relative to that whitepoint.

    Examples
    --------
    >>> XYZ_to_Luv([19.01, 20.0, 21.78]).shape
    (3,)
    """
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    whitepoint = _as_whitepoint(whitepoint_XYZ)

    y_r = xyz[..., 1] / whitepoint[1]
    L = np.where(y_r > EPSILON, 116.0 * np.cbrt(y_r) - 16.0, KAPPA * y_r)
    u_prime, v_prime = _uv_prime(xyz)
    u_n, v_n = _uv_prime(whitepoint)

    u = 13.0 * L * (u_prime - u_n)
    v = 13.0 * L * (v_prime - v_n)
    return np.stack((L, u, v), axis=-1)


def Luv_to_XYZ(
    Luv: Sequence[float] | np.ndarray,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XYZ,
) -> np.ndarray:
    """Convert CIE 1976 Luv values to CIE XYZ values.

    The returned XYZ values use the numeric scale of ``whitepoint_XYZ``. Use the
    same whitepoint that was used for the forward Luv conversion to preserve a
    round-trip.

    Parameters
    ----------
    Luv
        Luv values with final axis ``(L*, u*, v*)``.
    whitepoint_XYZ
        Reference whitepoint that sets the output XYZ scale.

    Returns
    -------
    numpy.ndarray
        XYZ tristimulus values with final axis ``(X, Y, Z)``.

    Notes
    -----
    This inverse does not infer the original whitepoint; callers must pass the
    same reference whitepoint used by ``XYZ_to_Luv`` when that matters.

    Examples
    --------
    >>> Luv_to_XYZ([51.837, -0.097, 2.782]).shape
    (3,)
    """
    luv = as_last_axis_triplets(Luv, name="Luv")
    whitepoint = _as_whitepoint(whitepoint_XYZ)

    L = luv[..., 0]
    Y = np.where(
        L > KAPPA * EPSILON,
        whitepoint[1] * ((L + 16.0) / 116.0) ** 3,
        whitepoint[1] * L / KAPPA,
    )

    u_n, v_n = _uv_prime(whitepoint)
    nonzero_L = L != 0
    u_prime = np.broadcast_to(u_n, L.shape).astype(np.float64, copy=True)
    v_prime = np.broadcast_to(v_n, L.shape).astype(np.float64, copy=True)
    np.divide(luv[..., 1], 13.0 * L, out=u_prime, where=nonzero_L)
    np.divide(luv[..., 2], 13.0 * L, out=v_prime, where=nonzero_L)
    u_prime += np.where(nonzero_L, u_n, 0.0)
    v_prime += np.where(nonzero_L, v_n, 0.0)

    X = np.zeros_like(Y, dtype=np.float64)
    Z = np.zeros_like(Y, dtype=np.float64)
    nonzero_v = v_prime != 0
    np.divide(9.0 * Y * u_prime, 4.0 * v_prime, out=X, where=nonzero_v)
    np.divide(
        Y * (12.0 - 3.0 * u_prime - 20.0 * v_prime),
        4.0 * v_prime,
        out=Z,
        where=nonzero_v,
    )
    return np.stack((X, Y, Z), axis=-1)


def Luv_to_LCHuv(Luv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE 1976 Luv values to cylindrical LCHuv values.

    The output final axis is ``L*, C*uv, h_uv`` with hue in degrees on
    ``[0, 360)``. Batch dimensions are preserved.

    Notes
    -----
    This is a cylindrical coordinate transform inside Luv; no whitepoint or XYZ
    conversion is involved.
    """
    luv = as_last_axis_triplets(Luv, name="Luv")
    C = np.hypot(luv[..., 1], luv[..., 2])
    h = np.mod(np.degrees(np.arctan2(luv[..., 2], luv[..., 1])), 360.0)
    return np.stack((luv[..., 0], C, h), axis=-1)


def LCHuv_to_Luv(LCHuv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert cylindrical LCHuv values to CIE 1976 Luv values.

    The input final axis is ``L*, C*uv, h_uv`` with hue in degrees. Batch
    dimensions are preserved and the returned final axis is ``L*, u*, v*``.

    Notes
    -----
    This is the inverse cylindrical transform for ``Luv_to_LCHuv``.
    """
    lch = as_last_axis_triplets(LCHuv, name="LCHuv")
    h = np.radians(lch[..., 2])
    u = lch[..., 1] * np.cos(h)
    v = lch[..., 1] * np.sin(h)
    return np.stack((lch[..., 0], u, v), axis=-1)


def Luv_to_Lshuv(Luv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIE 1976 Luv values to Lshuv saturation coordinates.

    The output final axis is ``L*, s_uv, h_uv`` where saturation is computed as
    ``C*uv / L*`` and hue is in degrees on ``[0, 360)``.

    Notes
    -----
    ``L*=0`` maps to zero saturation to avoid division by zero.
    """
    luv = as_last_axis_triplets(Luv, name="Luv")
    L = luv[..., 0]
    C = np.hypot(luv[..., 1], luv[..., 2])
    s = np.divide(C, L, out=np.zeros_like(C), where=L != 0)
    h = np.mod(np.degrees(np.arctan2(luv[..., 2], luv[..., 1])), 360.0)
    return np.stack((L, s, h), axis=-1)


def Lshuv_to_Luv(Lshuv: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert Lshuv saturation coordinates to CIE 1976 Luv values.

    The input final axis is ``L*, s_uv, h_uv`` with hue in degrees. Chroma is
    reconstructed as ``L* * s_uv`` before converting back to ``u*, v*``.

    Notes
    -----
    This transform is a Luv-family coordinate change and does not involve XYZ or
    a reference whitepoint.
    """
    lsh = as_last_axis_triplets(Lshuv, name="Lshuv")
    h = np.radians(lsh[..., 2])
    C = lsh[..., 0] * lsh[..., 1]
    u = C * np.cos(h)
    v = C * np.sin(h)
    return np.stack((lsh[..., 0], u, v), axis=-1)


SPACE_NODES = (
    ColorSpaceNode(
        name="Luv",
        aliases=("CIE Luv", "CIELUV"),
        to_XYZ=Luv_to_XYZ,
        from_XYZ=XYZ_to_Luv,
        family="Luv",
    ),
    ColorSpaceNode(
        name="LCHuv",
        aliases=("CIE LCHuv", "CIELCHuv", "LChuv"),
        parent="Luv",
        to_parent=LCHuv_to_Luv,
        from_parent=Luv_to_LCHuv,
        family="Luv",
    ),
    ColorSpaceNode(
        name="Lshuv",
        aliases=("CIE Lshuv", "CIELshuv", "LShuv", "Lsh"),
        parent="Luv",
        to_parent=Lshuv_to_Luv,
        from_parent=Luv_to_Lshuv,
        family="Luv",
    ),
)


__all__ = [
    "DEFAULT_WHITEPOINT_XYZ",
    "XYZ_to_Luv",
    "Luv_to_XYZ",
    "Luv_to_LCHuv",
    "LCHuv_to_Luv",
    "Luv_to_Lshuv",
    "Lshuv_to_Luv",
    "SPACE_NODES",
]
