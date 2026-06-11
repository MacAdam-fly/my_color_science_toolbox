"""Pointer real-surface colour gamut utilities."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.datasets.gamut_data import get_gamut_data

from .boundary import GamutBoundary
from .mesh import is_within_mesh_volume


_POINTER_GAMUT_BOUNDARY_XY_REFERENCE = np.array(
    [
        [0.659, 0.316],
        [0.634, 0.351],
        [0.594, 0.391],
        [0.557, 0.427],
        [0.523, 0.462],
        [0.482, 0.491],
        [0.444, 0.515],
        [0.409, 0.546],
        [0.371, 0.558],
        [0.332, 0.573],
        [0.288, 0.584],
        [0.242, 0.576],
        [0.202, 0.530],
        [0.177, 0.454],
        [0.151, 0.389],
        [0.151, 0.330],
        [0.162, 0.295],
        [0.157, 0.266],
        [0.159, 0.245],
        [0.142, 0.214],
        [0.141, 0.195],
        [0.129, 0.168],
        [0.138, 0.141],
        [0.145, 0.129],
        [0.145, 0.106],
        [0.161, 0.094],
        [0.188, 0.084],
        [0.252, 0.104],
        [0.324, 0.127],
        [0.393, 0.165],
        [0.451, 0.199],
        [0.508, 0.226],
    ],
    dtype=np.float64,
)


def pointer_gamut_data() -> dict[str, np.ndarray]:
    """Return Pointer real-surface gamut data from the dataset registry."""
    return get_gamut_data("pointer")


def pointer_gamut_whitepoint_XYZ() -> np.ndarray:
    """Return Pointer gamut reference white tristimulus values."""
    data = pointer_gamut_data()
    return np.array([data["Xn"][0], data["Yn"][0], data["Zn"][0]], dtype=np.float64)


def pointer_gamut_LCHab() -> np.ndarray:
    """Return Pointer gamut boundary rows as ``(L*, C*, h)``."""
    data = pointer_gamut_data()
    return np.stack((data["L"], data["C"], data["hab"]), axis=-1)


def pointer_gamut_published_xy_boundary() -> np.ndarray:
    """Return Pointer's published CIE 1931 xy-plane boundary.

    Parameters
    ----------
    None

    Returns
    -------
    ndarray
        Closed ``(n, 2)`` xy boundary polygon.

    Notes
    -----
    Pointer data is tabulated as several L* slices. This helper computes the
    xy boundary directly in the xy plane, avoiding Lab/LCHab projection
    artefacts. The boundary follows the 32-point Pointer xy boundary used by
    ``colour``.

    Examples
    --------
    >>> pointer_gamut_published_xy_boundary().shape[1]
    2
    """
    boundary = _POINTER_GAMUT_BOUNDARY_XY_REFERENCE.copy()
    return np.vstack((boundary, boundary[0]))


class PointerGamutBoundary(GamutBoundary):
    """Pointer real-surface gamut boundary.

    Notes
    -----
    Pointer is an empirical object-colour gamut, not a display-primary gamut.
    Its ``xy_boundary()`` returns the published xy boundary rather than a
    primary hull.
    """

    def xy_boundary(self) -> np.ndarray:
        """Return Pointer's published CIE xy-plane boundary."""
        return pointer_gamut_published_xy_boundary()


def pointer_gamut() -> PointerGamutBoundary:
    """Return Pointer real-surface gamut as a ``GamutBoundary``.

    Parameters
    ----------
    None

    Returns
    -------
    PointerGamutBoundary
        Regular ``L* x hue`` boundary built from the registered Pointer data.

    Notes
    -----
    The returned boundary can be used with Lab volume, projected boundary and
    coverage helpers. It has no display primaries.

    Examples
    --------
    >>> pointer = pointer_gamut()
    >>> pointer.primaries is None
    True
    """
    data = pointer_gamut_data()
    L_values = np.unique(data["L"])
    hue_values = np.unique(data["hab"])
    C_max = np.empty((L_values.size, hue_values.size), dtype=np.float64)

    for L_index, L in enumerate(L_values):
        for hue_index, hue in enumerate(hue_values):
            mask = (data["L"] == L) & (data["hab"] == hue)
            if np.count_nonzero(mask) != 1:
                raise ValueError("Pointer gamut data must be a regular L*/hue grid")
            C_max[L_index, hue_index] = data["C"][mask][0]

    return PointerGamutBoundary(
        C_max=C_max,
        L_values=L_values,
        hue_values=hue_values,
        whitepoint_XYZ=pointer_gamut_whitepoint_XYZ(),
        primaries=None,
    )


def pointer_gamut_XYZ() -> np.ndarray:
    """Return Pointer gamut boundary vertices as XYZ rows."""
    return pointer_gamut().to_XYZ().reshape(-1, 3)


def is_within_pointer_gamut(
    XYZ: Sequence[float] | np.ndarray,
    *,
    tolerance: float = 1e-9,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside Pointer's real-surface gamut.

    Parameters
    ----------
    XYZ
        XYZ values with final-axis shape ``(..., 3)`` in project ``Y=100``
        scale.
    tolerance
        Non-negative mesh tolerance.

    Returns
    -------
    bool or ndarray
        Inside mask matching the leading shape of ``XYZ``.

    Notes
    -----
    The test uses the Pointer boundary mesh, not display primary feasibility.

    Examples
    --------
    >>> bool(is_within_pointer_gamut([0.0, 0.0, 0.0])) in {True, False}
    True
    """
    return is_within_mesh_volume(XYZ, pointer_gamut_XYZ(), tolerance=tolerance)


__all__ = [
    "PointerGamutBoundary",
    "pointer_gamut_whitepoint_XYZ",
    "pointer_gamut_data",
    "pointer_gamut_LCHab",
    "pointer_gamut_published_xy_boundary",
    "pointer_gamut",
    "pointer_gamut_XYZ",
    "is_within_pointer_gamut",
]
