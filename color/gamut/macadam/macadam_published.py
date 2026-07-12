"""Cached MacAdam optimal colour stimuli limits."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.spatial import ConvexHull

from color.colorimetry import XYZ_to_xy
from color.constants import A_XYZ, C_XYZ, D65_XYZ
from color.spaces.basic.lab import LCHab_to_Lab, Lab_to_XYZ
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
_STATIC_BOUNDARY_CACHE: dict[str, np.ndarray] = {}
STATIC_MACADAM_L_VALUES = np.arange(0.0, 101.0, 1.0)
STATIC_MACADAM_HUE_VALUES = np.arange(0.0, 361.0, 3.0)
_STATIC_BOUNDARY_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "gamut_data"


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


def _static_boundary_C_max(illuminant: str) -> np.ndarray:
    """Return the packaged L1/h3 boundary cache for an illuminant."""
    illuminant = _resolve_illuminant(illuminant)
    cached = _STATIC_BOUNDARY_CACHE.get(illuminant)
    if cached is not None:
        return cached

    path = _STATIC_BOUNDARY_DATA_DIR / f"MacAdamBoundary_{illuminant}_L1_H3.csv"
    values = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
    expected_rows = STATIC_MACADAM_L_VALUES.size * STATIC_MACADAM_HUE_VALUES.size
    if values.shape != (expected_rows, 3):
        raise ValueError(f"Invalid packaged MacAdam boundary cache: {path.name}")
    if not np.allclose(values[:, 0], np.repeat(STATIC_MACADAM_L_VALUES, STATIC_MACADAM_HUE_VALUES.size)):
        raise ValueError(f"Invalid L* grid in packaged MacAdam boundary cache: {path.name}")
    if not np.allclose(values[:, 1], np.tile(STATIC_MACADAM_HUE_VALUES, STATIC_MACADAM_L_VALUES.size)):
        raise ValueError(f"Invalid hue grid in packaged MacAdam boundary cache: {path.name}")
    C_max = values[:, 2].reshape(STATIC_MACADAM_L_VALUES.size, STATIC_MACADAM_HUE_VALUES.size)
    if not np.all(np.isfinite(C_max)) or np.any(C_max < 0.0):
        raise ValueError(f"Invalid chroma values in packaged MacAdam boundary cache: {path.name}")
    C_max.setflags(write=False)
    _STATIC_BOUNDARY_CACHE[illuminant] = C_max
    return C_max


def _static_grid_indices(values: np.ndarray, grid: np.ndarray, *, name: str) -> np.ndarray:
    """Return exact static-grid indices for requested values."""
    matches = [
        np.flatnonzero(np.isclose(grid, value, atol=1e-9, rtol=0.0))
        for value in values
    ]
    if any(index.size != 1 for index in matches):
        if name == "L_values":
            raise ValueError("published MacAdam data supports integer L_values in [0, 100]")
        raise ValueError("published MacAdam data supports hue_values in 3-degree steps")
    return np.array([int(index[0]) for index in matches], dtype=np.intp)


def macadam_limits_data(illuminant: str = "D65") -> dict[str, np.ndarray]:
    """Return the packaged MacAdam L1/h3 boundary samples."""
    illuminant = _resolve_illuminant(illuminant)
    L, h = np.meshgrid(STATIC_MACADAM_L_VALUES, STATIC_MACADAM_HUE_VALUES, indexing="ij")
    return {
        "L": L.reshape(-1),
        "h": h.reshape(-1),
        "C_max": _static_boundary_C_max(illuminant).reshape(-1).copy(),
    }


def macadam_limits_XYZ(illuminant: str = "D65") -> np.ndarray:
    """Return packaged MacAdam boundary samples as XYZ rows."""
    illuminant = _resolve_illuminant(illuminant)
    L, h = np.meshgrid(STATIC_MACADAM_L_VALUES, STATIC_MACADAM_HUE_VALUES, indexing="ij")
    LCHab = np.stack((L, _static_boundary_C_max(illuminant), h), axis=-1)
    return Lab_to_XYZ(
        LCHab_to_Lab(LCHab.reshape(-1, 3)),
        whitepoint_XYZ=_WHITEPOINTS_XYZ[illuminant],
    )


def macadam_limits_published_xy_boundary(illuminant: str = "D65") -> np.ndarray:
    """Return the published CIE xy-plane boundary of the MacAdam limits.

    Parameters
    ----------
    illuminant
        Published MacAdam illuminant name: ``"A"``, ``"C"`` or ``"D65"``.

    Returns
    -------
    ndarray
        Closed ``(n, 2)`` xy boundary polygon.

    Notes
    -----
    This boundary is the xy convex hull of the packaged L1/h3 boundary
    samples.

    Examples
    --------
    >>> macadam_limits_published_xy_boundary("D65").shape[1]
    2
    """
    XYZ = macadam_limits_XYZ(illuminant)
    positive = np.sum(XYZ, axis=1) > 1e-12
    return _convex_hull_polygon(XYZ_to_xy(XYZ[positive]))


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
    hue_values: Sequence[float] | np.ndarray = np.arange(0.0, 361.0, 3.0),
    C_upper: float = 300.0,
    iterations: int = 14,
    tolerance: float = 1e-9,
) -> MacAdamLimitsBoundary:
    """Return a regular LCHab boundary from packaged static MacAdam data.

    The A/C/D65 static source is defined on integer ``L*`` values and
    3-degree hue samples. Requests must use that grid or an exact subset;
    custom spectral conditions belong to the computed route.
    """
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

    L_indices = _static_grid_indices(L_array, STATIC_MACADAM_L_VALUES, name="L_values")
    hue_indices = _static_grid_indices(hue_array, STATIC_MACADAM_HUE_VALUES, name="hue_values")
    C_max = np.minimum(
        _static_boundary_C_max(illuminant)[np.ix_(L_indices, hue_indices)],
        C_upper,
    )

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
