"""Cached MacAdam optimal colour stimuli limits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.spatial import ConvexHull

from color.constants import A_XYZ, C_XYZ, D65_XYZ
from color.datasets.gamut_data import get_gamut_data
from color.utils.arrays import as_last_axis_triplets
from color.utils.names import canonical_method_name

from ..boundary import GamutBoundary, _as_1d_values, _convex_hull_polygon


_ILLUMINANTS = {
    "a": "A",
    "c": "C",
    "d65": "D65",
}

_WHITEPOINTS_XYZ = {
    "A": A_XYZ,
    "C": C_XYZ,
    "D65": D65_XYZ,
}

_HULL_EQUATIONS_CACHE: dict[str, np.ndarray] = {}


def _resolve_illuminant(illuminant: str) -> str:
    """Return the canonical supported MacAdam illuminant name."""
    key = canonical_method_name(illuminant)
    resolved = _ILLUMINANTS.get(key)
    if resolved is None:
        raise ValueError("illuminant must be one of 'A', 'C' or 'D65'")
    return resolved


def _hull_equations(illuminant: str) -> np.ndarray:
    """Return cached convex-hull equations for a MacAdam limits dataset."""
    illuminant = _resolve_illuminant(illuminant)
    equations = _HULL_EQUATIONS_CACHE.get(illuminant)
    if equations is None:
        equations = ConvexHull(macadam_limits_XYZ(illuminant)).equations
        _HULL_EQUATIONS_CACHE[illuminant] = equations
    return equations


def macadam_limits_data(illuminant: str = "D65") -> dict[str, np.ndarray]:
    """Return cached MacAdam optimal colour stimuli data."""
    illuminant = _resolve_illuminant(illuminant)
    return get_gamut_data(f"macadam_limits_{illuminant}")


def macadam_limits_XYZ(illuminant: str = "D65") -> np.ndarray:
    """Return cached MacAdam optimal colour stimuli vertices as XYZ rows."""
    data = macadam_limits_data(illuminant)
    return np.stack((data["X"], data["Y"], data["Z"]), axis=-1)


def macadam_limits_published_xy_boundary(illuminant: str = "D65") -> np.ndarray:
    """Return the published CIE xy-plane boundary of the MacAdam limits."""
    data = macadam_limits_data(illuminant)
    positive = data["Y"] > 1e-12
    xy = np.stack((data["x"][positive], data["y"][positive]), axis=-1)
    return _convex_hull_polygon(xy)


def _resample_chroma_by_hue(
    h: np.ndarray,
    C: np.ndarray,
    hue_values: np.ndarray,
) -> np.ndarray:
    """Return a nearest-envelope chroma sampled at target hues."""
    if h.size == 0:
        return np.zeros_like(hue_values, dtype=np.float64)
    h = np.mod(h, 360.0)
    C = np.asarray(C, dtype=np.float64)
    result = np.empty_like(hue_values, dtype=np.float64)
    if hue_values.size > 1:
        diffs = np.diff(np.sort(np.unique(np.mod(hue_values, 360.0))))
        half_width = max(float(np.min(diffs)) / 2.0 if diffs.size else 1.0, 0.5)
    else:
        half_width = 1.0

    for index, hue in enumerate(np.mod(hue_values, 360.0)):
        distance = np.abs(((h - hue + 180.0) % 360.0) - 180.0)
        mask = distance <= half_width
        if np.any(mask):
            result[index] = float(np.max(C[mask]))
        else:
            result[index] = float(C[np.argmin(distance)])
    return result


@dataclass(frozen=True)
class MacAdamLimitsBoundary(GamutBoundary):
    """Cached MacAdam optimal colour stimuli boundary."""

    illuminant: str = "D65"
    vertices_XYZ: np.ndarray | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        illuminant = _resolve_illuminant(self.illuminant)
        vertices = (
            macadam_limits_XYZ(illuminant)
            if self.vertices_XYZ is None
            else np.array(self.vertices_XYZ, dtype=np.float64, copy=True)
        )
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("vertices_XYZ must have shape (n, 3)")
        if vertices.shape[0] < 4:
            raise ValueError("vertices_XYZ must contain at least four vertices")
        if not np.all(np.isfinite(vertices)):
            raise ValueError("vertices_XYZ must be finite")
        vertices.setflags(write=False)
        object.__setattr__(self, "illuminant", illuminant)
        object.__setattr__(self, "vertices_XYZ", vertices)

    def xy_boundary(self) -> np.ndarray:
        """Return the cached MacAdam xy-plane boundary."""
        return macadam_limits_published_xy_boundary(self.illuminant)


def _inside_macadam_mesh(
    XYZ: Sequence[float] | np.ndarray,
    *,
    illuminant: str,
    tolerance: float,
    equations: np.ndarray | None = None,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside the MacAdam mesh."""
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    hull_equations = _hull_equations(illuminant) if equations is None else equations
    flat = xyz.reshape(-1, 3)
    inside = np.all(
        flat @ hull_equations[:, :3].T + hull_equations[:, 3] <= tolerance,
        axis=1,
    )
    inside = inside.reshape(xyz.shape[:-1])
    return inside[()] if inside.shape == () else inside


def is_within_macadam_limits(
    XYZ: Sequence[float] | np.ndarray,
    illuminant: str = "D65",
    *,
    tolerance: float = 1e-9,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside the cached MacAdam limits."""
    illuminant = _resolve_illuminant(illuminant)
    return _inside_macadam_mesh(
        XYZ,
        illuminant=illuminant,
        tolerance=tolerance,
    )


def macadam_limits(
    illuminant: str = "D65",
    *,
    L_values: Sequence[float] | np.ndarray = np.arange(0.0, 101.0, 1.0),
    hue_values: Sequence[float] | np.ndarray = np.arange(0.0, 361.0, 1.0),
    C_upper: float = 300.0,
    iterations: int = 14,
    tolerance: float = 1e-9,
) -> MacAdamLimitsBoundary:
    """Return cached MacAdam limits resampled as a regular LCHab boundary."""
    illuminant = _resolve_illuminant(illuminant)
    whitepoint = _WHITEPOINTS_XYZ[illuminant]
    L_array = _as_1d_values(L_values, name="L_values")
    hue_array = _as_1d_values(hue_values, name="hue_values")

    C_upper = float(C_upper)
    if not np.isfinite(C_upper) or C_upper <= 0:
        raise ValueError("C_upper must be a finite positive value")
    if int(iterations) != iterations or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    data = macadam_limits_data(illuminant)
    source_L = np.sort(np.unique(data["L"]))
    source_C = np.vstack([
        _resample_chroma_by_hue(
            data["h"][np.isclose(data["L"], L)],
            data["C"][np.isclose(data["L"], L)],
            hue_array,
        )
        for L in source_L
    ])
    C_max = np.vstack([
        np.array([
            np.interp(L, source_L, source_C[:, hue_index])
            for hue_index in range(hue_array.size)
        ])
        for L in L_array
    ])
    C_max = np.minimum(C_max, C_upper)

    return MacAdamLimitsBoundary(
        C_max=C_max,
        L_values=L_array,
        hue_values=hue_array,
        whitepoint_XYZ=whitepoint,
        primaries=None,
        illuminant=illuminant,
        vertices_XYZ=macadam_limits_XYZ(illuminant),
    )


__all__ = [
    "MacAdamLimitsBoundary",
    "macadam_limits_data",
    "macadam_limits_XYZ",
    "macadam_limits_published_xy_boundary",
    "macadam_limits",
    "is_within_macadam_limits",
]
