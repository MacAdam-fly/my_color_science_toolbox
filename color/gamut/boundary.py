"""LCH gamut-boundary computation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.spatial import ConvexHull

from color.colorimetry import XYZ_to_xy
from color.spaces.basic.lab import Lab_to_LCHab, LCHab_to_Lab, Lab_to_XYZ

from .primaries import DisplayPrimaries, as_display_primaries
from .solvers import is_within_primary_gamut


def _as_1d_values(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return finite non-empty one-dimensional values."""
    values = np.asarray(value, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must be finite")
    return np.array(values, dtype=np.float64, copy=True)


def _polygon_area(points: np.ndarray) -> float:
    """Return the area of a 2D polygon using the shoelace formula."""
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if points.shape[0] < 3:
        raise ValueError("points must contain at least three vertices")
    if not np.all(np.isfinite(points)):
        raise ValueError("points must be finite")
    x = points[:, 0]
    y = points[:, 1]
    return float(0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def _convex_hull_polygon(points: np.ndarray) -> np.ndarray:
    """Return finite 2D convex-hull vertices closed as a polygon."""
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if points.shape[0] < 3:
        raise ValueError("points must contain at least three rows")
    if not np.all(np.isfinite(points)):
        raise ValueError("points must be finite")
    hull = ConvexHull(points)
    polygon = points[hull.vertices]
    return np.vstack([polygon, polygon[0]])


@dataclass(frozen=True)
class GamutBoundary:
    """Computed LCHab gamut boundary."""

    C_max: np.ndarray
    L_values: np.ndarray
    hue_values: np.ndarray
    whitepoint_XYZ: np.ndarray
    primaries: DisplayPrimaries | None = None

    def __post_init__(self) -> None:
        c_max = np.array(self.C_max, dtype=np.float64, copy=True)
        L_values = _as_1d_values(self.L_values, name="L_values")
        hue_values = _as_1d_values(self.hue_values, name="hue_values")
        if c_max.shape != (L_values.size, hue_values.size):
            raise ValueError("C_max shape must match (len(L_values), len(hue_values))")
        if not np.all(np.isfinite(c_max)) or np.any(c_max < 0):
            raise ValueError("C_max must be finite and non-negative")
        whitepoint = np.array(self.whitepoint_XYZ, dtype=np.float64, copy=True)
        if whitepoint.shape != (3,) or not np.all(np.isfinite(whitepoint)):
            raise ValueError("whitepoint_XYZ must be a finite triplet")
        if np.any(whitepoint <= 0):
            raise ValueError("whitepoint_XYZ values must be positive")
        c_max.setflags(write=False)
        L_values.setflags(write=False)
        hue_values.setflags(write=False)
        whitepoint.setflags(write=False)
        object.__setattr__(self, "C_max", c_max)
        object.__setattr__(self, "L_values", L_values)
        object.__setattr__(self, "hue_values", hue_values)
        object.__setattr__(self, "whitepoint_XYZ", whitepoint)
        primaries = None if self.primaries is None else as_display_primaries(self.primaries)
        object.__setattr__(self, "primaries", primaries)

    def to_LCHab(self) -> np.ndarray:
        """Return boundary points as ``(L, C, h)`` rows."""
        L_grid, hue_grid = np.meshgrid(self.L_values, self.hue_values, indexing="ij")
        return np.stack((L_grid, self.C_max, hue_grid), axis=-1)

    def to_Lab(self) -> np.ndarray:
        """Return boundary points as Lab rows."""
        return LCHab_to_Lab(self.to_LCHab())

    def to_XYZ(self) -> np.ndarray:
        """Return boundary points as XYZ rows."""
        return Lab_to_XYZ(self.to_Lab(), whitepoint_XYZ=self.whitepoint_XYZ)

    def primary_xy_hull(self) -> np.ndarray:
        """Return the exact primary chromaticity hull in CIE xy coordinates."""
        if self.primaries is None:
            raise ValueError("primary_xy_hull requires display primaries")
        return _convex_hull_polygon(XYZ_to_xy(self.primaries.primaries_XYZ))

    def slice_L(self, L: float) -> np.ndarray:
        """Return an interpolated LCHab boundary slice at lightness *L*."""
        L = float(L)
        if not np.isfinite(L):
            raise ValueError("L must be finite")
        if L < self.L_values[0] or L > self.L_values[-1]:
            raise ValueError("L is outside the boundary L_values range")
        C = np.array([
            np.interp(L, self.L_values, self.C_max[:, index])
            for index in range(self.hue_values.size)
        ])
        L_column = np.full_like(self.hue_values, L, dtype=np.float64)
        return np.stack((L_column, C, self.hue_values), axis=-1)

    def projected_chroma(self) -> np.ndarray:
        """Return the maximum chroma over all lightness slices for each hue.

        This is the radial boundary of the projected ``a*b*`` plane gamut:
        for every stored hue direction, all L* slices are projected onto the
        chroma axis and the largest reachable C* is retained.
        """
        return np.max(self.C_max, axis=0)

    def projected_lightness(self) -> np.ndarray:
        """Return the L* slice that provides the projected maximum chroma."""
        indices = np.argmax(self.C_max, axis=0)
        return self.L_values[indices]

    def projected_LCHab(self) -> np.ndarray:
        """Return projected plane-gamut boundary as ``(L, C, h)`` rows."""
        return np.stack(
            (
                self.projected_lightness(),
                self.projected_chroma(),
                self.hue_values,
            ),
            axis=-1,
        )

    def projected_ab(self) -> np.ndarray:
        """Return projected plane-gamut boundary as ``(a*, b*)`` rows."""
        return LCHab_to_Lab(self.projected_LCHab())[:, 1:3]

    def projected_area(self) -> float:
        """Return the projected plane-gamut area in Lab ``a*b*`` coordinates."""
        return _polygon_area(self.projected_ab())

    def area_at_L(self, L: float) -> float:
        """Return the Lab a*b* polygon area of a lightness slice."""
        lab = LCHab_to_Lab(self.slice_L(L))
        return _polygon_area(lab[:, 1:3])

    def areas(self) -> np.ndarray:
        """Return Lab a*b* polygon areas for all stored lightness slices."""
        lab = self.to_Lab()
        return np.array([
            _polygon_area(lab[index, :, 1:3])
            for index in range(self.L_values.size)
        ])

    def volume(self) -> float:
        """Return an approximate Lab gamut volume by integrating slice areas."""
        if self.L_values.size == 1:
            return 0.0
        return float(np.trapz(self.areas(), self.L_values))

    def gamut_rings(
        self,
        L_steps: Sequence[float] | np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return cumulative gamut rings in a*b* coordinates.

        The rings follow the same practical idea as the legacy implementation:
        per-L/h chroma values are accumulated as root-sum-square contributions
        along the lightness axis, then projected into a 2D a*b* ring.
        """
        if L_steps is None:
            L_steps = self.L_values
        steps = _as_1d_values(L_steps, name="L_steps")
        if np.any(steps < self.L_values[0]) or np.any(steps > self.L_values[-1]):
            raise ValueError("L_steps must be within the boundary L_values range")

        cumulative = np.sqrt(np.cumsum(self.C_max**2, axis=0))
        ring_C = np.vstack([
            np.array([
                np.interp(step, self.L_values, cumulative[:, hue_index])
                for hue_index in range(self.hue_values.size)
            ])
            for step in steps
        ])
        hue_rad = np.radians(self.hue_values)
        rings = np.stack(
            (ring_C * np.cos(hue_rad), ring_C * np.sin(hue_rad)),
            axis=-1,
        )
        return rings, steps

    def ring_area(self, L: float | None = None) -> float:
        """Return the cumulative gamut-ring area at lightness *L*."""
        if L is None:
            L = float(self.L_values[-1])
        rings, _ = self.gamut_rings([L])
        return _polygon_area(rings[0])

    def ring_areas(
        self,
        L_steps: Sequence[float] | np.ndarray | None = None,
    ) -> dict[float, float]:
        """Return cumulative gamut-ring areas keyed by lightness."""
        rings, steps = self.gamut_rings(L_steps)
        return {
            float(step): _polygon_area(ring)
            for step, ring in zip(steps, rings)
        }


def compute_LCH_gamut_boundary(
    primaries: DisplayPrimaries | Sequence[Sequence[float]] | np.ndarray | str,
    *,
    whitepoint_XYZ: Sequence[float] | np.ndarray | None = None,
    L_values: Sequence[float] | np.ndarray = np.arange(0.0, 101.0, 1.0),
    hue_values: Sequence[float] | np.ndarray = np.arange(0.0, 361.0, 1.0),
    C_upper: float = 300.0,
    iterations: int = 14,
    method: str = "auto",
) -> GamutBoundary:
    """Compute maximum displayable CIE LCHab chroma for each L/h direction."""
    display = as_display_primaries(primaries)
    whitepoint = (
        display.whitepoint_XYZ
        if whitepoint_XYZ is None
        else np.asarray(whitepoint_XYZ, dtype=np.float64)
    )
    if whitepoint.shape != (3,) or not np.all(np.isfinite(whitepoint)):
        raise ValueError("whitepoint_XYZ must be a finite triplet")
    if np.any(whitepoint <= 0):
        raise ValueError("whitepoint_XYZ values must be positive")

    L_array = _as_1d_values(L_values, name="L_values")
    hue_array = _as_1d_values(hue_values, name="hue_values")
    C_upper = float(C_upper)
    if not np.isfinite(C_upper) or C_upper <= 0:
        raise ValueError("C_upper must be a finite positive value")
    if int(iterations) != iterations or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    iterations = int(iterations)

    L_grid, hue_grid = np.meshgrid(L_array, hue_array, indexing="ij")
    low = np.zeros_like(L_grid, dtype=np.float64)
    high = np.full_like(L_grid, C_upper, dtype=np.float64)

    for _ in range(iterations):
        mid = (low + high) / 2.0
        LCHab = np.stack((L_grid, mid, hue_grid), axis=-1)
        XYZ = Lab_to_XYZ(LCHab_to_Lab(LCHab), whitepoint_XYZ=whitepoint)
        inside = is_within_primary_gamut(XYZ, display, method=method)
        low = np.where(inside, mid, low)
        high = np.where(inside, high, mid)

    return GamutBoundary(
        C_max=low,
        L_values=L_array,
        hue_values=hue_array,
        whitepoint_XYZ=whitepoint,
        primaries=display,
    )


__all__ = ["GamutBoundary", "compute_LCH_gamut_boundary"]
