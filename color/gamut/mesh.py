"""Generic 3D mesh-volume inside tests."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.spatial import Delaunay

from color.utils.arrays import as_last_axis_triplets


def _as_vertices_XYZ(vertices_XYZ: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    """Return finite 3D mesh vertices."""
    vertices = np.array(vertices_XYZ, dtype=np.float64, copy=True)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("vertices_XYZ must have shape (n, 3)")
    if vertices.shape[0] < 4:
        raise ValueError("vertices_XYZ must contain at least four vertices")
    if not np.all(np.isfinite(vertices)):
        raise ValueError("vertices_XYZ must be finite")
    if np.linalg.matrix_rank(vertices - vertices[0]) < 3:
        raise ValueError("vertices_XYZ must span a three-dimensional volume")
    return vertices


def is_within_mesh_volume(
    XYZ: Sequence[float] | np.ndarray,
    vertices_XYZ: Sequence[Sequence[float]] | np.ndarray,
    *,
    tolerance: float = 1e-9,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside the volume defined by vertices."""
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    vertices = _as_vertices_XYZ(vertices_XYZ)
    triangulation = Delaunay(vertices)
    flat = xyz.reshape(-1, 3)
    inside = triangulation.find_simplex(flat, tol=tolerance) >= 0
    inside = inside.reshape(xyz.shape[:-1])
    return inside[()] if inside.shape == () else inside


__all__ = ["is_within_mesh_volume"]
